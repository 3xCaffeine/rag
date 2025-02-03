"use client";
import { useState, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Send, Paperclip, Globe, Mic, X } from "lucide-react";
import MessageBubble from "./MessageBubble";
import { useCategory } from "@/context/CategoryContext";

interface Message {
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
}

// Add FilePreview component
const FilePreview = ({ 
  file, 
  onRemove 
}: { 
  file: File; 
  onRemove: () => void;
}) => {
  return (
    <div className="flex items-center gap-2 p-2 bg-muted rounded-md">
      <span className="text-sm text-gray-500 flex-1 truncate">
        {file.name}
      </span>
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="h-5 w-5"
        onClick={onRemove}
      >
        <X className="h-3 w-3" />
      </Button>
    </div>
  );
};

export default function PromptForm() {
  const { category } = useCategory();
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [selectedPdf, setSelectedPdf] = useState<File | null>(null);
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() && !selectedImage && !selectedPdf) return;

    const userMessage: Message = { 
      role: "user", 
      content: selectedImage 
        ? `[Image uploaded] ${prompt}`
        : selectedPdf
        ? `[PDF uploaded] ${prompt}`
        : webSearchEnabled
        ? `[Web Search] ${prompt}`
        : prompt 
    };
    
    // Add loading message
    const loadingMessage: Message = {
      role: "assistant",
      content: ""
    };
    
    setMessages((prev) => [...prev, userMessage, loadingMessage]);
    setPrompt("");
    setIsLoading(true);

    try {
      const apiKey = process.env.NEXT_PUBLIC_API_KEY;
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      if (!apiKey || !apiUrl) {
        throw new Error("API key or URL is not defined");
      }

      const params = new URLSearchParams({
        category: category, // This line is already correct
        prompt: prompt,
      });

      let response;
      if (webSearchEnabled) {
        response = await fetch(
          `${apiUrl}/search?${params}`,
          {
            method: "POST",
            headers: {
              "X-API-Key": apiKey,
              "Accept": "application/json",
            },
          }
        );
      } else if (selectedPdf) {
        const formData = new FormData();
        formData.append('file', selectedPdf);

        response = await fetch(
          `${apiUrl}/pdfs?${params}`, 
          {
            method: "POST",
            headers: {
              "X-API-Key": apiKey,
              "Accept": "application/json",
            },
            body: formData,
          }
        );
      } else if (selectedImage) {
        const formData = new FormData();
        formData.append('file', selectedImage);

        response = await fetch(
          `${apiUrl}/image?${params}`, 
          {
            method: "POST",
            headers: {
              "X-API-Key": apiKey,
              "Accept": "application/json",
            },
            body: formData,
          }
        );
      } else {
        response = await fetch(
          `${apiUrl}/text?${params}`,
          {
            method: "POST",
            headers: {
              "X-API-Key": apiKey,
            },
          }
        );
      }

      const data = await response.json();
      // Replace loading message with streaming response
      setMessages((prev) => {
        const newMessages = [...prev.slice(0, -1)]; // Remove loading message
        newMessages.push({
          role: "assistant",
          content: data.response || "No response received",
          isStreaming: true
        });
        return newMessages;
      });

      // After 5 seconds, mark the message as no longer streaming
      setTimeout(() => {
        setMessages((prev) => {
          return prev.map((msg, idx) => {
            if (idx === prev.length - 1) {
              return { ...msg, isStreaming: false };
            }
            return msg;
          });
        });
      }, 5000);

      setSelectedImage(null);
      setSelectedPdf(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error("API Error:", error); 
      // Replace loading message with error
      setMessages((prev) => {
        const newMessages = [...prev.slice(0, -1)]; // Remove loading message
        newMessages.push({
          role: "assistant",
          content: "Error occurred while fetching data"
        });
        return newMessages;
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.type.match('image/jpe?g')) {
        setSelectedImage(file);
        setSelectedPdf(null);
      } else if (file.type === 'application/pdf') {
        setSelectedPdf(file);
        setSelectedImage(null);
      } else {
        alert('Please select only JPG/JPEG images or PDF files');
        e.target.value = '';
      }
    }
  };

  const handlePaperclipClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemoveFile = () => {
    setSelectedImage(null);
    setSelectedPdf(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      
      // Add recording message immediately
      const recordingMessage: Message = {
        role: "user",
        content: "Recording audio...",
        isStreaming: true
      };
      setMessages(prev => [...prev, recordingMessage]);

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) {
          audioChunks.current.push(e.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/wav' });
        audioChunks.current = [];
        
        // Update the recording message
        setMessages(prev => {
          const newMessages = [...prev];
          newMessages[newMessages.length - 1] = {
            role: "user",
            content: "🎤 Audio message sent",
            isStreaming: false
          };
          return newMessages;
        });

        // Submit audio file
        const formData = new FormData();
        formData.append('file', audioBlob);

        setIsLoading(true);
        try {
          const apiKey = process.env.NEXT_PUBLIC_API_KEY;
          const apiUrl = process.env.NEXT_PUBLIC_API_URL;
          if (!apiKey || !apiUrl) {
            throw new Error("API key or URL is not defined");
          }

          const params = new URLSearchParams({
            category: category, 
          });

          const response = await fetch(
            `${apiUrl}/audio?${params}`,
            {
              method: "POST",
              headers: {
                "X-API-Key": apiKey,
                "Accept": "application/json",
              },
              body: formData,
            }
          );

          const data = await response.json();
          const assistantMessage: Message = {
            role: "assistant",
            content: data.response || "No response received",
          };
          setMessages((prev) => [...prev, assistantMessage]);
        } catch (error) {
          console.error("API Error:", error);
          const errorMessage: Message = {
            role: "assistant",
            content: "Error occurred while processing audio",
          };
          setMessages((prev) => [...prev, errorMessage]);
        } finally {
          setIsLoading(false);
        }
      };

      setMediaRecorder(recorder);
      recorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
      mediaRecorder.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 dark:bg-black bg-white dark:bg-grid-white/[0.2] bg-grid-black/[0.2] relative">
        {/* Radial gradient overlay */}
        <div className="absolute pointer-events-none inset-0 dark:bg-black bg-white [mask-image:radial-gradient(ellipse_at_center,transparent_20%,black)]"></div>
        
        {/* Messages container - make it relative to appear above the gradient */}
        <div className="relative">
          {messages.map((message, index) => (
            <MessageBubble
              key={index}
              role={message.role}
              content={message.content}
              isLoading={isLoading && index === messages.length - 1 && message.role === 'assistant'}
              isStreaming={message.isStreaming}
            />
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t bg-background">
        <div className="flex flex-col space-y-2">
          {(selectedImage || selectedPdf) && (
            <FilePreview 
              file={selectedImage || selectedPdf!} 
              onRemove={handleRemoveFile}
            />
          )}
          {(webSearchEnabled || isRecording) && (
            <div className="flex flex-col gap-1">
              {webSearchEnabled && (
                <div className="text-sm text-blue-500">
                  Web search mode enabled
                </div>
              )}
              {isRecording && (
                <div className="text-sm text-red-500">
                  Recording in progress...
                </div>
              )}
            </div>
          )}
          <div className="flex space-x-2">
            <Input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Type your message..."
              className="flex-1"
            />
            <input
              type="file"
              accept="image/jpeg,image/jpg,application/pdf"
              onChange={handleFileSelect}
              ref={fileInputRef}
              className="hidden"
            />
            <Button 
              type="button" 
              onClick={() => setWebSearchEnabled(!webSearchEnabled)} 
              size="icon"
              variant={webSearchEnabled ? "default" : "ghost"}
            >
              <Globe className="h-4 w-4" />
            </Button>
            <Button 
              type="button" 
              onMouseDown={startRecording}
              onMouseUp={stopRecording}
              onMouseLeave={stopRecording}
              size="icon"
              variant={isRecording ? "default" : "ghost"}
            >
              <Mic className="h-4 w-4" />
            </Button>
            <Button 
              type="button" 
              onClick={handlePaperclipClick} 
              size="icon"
              variant="ghost"
            >
              <Paperclip className="h-4 w-4" />
            </Button>
            <Button type="submit" disabled={isLoading} size="icon">
              <Send className="h-4 w-4" />
            </Button>
          </div>
          {isLoading && (
            <div className="text-sm text-gray-500">
              AI is typing...
            </div>
          )}
        </div>
      </form>
    </div>
  );
}
