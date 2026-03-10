"use client";

import { useState, useRef, useEffect } from "react";
import { api, ChatMessage, Activity } from "@/lib/api";
import Link from "next/link";

function ActivityProposal({
  data,
  onSave,
  onReject,
  saving,
}: {
  data: Partial<Activity>;
  onSave: () => void;
  onReject: () => void;
  saving: boolean;
}) {
  const rows: [string, string | number][] = (
    [
      ["Type", data.activity_type?.replace(/_/g, " ")],
      ["Date", data.date ? new Date(data.date).toLocaleDateString() : undefined],
      ["Route", data.route_name],
      ["Grade", data.grade ? `${data.grade}${data.grade_system ? ` (${data.grade_system})` : ""}` : undefined],
      ["Style", data.climb_style],
      ["Pitches", data.pitches],
      ["Height", data.height_m ? `${data.height_m} m` : undefined],
      ["Area", data.area],
      ["Location", data.location_name],
      ["Partner", data.partner],
      ["Duration", data.duration_minutes ? `${Math.floor(data.duration_minutes / 60)}h ${data.duration_minutes % 60}m` : undefined],
      ["Distance", data.distance_km ? `${data.distance_km} km` : undefined],
      ["Elevation gain", data.elevation_gain_m ? `${data.elevation_gain_m} m` : undefined],
      ["Notes", data.notes],
    ] as [string, string | number | undefined | null][]
  ).filter(([, v]) => v != null && v !== "") as [string, string | number][];

  return (
    <div className="rounded-xl border border-yellow-700 bg-yellow-950/30 p-4">
      <p className="text-xs font-semibold text-yellow-400 uppercase tracking-wide mb-3">
        Proposed activity — please review
      </p>
      <div className="space-y-1.5 mb-4">
        {rows.map(([label, value]) => (
          <div key={label} className="flex gap-2 text-sm">
            <span className="text-slate-500 w-32 shrink-0">{label}</span>
            <span className="text-slate-200 capitalize">{String(value)}</span>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <button
          onClick={onSave}
          disabled={saving}
          className="px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 disabled:opacity-50 text-sm font-medium transition-colors"
        >
          {saving ? "Saving…" : "✓ Save"}
        </button>
        <button
          onClick={onReject}
          disabled={saving}
          className="px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-50 text-sm transition-colors"
        >
          ✗ Something&apos;s wrong
        </button>
      </div>
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content: "Hi! Tell me about your latest climb, hike, or adventure and I'll log it for you.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [pendingActivity, setPendingActivity] = useState<Partial<Activity> | null>(null);
  const [savedActivity, setSavedActivity] = useState<Activity | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, pendingActivity]);

  const send = async () => {
    const content = input.trim();
    if (!content || loading) return;

    const userMsg: ChatMessage = { role: "user", content };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setInput("");
    setLoading(true);
    setPendingActivity(null);

    try {
      const toSend = newMessages.filter((_, i) => i > 0);
      const res = await api.chat(toSend);
      if (res.reply) {
        setMessages((prev) => [...prev, { role: "assistant", content: res.reply }]);
      }
      if (res.pending_activity && res.needs_confirmation) {
        setPendingActivity(res.pending_activity);
      }
    } catch (e: unknown) {
      const errorMsg = e instanceof Error ? e.message : "Unknown error";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Error: ${errorMsg}. Make sure the backend is running.` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!pendingActivity) return;
    setSaving(true);
    try {
      const saved = await api.activities.create(pendingActivity);
      setSavedActivity(saved);
      setPendingActivity(null);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `✓ Saved! Activity logged as "${saved.title}".` },
      ]);
    } catch (e: unknown) {
      const errorMsg = e instanceof Error ? e.message : "Unknown error";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `Failed to save: ${errorMsg}` },
      ]);
    } finally {
      setSaving(false);
    }
  };

  const handleReject = () => {
    setPendingActivity(null);
    setMessages((prev) => [
      ...prev,
      { role: "user", content: "That's not quite right — let me correct it." },
    ]);
  };

  return (
    <div className="max-w-2xl mx-auto flex flex-col h-[calc(100vh-12rem)]">
      <h1 className="text-2xl font-bold text-slate-100 mb-4">Log Activity</h1>

      {savedActivity && (
        <div className="mb-4 p-4 rounded-xl border border-emerald-700 bg-emerald-950/40">
          <p className="text-emerald-300 font-medium mb-1">✓ Activity saved!</p>
          <p className="text-sm text-slate-300">{savedActivity.title}</p>
          <Link
            href={`/activities/${savedActivity.id}`}
            className="text-xs text-emerald-400 hover:underline mt-1 inline-block"
          >
            View activity →
          </Link>
        </div>
      )}

      <div className="flex-1 overflow-y-auto space-y-3 mb-4 pr-1">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm ${
                m.role === "user"
                  ? "bg-emerald-700 text-white rounded-br-sm"
                  : "bg-slate-800 text-slate-100 rounded-bl-sm"
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}

        {pendingActivity && (
          <div className="flex justify-start">
            <div className="w-full max-w-[90%]">
              <ActivityProposal
                data={pendingActivity}
                onSave={handleSave}
                onReject={handleReject}
                saving={saving}
              />
            </div>
          </div>
        )}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-800 text-slate-400 rounded-2xl rounded-bl-sm px-4 py-2.5 text-sm">
              Thinking…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2">
        <input
          className="flex-1 rounded-xl bg-slate-800 border border-slate-700 px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-emerald-600"
          placeholder="Describe your activity…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
          disabled={loading || saving}
        />
        <button
          onClick={send}
          disabled={loading || saving || !input.trim()}
          className="px-4 py-2.5 rounded-xl bg-emerald-700 hover:bg-emerald-600 disabled:opacity-40 disabled:cursor-not-allowed text-sm font-medium transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
}
