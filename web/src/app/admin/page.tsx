"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import { useBrand } from "@/components/BrandProvider";
import {
  api,
  ApiError,
  formatPrice,
  type Listing,
  type PlatformSettingsAdmin,
} from "@/lib/api";

type Tab = "moderation" | "settings";

export default function AdminPage() {
  const { user, loading: authLoading } = useAuth();
  const { brand_name, logo_url } = useBrand();
  const router = useRouter();
  const [tab, setTab] = useState<Tab>("moderation");
  const [queue, setQueue] = useState<Listing[]>([]);
  const [settings, setSettings] = useState<PlatformSettingsAdmin | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionId, setActionId] = useState<string | null>(null);
  const [rejectReason, setRejectReason] = useState<Record<string, string>>({});
  const [savingSettings, setSavingSettings] = useState(false);
  const [logoFile, setLogoFile] = useState<File | null>(null);

  const isModerator = user?.role === "moderator" || user?.role === "admin";
  const isAdmin = user?.role === "admin";

  useEffect(() => {
    if (!authLoading && !user) router.replace("/login?redirect=/admin");
    else if (!authLoading && user && !isModerator) router.replace("/");
  }, [authLoading, user, isModerator, router]);

  useEffect(() => {
    if (!isModerator) return;
    setLoading(true);
    setError(null);
    const tasks: Promise<void>[] = [
      api.moderation
        .listPending({ limit: 50 })
        .then(setQueue)
        .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load queue")),
    ];
    if (isAdmin) {
      tasks.push(
        api.admin
          .getPlatformSettings()
          .then(setSettings)
          .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load settings")),
      );
    }
    Promise.all(tasks).finally(() => setLoading(false));
  }, [isModerator, isAdmin]);

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

  async function handleSaveSettings() {
    if (!settings) return;
    setSavingSettings(true);
    setError(null);
    try {
      let updated = await api.admin.updatePlatformSettings({
        brand_name: settings.brand_name,
        brand_domain: settings.brand_domain,
        moderation_mode: settings.moderation_mode,
        enable_featured_listings: settings.enable_featured_listings,
        enable_dealer_subscriptions: settings.enable_dealer_subscriptions,
        enable_paid_listings: settings.enable_paid_listings,
      });
      if (logoFile) {
        updated = await api.admin.uploadLogo(logoFile);
        setLogoFile(null);
      }
      setSettings(updated);
      alert("Platform settings saved.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not save settings");
    } finally {
      setSavingSettings(false);
    }
  }

  if (authLoading || loading) {
    return <main className="px-4 py-12 text-center text-slate-600">Loading admin…</main>;
  }

  if (!isModerator) return null;

  return (
    <main className="mx-auto max-w-4xl px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900">Admin</h1>
      <div className="mt-4 flex gap-2 border-b border-slate-200">
        <button
          type="button"
          onClick={() => setTab("moderation")}
          className={`px-4 py-2 text-sm font-medium ${tab === "moderation" ? "border-b-2 border-emerald-600 text-emerald-700" : "text-slate-600"}`}
        >
          Moderation queue
        </button>
        {isAdmin && (
          <button
            type="button"
            onClick={() => setTab("settings")}
            className={`px-4 py-2 text-sm font-medium ${tab === "settings" ? "border-b-2 border-emerald-600 text-emerald-700" : "text-slate-600"}`}
          >
            Platform settings
          </button>
        )}
      </div>

      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

      {tab === "moderation" && (
        <>
          <p className="mt-4 text-sm text-slate-600">
            Review listings before they go live (when moderation is set to manual).
          </p>
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
        </>
      )}

      {tab === "settings" && isAdmin && settings && (
        <section className="mt-6 space-y-4 rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="font-semibold text-slate-900">Brand &amp; platform</h2>
          <label className="block text-sm text-slate-700">
            App name
            <input
              type="text"
              value={settings.brand_name}
              onChange={(e) => setSettings({ ...settings, brand_name: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </label>
          <label className="block text-sm text-slate-700">
            Domain
            <input
              type="text"
              value={settings.brand_domain}
              onChange={(e) => setSettings({ ...settings, brand_domain: e.target.value })}
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            />
          </label>
          <div className="text-sm text-slate-700">
            <p>Current logo</p>
            {(settings.logo_url || logo_url) && (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={settings.logo_url ?? logo_url ?? ""} alt={brand_name} className="mt-2 h-12 w-auto" />
            )}
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setLogoFile(e.target.files?.[0] ?? null)}
              className="mt-2 block w-full text-sm"
            />
          </div>
          <label className="block text-sm text-slate-700">
            Listing moderation
            <select
              value={settings.moderation_mode}
              onChange={(e) =>
                setSettings({
                  ...settings,
                  moderation_mode: e.target.value as PlatformSettingsAdmin["moderation_mode"],
                })
              }
              className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
            >
              <option value="manual">Manual approval (default)</option>
              <option value="auto">Auto-publish listings</option>
            </select>
          </label>
          <fieldset className="space-y-2 text-sm text-slate-700">
            <legend className="font-medium">Future paid features (off for now)</legend>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={settings.enable_featured_listings}
                onChange={(e) => setSettings({ ...settings, enable_featured_listings: e.target.checked })}
              />
              Featured listings
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={settings.enable_dealer_subscriptions}
                onChange={(e) => setSettings({ ...settings, enable_dealer_subscriptions: e.target.checked })}
              />
              Dealer subscriptions
            </label>
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={settings.enable_paid_listings}
                onChange={(e) => setSettings({ ...settings, enable_paid_listings: e.target.checked })}
              />
              Paid listing boosts
            </label>
          </fieldset>
          <button
            type="button"
            disabled={savingSettings}
            onClick={handleSaveSettings}
            className="rounded-lg bg-emerald-700 px-6 py-3 font-semibold text-white hover:bg-emerald-800 disabled:opacity-60"
          >
            {savingSettings ? "Saving…" : "Save settings"}
          </button>
        </section>
      )}
    </main>
  );
}
