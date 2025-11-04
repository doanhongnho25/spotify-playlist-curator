import { FormEvent, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { Send, Sparkles } from "lucide-react";
import { Card } from "@/components/ui/Card";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { apiFetch } from "@/hooks/useApi";
import { API_ROUTES } from "@/utils/apiRoutes";
import { useToast } from "@/context/ToastContext";

interface AssistantMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface ChatResponse {
  reply: string;
}

export const AssistantPage = () => {
  const { addToast } = useToast();
  const [messages, setMessages] = useState<AssistantMessage[]>([]);
  const [input, setInput] = useState("");

  const chatMutation = useMutation({
    mutationFn: (prompt: string) =>
      apiFetch<ChatResponse>(API_ROUTES.assistant.chat, {
        method: "POST",
        json: { prompt }
      }),
    onSuccess: (data, variables) => {
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "user", content: variables },
        { id: crypto.randomUUID(), role: "assistant", content: data.reply }
      ]);
      addToast({ title: "Assistant responded", variant: "success" });
    },
    onError: (error, variables) => {
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: "user", content: variables },
        {
          id: crypto.randomUUID(),
          role: "assistant",
          content:
            error instanceof Error ? error.message : "Unable to contact the assistant."
        }
      ]);
    }
  });

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!input.trim()) return;
    chatMutation.mutate(input.trim());
    setInput("");
  };

  return (
    <div className="space-y-6">
      <Card title="AI Command Center">
        <p className="text-sm text-white/60">
          Ask the Vibe Orchestrator to plan syncs, scaling, or ingest operations. Confirmations will appear when actions are ready.
        </p>
      </Card>
      <Card>
        <div className="flex flex-col gap-4">
          <div className="flex-1 space-y-3 overflow-y-auto rounded-2xl bg-black/20 p-4">
            {messages.length === 0 && (
              <div className="flex flex-col items-center justify-center gap-2 py-12 text-white/50">
                <Sparkles className="h-8 w-8" />
                <p>Start a conversation with the assistant.</p>
              </div>
            )}
            {messages.map((message) => (
              <div
                className={`max-w-2xl rounded-2xl px-4 py-3 text-sm ${
                  message.role === "user"
                    ? "ml-auto bg-accent text-white shadow-glow"
                    : "bg-white/10 text-white"
                }`}
                key={message.id}
              >
                {message.content}
              </div>
            ))}
          </div>
          <form className="flex items-end gap-3" onSubmit={handleSubmit}>
            <Textarea
              onChange={(event) => setInput(event.target.value)}
              placeholder="e.g. Create 50 playlists on account A"
              rows={3}
              value={input}
            />
            <Button
              className="shrink-0"
              disabled={chatMutation.isPending}
              type="submit"
            >
              <Send className="h-4 w-4" />
              Send
            </Button>
          </form>
        </div>
      </Card>
    </div>
  );
};

export default AssistantPage;
