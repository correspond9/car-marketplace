"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { api, ApiError, formatPrice, type Listing } from "@/lib/api";

export default function AdminPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [queue, setQueue] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionId, setActionId] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState<Record<string, string>>({});

  const isModerator = user?.role === "moderator" || user?.role === "admin";

  useEffect(() => {
    if (!authLoading && !user) router.replace("/login?redirect=/admin");
    else if (!authLoading && user && !isModerator) router.replace("/");
  }, [authLoading, user, isModerator, router]);

  useEffect(() => {
    if (!isModerator) return;
    api.moderation
      .listPending({ limit: 50 })
      .then(setQueue)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load queue"))
      .finally(() => setLoading(false));
  }, [isModerator]);

  async function handleApprove(id: string) {
    setActionId(id);
    try {
      await api.moderation.approve(id);
      setQueue((prev) => prev.filter((l) => l.id !== id));
    } catch (err) {
      alert(err instanceof ApiError ? err.message : "Approve failed");
    } finally {
      setActionId(null);
    }
  }

  async function handleReject(id: string) {
    const reason = rejectReason[id]?.trim();
    if (!reason || reason.length < 3) {
      alert("Please enter a rejection reason (min 3 characters).");
      return;
    }
    setActionId(id);
    try {
      await api.moderation.reject(id, reason);
      setQueue((prev) => prev.filter((l) => l.id !== id));
    } catch (err) {
      alert(err instanceof ApiError ? err.message : "Reject failed");
    } finally {
      setActionId(null);
    }
  }

  if (authLoading || loading) {
    return <main className="px-4 py-12 text-center text-slate-600">Loading moderation queue…</main>;
  }

  if (!isModerator) return null;

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900">Moderation queue</h1>
      <p className="mt-1 text-sm text-slate-600">Review and approve listings before they go live.</p>

      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

      {queue.length === 0 ? (
        <p className="mt-8 rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
          No listings pending review.
        </p>
      ) : (
        <ul className="mt-6 space-y-6">
          {queue.map((listing) => (
            <li key={listing.id} className="rounded-xl border border-slate-200 bg-white p-5">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-slate-900">
                    {listing.make} {listing.model} {listing.variant}
                  </p>
                  <p className="text-sm text-slate-600">
                    {formatPrice(listing.asking_price)} · {listing.city} · {listing.manufacturing_year}
                  </p>
                  <Link href={`/listing/${listing.id}`} className="mt-1 text-sm text-emerald-700 hover:underline">
                    View listing
                  </Link>
                </div>
                <div className="flex flex-col gap-2 sm:min-w-[240px]">
                  <button
                    type="button"
                    disabled={actionId === listing.id}
                    onClick={() => handleApprove(listing.id)}
                    className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-60"
                  >
                    Approve
                  </button>
                  <input
                    type="text"
                    placeholder="Rejection reason"
                    value={rejectReason[listing.id] ?? ""}
                    onChange={(e) =>
                      setRejectReason((prev) => ({ ...prev, [listing.id]: e.target.value }))
                    }
                    className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
                  />
                  <button
                    type="button"
                    disabled={actionId === listing.id}
                    onClick={() => handleReject(listing.id)}
                    className="rounded-lg border border-red-300 px-4 py-2 text-sm text-red-700 hover:bg-red-50 disabled:opacity-60"
                  >
                    Reject
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
