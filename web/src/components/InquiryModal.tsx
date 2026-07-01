"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, ApiError } from "@/lib/api";
import { useAuth } from "@/components/AuthProvider";

type Props = {
  listingId: string;
  listingTitle: string;
  open: boolean;
  onClose: () => void;
};

export function InquiryModal({ listingId, listingTitle, open, onClose }: Props) {
  const { isLoggedIn } = useAuth();
  const router = useRouter();
  const [message, setMessage] = useState(
    "Hi, I am interested in this car. Is it still available? Please share more details.",
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!open) return null;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!isLoggedIn) {
      router.push(`/login?redirect=/listing/${listingId}`);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await api.inquiries.create(listingId, message.trim());
      setSuccess(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not send inquiry. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">
        <div className="flex items-start justify-between gap-4">
          <h2 className="text-lg font-semibold text-slate-900">Contact seller</h2>
          <button type="button" onClick={onClose} className="text-slate-400 hover:text-slate-600">
            ✕
          </button>
        </div>
        <p className="mt-1 text-sm text-slate-600">{listingTitle}</p>

        {success ? (
          <div className="mt-6 rounded-lg bg-emerald-50 p-4 text-sm text-emerald-800">
            Your message was sent. The seller will contact you soon.
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            {!isLoggedIn && (
              <p className="rounded-lg bg-amber-50 p-3 text-sm text-amber-800">
                Please log in to contact the seller.
              </p>
            )}
            <div>
              <label htmlFor="inquiry-message" className="block text-sm font-medium text-slate-700">
                Your message
              </label>
              <textarea
                id="inquiry-message"
                rows={4}
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                required
                minLength={10}
                className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <div className="flex gap-3">
              <button
                type="button"
                onClick={onClose}
                className="flex-1 rounded-lg border border-slate-300 py-2 text-sm font-medium hover:bg-slate-50"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={loading}
                className="flex-1 rounded-lg bg-emerald-700 py-2 text-sm font-semibold text-white hover:bg-emerald-800 disabled:opacity-60"
              >
                {loading ? "Sending…" : isLoggedIn ? "Send message" : "Log in to send"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
