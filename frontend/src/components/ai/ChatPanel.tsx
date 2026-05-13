"use client";

import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { MessageSquare, Send, Trash2 } from "lucide-react";
import { api } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";

interface ChatPanelProps {
  questionId: number | null;
  submissionId: string;
}

export default function ChatPanel({ questionId, submissionId }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Reset chat when question changes
  useEffect(() => {
    setMessages([]);
  }, [questionId]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || sending) return;

    const userMsg: ChatMessage = { role: "user", content: text };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInput("");
    setSending(true);

    try {
      const res = await api.post<{ reply: string }>("/ai/chat", {
        messages: updatedMessages.map((m) => ({
          role: m.role,
          content: m.content,
        })),
        question_id: questionId,
        submission_id: parseInt(submissionId, 10),
      });
      setMessages([
        ...updatedMessages,
        { role: "assistant", content: res.data.reply },
      ]);
    } catch {
      setMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't process your request. Make sure OPENAI_API_KEY is configured.",
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!expanded) {
    return (
      <Card
        className="border-purple-200 bg-purple-50/30 cursor-pointer hover:bg-purple-50/60 transition-colors"
        onClick={() => setExpanded(true)}
      >
        <CardContent className="py-3 flex items-center gap-2">
          <MessageSquare className="h-4 w-4 text-purple-600" />
          <span className="text-sm text-purple-700 font-medium">
            AI Chat Assistant
          </span>
          <span className="text-xs text-purple-400 ml-auto">
            Click to open
          </span>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-purple-200 bg-purple-50/30">
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4 text-purple-600" />
            <CardTitle className="text-sm font-medium text-purple-800">
              AI Chat Assistant
            </CardTitle>
          </div>
          <div className="flex gap-1">
            {messages.length > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setMessages([])}
                title="Clear chat"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setExpanded(false)}
            >
              Minimize
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="h-64 overflow-y-auto rounded-md bg-white border border-purple-100 p-3 space-y-3">
          {messages.length === 0 && (
            <p className="text-xs text-gray-400 text-center mt-8">
              Ask me anything about this question — best practices,
              compliance requirements, or how to answer.
            </p>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`flex ${
                msg.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[85%] rounded-lg px-3 py-2 text-sm ${
                  msg.role === "user"
                    ? "bg-purple-600 text-white"
                    : "bg-gray-100 text-gray-800"
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
            </div>
          ))}
          {sending && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-lg px-3 py-2 text-sm text-gray-500">
                Thinking...
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>
        <div className="flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about this question..."
            rows={2}
            className="resize-none"
            disabled={sending}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            className="self-end bg-purple-600 hover:bg-purple-700"
          >
            <Send className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
