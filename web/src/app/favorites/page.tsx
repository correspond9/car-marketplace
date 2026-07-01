"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { ListingCard } from "@/components/ListingCard";
import { api, ApiError, type Listing } from "@/lib/api";

export default function FavoritesPage() {
  const { isLoggedIn, loading: authLoading } = useAuth();
  const router = useRouter();
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !isLoggedIn) router.replace("/login?redirect=/favorites");
  }, [authLoading, isLoggedIn, router]);

  useEffect(() => {
    if (!isLoggedIn) return;
    api.favorites
      .list({ limit: 50 })
      .then((favs) => {
        const items = favs.map((f) => f.listing).filter(Boolean) as Listing[];
        if (items.length === favs.length) {
          setListings(items);
          return;
        }
        return Promise.all(favs.map((f) => api.listings.get(f.listing_id))).then(setListings);
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load favorites"))
      .finally(() => setLoading(false));
  }, [isLoggedIn]);

  if (authLoading || loading) {
    return <main className="px-4 py-12 text-center text-slate-600">Loading favorites…</main>;
  }

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900">Saved cars</h1>
      <p className="mt-1 text-sm text-slate-600">Cars you have bookmarked for later.</p>

      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

      {listings.length === 0 ? (
        <p className="mt-8 rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
          No saved cars yet.{" "}
          <Link href="/search" className="text-emerald-700 hover:underline">
            Browse listings
          </Link>
        </p>
      ) : (
        <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {listings.map((listing) => (
            <ListingCard key={listing.id} listing={listing} />
          ))}
        </div>
      )}
    </main>
  );
}
