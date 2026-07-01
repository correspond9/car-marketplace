import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { SiteHeader } from "@/components/SiteHeader";
import { formatPrice, getListing } from "@/lib/api";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  try {
    const listing = await getListing(id);
    return {
      title: `${listing.make} ${listing.model} ${listing.manufacturing_year} — CarMarket`,
      description: `Used ${listing.make} ${listing.model} in ${listing.city}. ${formatPrice(listing.asking_price)}.`,
    };
  } catch {
    return { title: "Listing — CarMarket" };
  }
}

export default async function ListingDetailPage({ params }: Props) {
  const { id } = await params;
  let listing: Awaited<ReturnType<typeof getListing>>;
  try {
    listing = await getListing(id);
  } catch {
    notFound();
  }

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Car",
    name: `${listing.make} ${listing.model}`,
    modelDate: listing.manufacturing_year,
    mileageFromOdometer: {
      "@type": "QuantitativeValue",
      value: listing.odometer_km,
      unitCode: "KMT",
    },
    offers: {
      "@type": "Offer",
      price: listing.asking_price,
      priceCurrency: "INR",
    },
  };

  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <Link href="/search" className="text-sm text-emerald-700 hover:underline">
          ← Back to search
        </Link>
        <div className="mt-6 grid gap-8 lg:grid-cols-2">
          <div className="rounded-xl bg-slate-200 aspect-[4/3] flex items-center justify-center text-slate-500">
            {listing.images[0] ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={listing.images[0].url} alt="" className="h-full w-full rounded-xl object-cover" />
            ) : (
              "Photos coming soon"
            )}
          </div>
          <div>
            <h1 className="text-3xl font-bold text-slate-900">
              {listing.make} {listing.model}
              {listing.variant ? ` ${listing.variant}` : ""}
            </h1>
            <p className="mt-2 text-3xl font-bold text-emerald-700">{formatPrice(listing.asking_price)}</p>
            <ul className="mt-6 space-y-2 text-slate-700">
              <li>Year: {listing.manufacturing_year}</li>
              <li>Odometer: {listing.odometer_km.toLocaleString("en-IN")} km</li>
              <li>Fuel: {listing.fuel_type}</li>
              <li>Transmission: {listing.transmission}</li>
              <li>Body: {listing.body_type}</li>
              <li>Location: {listing.city}{listing.locality ? `, ${listing.locality}` : ""}</li>
              {listing.registration_number_masked && (
                <li>Reg: {listing.registration_number_masked}</li>
              )}
            </ul>
            <button
              type="button"
              className="mt-8 w-full rounded-lg bg-emerald-700 py-3 font-semibold text-white hover:bg-emerald-800 sm:w-auto sm:px-8"
            >
              Contact seller
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
