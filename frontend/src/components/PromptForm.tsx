"use client";
import { useState, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Send, Paperclip } from "lucide-react";
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
    if (!prompt.trim() && !selectedImage) return;

    const userMessage: Message = { 
      role: "user", 
      content: selectedImage 
        ? `[Image uploaded] ${prompt}` 
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
      if (selectedImage) {
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

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedImage(e.target.files[0]);
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
              accept="image/*"
              onChange={handleImageSelect}
              ref={fileInputRef}
              className="hidden"
            />
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
          {selectedImage && (
            <div className="text-sm text-gray-500">
              Selected image: {selectedImage.name}
            </div>
          )}
        </div>
      </form>
    </div>
  );
}
