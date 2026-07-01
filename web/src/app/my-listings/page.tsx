"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { api, ApiError, formatPrice, type Listing } from "@/lib/api";

const STATUS_LABELS: Record<string, string> = {
  draft: "Draft",
  pending_review: "Pending review",
  live: "Live",
  sold: "Sold",
  expired: "Expired",
  removed: "Removed",
};

export default function MyListingsPage() {
  const { isLoggedIn, loading: authLoading } = useAuth();
  const router = useRouter();
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionId, setActionId] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !isLoggedIn) router.replace("/login?redirect=/my-listings");
  }, [authLoading, isLoggedIn, router]);

  useEffect(() => {
    if (!isLoggedIn) return;
    api.listings
      .getMine({ limit: 50 })
      .then((res) => setListings(res.items))
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load listings"))
      .finally(() => setLoading(false));
  }, [isLoggedIn]);

  async function handlePublish(id: string) {
    setActionId(id);
    try {
      const updated = await api.listings.publish(id);
      setListings((prev) => prev.map((l) => (l.id === id ? updated : l)));
    } catch (err) {
      alert(err instanceof ApiError ? err.message : "Publish failed");
    } finally {
      setActionId(null);
    }
  }

  async function handleMarkSold(id: string) {
    if (!confirm("Mark this car as sold?")) return;
    setActionId(id);
    try {
      const updated = await api.listings.markSold(id);
      setListings((prev) => prev.map((l) => (l.id === id ? updated : l)));
    } catch (err) {
      alert(err instanceof ApiError ? err.message : "Could not mark as sold");
    } finally {
      setActionId(null);
    }
  }

  async function handleDelete(id: string) {
    if (!confirm("Remove this listing permanently?")) return;
    setActionId(id);
    try {
      await api.listings.delete(id);
      setListings((prev) => prev.filter((l) => l.id !== id));
    } catch (err) {
      alert(err instanceof ApiError ? err.message : "Delete failed");
    } finally {
      setActionId(null);
    }
  }

  if (authLoading || loading) {
    return <main className="px-4 py-12 text-center text-slate-600">Loading your listings…</main>;
  }

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">My listings</h1>
        <Link
          href="/sell"
          className="rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white hover:bg-emerald-800"
        >
          + New listing
        </Link>
      </div>

      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

      {listings.length === 0 ? (
        <p className="mt-8 rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
          You have no listings yet.{" "}
          <Link href="/sell" className="text-emerald-700 hover:underline">
            Sell your first car
          </Link>
        </p>
      ) : (
        <ul className="mt-6 space-y-4">
          {listings.map((listing) => (
            <li key={listing.id} className="rounded-xl border border-slate-200 bg-white p-4">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="font-semibold text-slate-900">
                    {listing.make} {listing.model} {listing.variant}
                  </p>
                  <p className="text-sm text-slate-600">
                    {formatPrice(listing.asking_price)} · {listing.city}
                  </p>
                  <span className="mt-1 inline-block rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-700">
                    {STATUS_LABELS[listing.status] ?? listing.status}
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  <Link
                    href={`/listing/${listing.id}`}
                    className="rounded-lg border px-3 py-1.5 text-sm hover:border-emerald-600"
                  >
                    View
                  </Link>
                  {listing.status === "draft" && (
                    <button
                      type="button"
                      disabled={actionId === listing.id}
                      onClick={() => handlePublish(listing.id)}
                      className="rounded-lg bg-emerald-700 px-3 py-1.5 text-sm text-white hover:bg-emerald-800 disabled:opacity-60"
                    >
                      Publish
                    </button>
                  )}
                  {listing.status === "live" && (
                    <button
                      type="button"
                      disabled={actionId === listing.id}
                      onClick={() => handleMarkSold(listing.id)}
                      className="rounded-lg border px-3 py-1.5 text-sm hover:border-emerald-600"
                    >
                      Mark sold
                    </button>
                  )}
                  <button
                    type="button"
                    disabled={actionId === listing.id}
                    onClick={() => handleDelete(listing.id)}
                    className="rounded-lg border border-red-200 px-3 py-1.5 text-sm text-red-700 hover:bg-red-50"
                  >
                    Remove
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
