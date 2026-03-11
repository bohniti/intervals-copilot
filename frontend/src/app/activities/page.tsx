"use client";

import { useEffect, useState } from "react";
import { api, Activity, ActivityType, ACTIVITY_TYPE_LABELS, ACTIVITY_TYPE_COLORS } from "@/lib/api";
import Link from "next/link";

export default function ActivitiesPage() {
  const [activities, setActivities] = useState<Activity[]>([]);
  const [regions, setRegions] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterType, setFilterType] = useState<ActivityType | "">("");
  const [filterRegion, setFilterRegion] = useState<string>("");

  // Load available regions once
  useEffect(() => {
    api.activities.regions().then(setRegions).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    const params: Record<string, string | number> = { limit: 200 };
    if (filterType) params.activity_type = filterType;
    if (filterRegion) params.region = filterRegion;
    api.activities
      .list(params)
      .then(setActivities)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [filterType, filterRegion]);

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-slate-100">Activities</h1>
        <Link
          href="/chat"
          className="px-4 py-2 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-sm font-medium transition-colors"
        >
          + Log New
        </Link>
      </div>

      {/* Type filter pills */}
      <div className="flex flex-wrap gap-2 mb-3">
        <button
          onClick={() => setFilterType("")}
          className={`text-xs px-3 py-1 rounded-full border transition-colors ${
            filterType === ""
              ? "bg-slate-600 border-slate-500 text-white"
              : "border-slate-700 text-slate-400 hover:text-slate-200"
          }`}
        >
          All types
        </button>
        {(Object.keys(ACTIVITY_TYPE_LABELS) as ActivityType[]).map((t) => (
          <button
            key={t}
            onClick={() => setFilterType(t)}
            className={`text-xs px-3 py-1 rounded-full border transition-colors ${
              filterType === t
                ? "bg-slate-600 border-slate-500 text-white"
                : "border-slate-700 text-slate-400 hover:text-slate-200"
            }`}
          >
            {ACTIVITY_TYPE_LABELS[t]}
          </button>
        ))}
      </div>

      {/* Region filter dropdown — only shown when regions exist */}
      {regions.length > 0 && (
        <div className="flex items-center gap-2 mb-6">
          <span className="text-xs text-slate-500">Region:</span>
          <select
            value={filterRegion}
            onChange={(e) => setFilterRegion(e.target.value)}
            className="text-xs rounded-lg bg-slate-800 border border-slate-700 px-2 py-1 text-slate-300 focus:outline-none focus:ring-1 focus:ring-emerald-600"
          >
            <option value="">All regions</option>
            {regions.map((r) => (
              <option key={r} value={r}>{r}</option>
            ))}
          </select>
          {filterRegion && (
            <button
              onClick={() => setFilterRegion("")}
              className="text-xs text-slate-500 hover:text-slate-300"
            >
              ✕ clear
            </button>
          )}
        </div>
      )}

      {loading ? (
        <div className="text-slate-400 text-sm">Loading activities…</div>
      ) : error ? (
        <div className="text-red-400">
          <p>Could not load activities: {error}</p>
          <p className="text-sm text-slate-500 mt-1">Make sure the backend is running.</p>
        </div>
      ) : activities.length === 0 ? (
        <div className="text-center py-16 text-slate-500">
          <div className="text-4xl mb-3">⛰</div>
          <p>No activities yet.</p>
          <Link href="/chat" className="text-emerald-400 hover:underline text-sm mt-1 inline-block">
            Log your first one →
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {activities.map((a) => (
            <Link
              key={a.id}
              href={`/activities/${a.id}`}
              className="block p-4 rounded-xl border border-slate-800 bg-slate-900/50 hover:bg-slate-900 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 min-w-0">
                  {/* Type badge + tags */}
                  <div className="flex flex-wrap items-center gap-1.5 mb-1.5">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        ACTIVITY_TYPE_COLORS[a.activity_type as ActivityType] ?? "bg-slate-800 text-slate-400"
                      }`}
                    >
                      {ACTIVITY_TYPE_LABELS[a.activity_type as ActivityType] ?? a.activity_type}
                    </span>
                    {a.tags?.map((tag) => (
                      <span key={tag} className="text-xs px-2 py-0.5 rounded-full bg-slate-800 text-slate-400">
                        {tag.replace("_", " ")}
                      </span>
                    ))}
                  </div>
                  <p className="font-medium text-slate-100 truncate">{a.title}</p>
                  {/* Location: show region > area > location_name */}
                  <div className="flex items-center gap-1.5 mt-0.5">
                    {a.region && (
                      <span className="text-xs text-slate-500">{a.region}</span>
                    )}
                    {a.area && a.area !== a.region && (
                      <>
                        {a.region && <span className="text-xs text-slate-700">›</span>}
                        <span className="text-xs text-slate-500">{a.area}</span>
                      </>
                    )}
                    {!a.region && !a.area && a.location_name && (
                      <span className="text-xs text-slate-500">{a.location_name}</span>
                    )}
                  </div>
                  {/* Stats row */}
                  <div className="flex gap-3 mt-1.5 text-xs text-slate-500">
                    {a.duration_minutes && (
                      <span>
                        {Math.floor(a.duration_minutes / 60)}h {a.duration_minutes % 60}m
                      </span>
                    )}
                    {a.elevation_gain_m && <span>↑ {a.elevation_gain_m.toLocaleString()} m</span>}
                    {a.distance_km && <span>{a.distance_km} km</span>}
                  </div>
                </div>
                <div className="text-xs text-slate-500 whitespace-nowrap mt-0.5">
                  {new Date(a.date).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                  })}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
