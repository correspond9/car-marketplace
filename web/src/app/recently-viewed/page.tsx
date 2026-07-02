"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { api, ApiError, formatPrice, type RecentlyViewedItem } from "@/lib/api";

export default function RecentlyViewedPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [items, setItems] = useState<RecentlyViewedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) router.replace("/login?redirect=/recently-viewed");
  }, [authLoading, user, router]);

  useEffect(() => {
    if (!user) return;
    api.users
      .recentlyViewed()
      .then((res) => setItems(res.items))
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load history"))
      .finally(() => setLoading(false));
  }, [user]);

  if (authLoading || loading) {
    return <main className="px-4 py-12 text-center text-slate-600">Loading recently viewed…</main>;
  }

  if (!user) return null;

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900">Recently viewed</h1>
      <p className="mt-1 text-sm text-slate-600">Cars you opened while logged in.</p>

      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

      {items.length === 0 ? (
        <p className="mt-8 rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
          No recently viewed cars yet.{" "}
          <Link href="/search" className="text-emerald-700 hover:underline">
            Browse listings
          </Link>
        </p>
      ) : (
        <ul className="mt-6 grid gap-4 sm:grid-cols-2">
          {items.map((item) =>
            item.listing ? (
              <li key={item.listing_id} className="rounded-xl border border-slate-200 bg-white p-4">
                <Link href={`/listing/${item.listing.id}`} className="block hover:text-emerald-700">
                  <p className="font-semibold text-slate-900">
                    {item.listing.make} {item.listing.model} {item.listing.manufacturing_year}
                  </p>
                  <p className="text-sm text-emerald-700">{formatPrice(item.listing.asking_price)}</p>
                  <p className="text-sm text-slate-600">{item.listing.city}</p>
                </Link>
              </li>
            ) : null,
          )}
        </ul>
      )}
    </main>
  );
}
