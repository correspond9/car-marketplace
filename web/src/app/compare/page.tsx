"use client";

import { Suspense, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { api, ApiError, formatPrice, type Listing } from "@/lib/api";
import {
  getCompareIds,
  MAX_COMPARE,
  removeFromCompare,
  setCompareIds,
} from "@/lib/compare";

function CompareContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [listings, setListings] = useState<Listing[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fromQuery = searchParams.get("ids");
    let ids: string[] = [];
    if (fromQuery) {
      ids = fromQuery.split(",").filter(Boolean).slice(0, MAX_COMPARE);
      setCompareIds(ids);
    } else {
      ids = getCompareIds();
    }

    if (ids.length === 0) {
      setLoading(false);
      return;
    }

    Promise.all(ids.map((id) => api.listings.get(id).catch(() => null)))
      .then((results) => setListings(results.filter(Boolean) as Listing[]))
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load cars"))
      .finally(() => setLoading(false));
  }, [searchParams]);

  function handleRemove(id: string) {
    const next = removeFromCompare(id);
    setListings((prev) => prev.filter((l) => l.id !== id));
    router.replace(next.length ? `/compare?ids=${next.join(",")}` : "/compare");
  }

  if (loading) {
    return <p className="text-center text-slate-600">Loading comparison…</p>;
  }

  if (listings.length === 0) {
    return (
      <div className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
        <p>No cars selected for comparison.</p>
        <Link href="/search" className="mt-4 inline-block text-emerald-700 hover:underline">
          Browse cars to compare
        </Link>
        <p className="mt-2 text-xs text-slate-500">You can compare up to {MAX_COMPARE} cars at once.</p>
      </div>
    );
  }

  const rows: { label: string; key: (l: Listing) => string }[] = [
    { label: "Price", key: (l) => formatPrice(l.asking_price) },
    { label: "Year", key: (l) => String(l.manufacturing_year) },
    { label: "Km driven", key: (l) => `${l.odometer_km.toLocaleString("en-IN")} km` },
    { label: "Fuel", key: (l) => l.fuel_type },
    { label: "Transmission", key: (l) => l.transmission },
    { label: "Body", key: (l) => l.body_type },
    { label: "Owners", key: (l) => String(l.num_owners) },
    { label: "City", key: (l) => l.city },
    { label: "Negotiable", key: (l) => (l.negotiable ? "Yes" : "No") },
  ];

  return (
    <>
      {error && <p className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200 bg-slate-50">
              <th className="px-4 py-3 text-left font-medium text-slate-600">Spec</th>
              {listings.map((l) => (
                <th key={l.id} className="min-w-[180px] px-4 py-3 text-left">
                  <Link href={`/listing/${l.id}`} className="font-semibold text-emerald-700 hover:underline">
                    {l.make} {l.model}
                  </Link>
                  <button
                    type="button"
                    onClick={() => handleRemove(l.id)}
                    className="ml-2 text-xs text-slate-400 hover:text-red-600"
                  >
                    Remove
                  </button>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.label} className="border-b border-slate-100">
                <td className="px-4 py-3 font-medium text-slate-700">{row.label}</td>
                {listings.map((l) => (
                  <td key={l.id} className="px-4 py-3 text-slate-900">
                    {row.key(l)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export default function ComparePage() {
  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900">Compare cars</h1>
      <p className="mt-1 text-sm text-slate-600">Side-by-side comparison of up to {MAX_COMPARE} selected cars.</p>
      <div className="mt-6">
        <Suspense fallback={<p className="text-center text-slate-600">Loading…</p>}>
          <CompareContent />
        </Suspense>
      </div>
    </main>
  );
}
