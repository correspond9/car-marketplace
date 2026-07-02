"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { api, ApiError, type Inquiry } from "@/lib/api";

type Tab = "inbox" | "sent";

export default function InquiriesPage() {
  const { user, loading: authLoading } = useAuth();
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("inbox");
  const [items, setItems] = useState<Inquiry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionId, setActionId] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !user) router.replace("/login?redirect=/inquiries");
  }, [authLoading, user, router]);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    setError(null);
    const loader = tab === "inbox" ? api.inquiries.listInbox : api.inquiries.listSent;
    loader({ limit: 50 })
      .then((res) => setItems(res.items))
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load messages"))
      .finally(() => setLoading(false));
  }, [user, tab]);

  async function handleAccept(id: string) {
    setActionId(id);
    try {
      const updated = await api.inquiries.accept(id);
      setItems((prev) => prev.map((i) => (i.id === id ? updated : i)));
    } catch (err) {
      alert(err instanceof ApiError ? err.message : "Could not accept inquiry");
    } finally {
      setActionId(null);
    }
  }

  async function handleDecline(id: string) {
    setActionId(id);
    try {
      const updated = await api.inquiries.decline(id);
      setItems((prev) => prev.map((i) => (i.id === id ? updated : i)));
    } catch (err) {
      alert(err instanceof ApiError ? err.message : "Could not decline inquiry");
    } finally {
      setActionId(null);
    }
  }

  if (authLoading || loading) {
    return <main className="px-4 py-12 text-center text-slate-600">Loading messages…</main>;
  }

  if (!user) return null;

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900">Messages</h1>
      <p className="mt-1 text-sm text-slate-600">Inquiries from buyers and sellers you contacted.</p>

      <div className="mt-4 flex gap-2 border-b border-slate-200">
        <button
          type="button"
          onClick={() => setTab("inbox")}
          className={`px-4 py-2 text-sm font-medium ${tab === "inbox" ? "border-b-2 border-emerald-600 text-emerald-700" : "text-slate-600"}`}
        >
          Received
        </button>
        <button
          type="button"
          onClick={() => setTab("sent")}
          className={`px-4 py-2 text-sm font-medium ${tab === "sent" ? "border-b-2 border-emerald-600 text-emerald-700" : "text-slate-600"}`}
        >
          Sent
        </button>
      </div>

      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

      {items.length === 0 ? (
        <p className="mt-8 rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
          No messages in this folder yet.
        </p>
      ) : (
        <ul className="mt-6 space-y-4">
          {items.map((inquiry) => (
            <li key={inquiry.id} className="rounded-xl border border-slate-200 bg-white p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-xs uppercase tracking-wide text-slate-500">{inquiry.status}</p>
                  <p className="mt-1 text-sm text-slate-800">{inquiry.message}</p>
                  <Link
                    href={`/listing/${inquiry.listing_id}`}
                    className="mt-2 inline-block text-sm text-emerald-700 hover:underline"
                  >
                    View listing
                  </Link>
                  {tab === "sent" && inquiry.seller_phone && (
                    <p className="mt-2 text-sm font-medium text-emerald-800">
                      Seller phone:{" "}
                      <a href={`tel:${inquiry.seller_phone}`} className="underline">
                        {inquiry.seller_phone}
                      </a>
                    </p>
                  )}
                  {tab === "inbox" && inquiry.buyer_phone && (
                    <p className="mt-2 text-sm font-medium text-emerald-800">
                      Buyer phone:{" "}
                      <a href={`tel:${inquiry.buyer_phone}`} className="underline">
                        {inquiry.buyer_phone}
                      </a>
                    </p>
                  )}
                </div>
                {tab === "inbox" && inquiry.status === "open" && (
                  <div className="flex gap-2">
                    <button
                      type="button"
                      disabled={actionId === inquiry.id}
                      onClick={() => handleAccept(inquiry.id)}
                      className="rounded-lg bg-emerald-700 px-3 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-60"
                    >
                      Accept
                    </button>
                    <button
                      type="button"
                      disabled={actionId === inquiry.id}
                      onClick={() => handleDecline(inquiry.id)}
                      className="rounded-lg border border-red-300 px-3 py-2 text-sm text-red-700 hover:bg-red-50 disabled:opacity-60"
                    >
                      Decline
                    </button>
                  </div>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
