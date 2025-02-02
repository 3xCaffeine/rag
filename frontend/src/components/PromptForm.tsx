"use client";
import { useState, useRef, useEffect } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";
import MessageBubble from "./MessageBubble";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function PromptForm() {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    const userMessage: Message = { role: "user", content: prompt };
    setMessages((prev) => [...prev, userMessage]);
    setPrompt("");
    setIsLoading(true);

    try {
      const params = new URLSearchParams({
        category: "medical",
        prompt: prompt,
      });

      const apiKey = process.env.NEXT_PUBLIC_API_KEY;
      const apiUrl = process.env.NEXT_PUBLIC_API_URL;
      if (!apiKey || !apiUrl) {
        throw new Error("API key or URL is not defined");
      }

      const res = await fetch(
        `${apiUrl}/text?${params}`,
        {
          method: "POST",
          headers: {
            "X-API-Key": apiKey,
          },
        }
      );

      const data = await res.json();
      console.log("API Response:", data); 
      const assistantMessage: Message = {
        role: "assistant",
        content: data.response || "No response received", 
      };
      setMessages((prev) => [...prev, assistantMessage]);
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
        <div className="flex space-x-2">
          <Input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Type your message..."
            className="flex-1"
          />
          <Button type="submit" disabled={isLoading} size="icon">
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </form>
    </div>
  );
}
