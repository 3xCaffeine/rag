"use client";
import { useState, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Send, Paperclip, Globe } from "lucide-react";
import MessageBubble from "./MessageBubble";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function PromptForm() {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [selectedPdf, setSelectedPdf] = useState<File | null>(null);
  const [webSearchEnabled, setWebSearchEnabled] = useState(false);
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
    setMessages((prev) => [...prev, userMessage]);
    setPrompt("");
    setIsLoading(true);

    try {
      const apiKey = process.env.NEXT_PUBLIC_API_KEY;
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      if (!apiKey || !apiUrl) {
        throw new Error("API key or URL is not defined");
      }

      const params = new URLSearchParams({
        category: "medical",
        prompt: prompt,
      });

      let response;
      if (webSearchEnabled) {
        // Handle web search case
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
        // Handle PDF + text case
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
        // Handle image + text case
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
        // Handle text-only case
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
      const assistantMessage: Message = {
        role: "assistant",
        content: data.response || "No response received",
      };
      setMessages((prev) => [...prev, assistantMessage]);
      setSelectedImage(null);
      setSelectedPdf(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      console.error("API Error:", error); 
      const errorMessage: Message = {
        role: "assistant",
        content: "Error occurred while fetching data",
      };
      setMessages((prev) => [...prev, errorMessage]);
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

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)]">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <MessageBubble
            key={index}
            role={message.role}
            content={message.content}
          />
        ))}
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-4 border-t">
        <div className="flex flex-col space-y-2">
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
          {(selectedImage || selectedPdf) && (
            <div className="text-sm text-gray-500">
              Selected file: {selectedImage?.name || selectedPdf?.name}
            </div>
          )}
          {webSearchEnabled && (
            <div className="text-sm text-blue-500">
              Web search mode enabled
            </div>
          )}
        </div>
      </form>
    </div>
  );
}
