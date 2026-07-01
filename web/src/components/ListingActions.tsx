"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { InquiryModal } from "@/components/InquiryModal";
import { useAuth } from "@/components/AuthProvider";
import { api, ApiError } from "@/lib/api";
import { addToCompare, compareQueryString, getCompareIds } from "@/lib/compare";

type Props = {
  listingId: string;
  listingTitle: string;
};

export function ListingActions({ listingId, listingTitle }: Props) {
  const { isLoggedIn } = useAuth();
  const router = useRouter();
  const [inquiryOpen, setInquiryOpen] = useState(false);
  const [favoriteLoading, setFavoriteLoading] = useState(false);
  const [favoriteMsg, setFavoriteMsg] = useState<string | null>(null);
  const [compareMsg, setCompareMsg] = useState<string | null>(null);
  const [compareCount, setCompareCount] = useState(0);

  useEffect(() => {
    setCompareCount(getCompareIds().length);
  }, []);

  async function handleFavorite() {
    if (!isLoggedIn) {
      router.push(`/login?redirect=/listing/${listingId}`);
      return;
    }
    setFavoriteLoading(true);
    setFavoriteMsg(null);
    try {
      await api.favorites.add(listingId);
      setFavoriteMsg("Added to favorites");
    } catch (err) {
      setFavoriteMsg(err instanceof ApiError ? err.message : "Could not add to favorites");
    } finally {
      setFavoriteLoading(false);
    }
  }

  function handleCompare() {
    const ids = addToCompare(listingId);
    setCompareCount(ids.length);
    setCompareMsg(`Added to compare (${ids.length}/4)`);
    router.push(`/compare${compareQueryString(ids)}`);
  }

  return (
    <>
      <div className="mt-8 flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => setInquiryOpen(true)}
          className="rounded-lg bg-emerald-700 px-6 py-3 font-semibold text-white hover:bg-emerald-800"
        >
          Contact seller
        </button>
        <button
          type="button"
          onClick={handleFavorite}
          disabled={favoriteLoading}
          className="rounded-lg border border-slate-300 px-6 py-3 font-medium text-slate-700 hover:border-emerald-600 hover:text-emerald-700 disabled:opacity-60"
        >
          {favoriteLoading ? "Saving…" : "Save to favorites"}
        </button>
        <button
          type="button"
          onClick={handleCompare}
          className="rounded-lg border border-slate-300 px-6 py-3 font-medium text-slate-700 hover:border-emerald-600 hover:text-emerald-700"
        >
          Compare
        </button>
        {compareCount > 0 && (
          <Link
            href={`/compare${compareQueryString(getCompareIds())}`}
            className="rounded-lg px-3 py-3 text-sm font-medium text-emerald-700 hover:underline"
          >
            View compare ({compareCount})
          </Link>
        )}
      </div>
      {favoriteMsg && <p className="mt-2 text-sm text-slate-600">{favoriteMsg}</p>}
      {compareMsg && <p className="mt-1 text-sm text-slate-600">{compareMsg}</p>}
      <InquiryModal
        listingId={listingId}
        listingTitle={listingTitle}
        open={inquiryOpen}
        onClose={() => setInquiryOpen(false)}
      />
    </>
  );
}
