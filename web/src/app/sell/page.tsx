"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/components/AuthProvider";
import {
  api,
  ApiError,
  type BodyType,
  type FuelType,
  type Listing,
  type ListingCreateInput,
  type Transmission,
} from "@/lib/api";

const BODY_TYPES: BodyType[] = ["hatchback", "sedan", "suv", "muv", "coupe", "convertible", "pickup", "van"];
const FUEL_TYPES: FuelType[] = ["petrol", "diesel", "cng", "ev", "hybrid"];
const TRANSMISSIONS: Transmission[] = ["manual", "automatic", "amt", "dct"];

const emptyForm: ListingCreateInput = {
  make: "",
  model: "",
  variant: "",
  manufacturing_year: new Date().getFullYear() - 3,
  body_type: "hatchback",
  fuel_type: "petrol",
  transmission: "manual",
  odometer_km: 50000,
  num_owners: 1,
  asking_price: 500000,
  negotiable: true,
  city: "",
  locality: "",
  accident_history: false,
  flood_history: false,
  service_history_available: false,
  exchange_accepted: false,
  test_drive_available: true,
  show_contact_publicly: false,
};

export default function SellPage() {
  const { isLoggedIn, loading: authLoading, user } = useAuth();
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<ListingCreateInput>(emptyForm);
  const [listing, setListing] = useState<Listing | null>(null);
  const [photos, setPhotos] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  useEffect(() => {
    if (!authLoading && !isLoggedIn) router.replace("/login?redirect=/sell");
  }, [authLoading, isLoggedIn, router]);

  useEffect(() => {
    if (user?.role === "dealer") {
      setForm((prev) => ({ ...prev, show_contact_publicly: true }));
    }
  }, [user?.role]);

  function updateField<K extends keyof ListingCreateInput>(key: K, value: ListingCreateInput[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  async function handleCreateDraft() {
    setSubmitting(true);
    setError(null);
    try {
      const created = await api.listings.create(form);
      setListing(created);
      setStep(3);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not create listing");
    } finally {
      setSubmitting(false);
    }
  }

  async function handleUploadPhotos() {
    if (!listing) return;
    setSubmitting(true);
    setError(null);
    try {
      for (let i = 0; i < photos.length; i++) {
        setUploadProgress(`Uploading photo ${i + 1} of ${photos.length}…`);
        await api.listings.uploadImage(listing.id, photos[i], { is_cover: i === 0, sort_order: i });
      }
      setUploadProgress(null);
      setStep(4);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Photo upload failed");
    } finally {
      setSubmitting(false);
    }
  }

  async function handlePublish() {
    if (!listing) return;
    setSubmitting(true);
    setError(null);
    try {
      await api.listings.publish(listing.id);
      setDone(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not publish listing");
    } finally {
      setSubmitting(false);
    }
  }

  if (authLoading) {
    return <main className="px-4 py-12 text-center text-slate-600">Loading…</main>;
  }

  if (done && listing) {
    return (
      <main className="mx-auto max-w-lg px-4 py-12 text-center">
        <h1 className="text-2xl font-bold text-slate-900">Listing submitted!</h1>
        <p className="mt-3 text-slate-600">
          Your car is pending review. We will notify you once it goes live.
        </p>
        <div className="mt-6 flex justify-center gap-4">
          <Link href={`/listing/${listing.id}`} className="text-emerald-700 hover:underline">
            Preview listing
          </Link>
          <Link href="/my-listings" className="text-emerald-700 hover:underline">
            My listings
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-2xl px-4 py-8">
      <h1 className="text-2xl font-bold text-slate-900">Sell your car</h1>
      <p className="mt-1 text-sm text-slate-600">Step {step} of 4</p>

      <div className="mt-4 flex gap-2">
        {[1, 2, 3, 4].map((s) => (
          <div
            key={s}
            className={`h-1 flex-1 rounded ${s <= step ? "bg-emerald-600" : "bg-slate-200"}`}
          />
        ))}
      </div>

      {error && <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}

      {step === 1 && (
        <section className="mt-6 space-y-4 rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="font-semibold text-slate-900">Vehicle details</h2>
          <div className="grid gap-4 sm:grid-cols-2">
            <Field label="Make" value={form.make} onChange={(v) => updateField("make", v)} required />
            <Field label="Model" value={form.model} onChange={(v) => updateField("model", v)} required />
            <Field label="Variant" value={form.variant ?? ""} onChange={(v) => updateField("variant", v)} />
            <Field
              label="Year"
              type="number"
              value={String(form.manufacturing_year)}
              onChange={(v) => updateField("manufacturing_year", Number(v))}
              required
            />
            <SelectField
              label="Body type"
              value={form.body_type}
              options={BODY_TYPES}
              onChange={(v) => updateField("body_type", v as BodyType)}
            />
            <SelectField
              label="Fuel"
              value={form.fuel_type}
              options={FUEL_TYPES}
              onChange={(v) => updateField("fuel_type", v as FuelType)}
            />
            <SelectField
              label="Transmission"
              value={form.transmission}
              options={TRANSMISSIONS}
              onChange={(v) => updateField("transmission", v as Transmission)}
            />
            <Field
              label="Odometer (km)"
              type="number"
              value={String(form.odometer_km)}
              onChange={(v) => updateField("odometer_km", Number(v))}
              required
            />
            <Field
              label="Number of owners"
              type="number"
              value={String(form.num_owners ?? 1)}
              onChange={(v) => updateField("num_owners", Number(v))}
            />
          </div>
          <button
            type="button"
            onClick={() => setStep(2)}
            disabled={!form.make || !form.model}
            className="mt-4 w-full rounded-lg bg-emerald-700 py-3 font-semibold text-white hover:bg-emerald-800 disabled:opacity-60"
          >
            Continue
          </button>
        </section>
      )}

      {step === 2 && (
        <section className="mt-6 space-y-4 rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="font-semibold text-slate-900">Location &amp; price</h2>
          <Field label="City" value={form.city} onChange={(v) => updateField("city", v)} required />
          <Field label="Locality" value={form.locality ?? ""} onChange={(v) => updateField("locality", v)} />
          <Field
            label="Asking price (₹)"
            type="number"
            value={String(form.asking_price)}
            onChange={(v) => updateField("asking_price", Number(v))}
            required
          />
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={form.negotiable ?? true}
              onChange={(e) => updateField("negotiable", e.target.checked)}
            />
            Price is negotiable
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={form.test_drive_available ?? false}
              onChange={(e) => updateField("test_drive_available", e.target.checked)}
            />
            Test drive available
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-700">
            <input
              type="checkbox"
              checked={form.show_contact_publicly ?? false}
              onChange={(e) => updateField("show_contact_publicly", e.target.checked)}
            />
            Show my phone number on the listing (dealers: on by default)
          </label>
          <div className="flex gap-3">
            <button type="button" onClick={() => setStep(1)} className="flex-1 rounded-lg border py-3">
              Back
            </button>
            <button
              type="button"
              onClick={handleCreateDraft}
              disabled={submitting || !form.city}
              className="flex-1 rounded-lg bg-emerald-700 py-3 font-semibold text-white hover:bg-emerald-800 disabled:opacity-60"
            >
              {submitting ? "Saving…" : "Save draft & add photos"}
            </button>
          </div>
        </section>
      )}

      {step === 3 && listing && (
        <section className="mt-6 space-y-4 rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="font-semibold text-slate-900">Upload photos</h2>
          <p className="text-sm text-slate-600">Add clear photos of the exterior, interior, and odometer.</p>
          <input
            type="file"
            accept="image/*"
            multiple
            onChange={(e) => setPhotos(Array.from(e.target.files ?? []))}
            className="block w-full text-sm"
          />
          {photos.length > 0 && <p className="text-sm text-slate-600">{photos.length} photo(s) selected</p>}
          {uploadProgress && <p className="text-sm text-emerald-700">{uploadProgress}</p>}
          <div className="flex gap-3">
            <button type="button" onClick={() => setStep(4)} className="flex-1 rounded-lg border py-3">
              Skip for now
            </button>
            <button
              type="button"
              onClick={handleUploadPhotos}
              disabled={submitting || photos.length === 0}
              className="flex-1 rounded-lg bg-emerald-700 py-3 font-semibold text-white hover:bg-emerald-800 disabled:opacity-60"
            >
              {submitting ? "Uploading…" : "Upload photos"}
            </button>
          </div>
        </section>
      )}

      {step === 4 && listing && (
        <section className="mt-6 space-y-4 rounded-xl border border-slate-200 bg-white p-6">
          <h2 className="font-semibold text-slate-900">Review &amp; publish</h2>
          <ul className="space-y-1 text-sm text-slate-700">
            <li>
              {form.make} {form.model} {form.variant}
            </li>
            <li>
              {form.manufacturing_year} · {form.odometer_km.toLocaleString("en-IN")} km
            </li>
            <li>
              {form.city} · ₹{form.asking_price.toLocaleString("en-IN")}
            </li>
          </ul>
          <p className="text-sm text-slate-600">
            Publishing sends your listing for moderation review before it appears publicly.
          </p>
          <button
            type="button"
            onClick={handlePublish}
            disabled={submitting}
            className="w-full rounded-lg bg-emerald-700 py-3 font-semibold text-white hover:bg-emerald-800 disabled:opacity-60"
          >
            {submitting ? "Submitting…" : "Submit for review"}
          </button>
        </section>
      )}
    </main>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
  required,
}: {
  label: string;
  value: string;
  onChange: (v: string) => void;
  type?: string;
  required?: boolean;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700">{label}</label>
      <input
        type={type}
        value={value}
        required={required}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
      />
    </div>
  );
}

function SelectField({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: string;
  options: string[];
  onChange: (v: string) => void;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2"
      >
        {options.map((o) => (
          <option key={o} value={o}>
            {o}
          </option>
        ))}
      </select>
    </div>
  );
}
