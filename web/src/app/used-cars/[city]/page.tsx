import type { Metadata } from "next";
import Link from "next/link";
import { ListingCard } from "@/components/ListingCard";
import { searchListings } from "@/lib/api";
import { buildListingImageSlots } from "@/lib/listingImages";

type Props = { params: Promise<{ city: string }> };

function formatCity(slug: string): string {
  return slug
    .split("-")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { city } = await params;
  const name = formatCity(city);
  return {
    title: `Used cars in ${name}`,
    description: `Browse verified used car listings in ${name}. Compare prices, km, and sellers on CarMarket.`,
  };
}

export default async function CityLandingPage({ params }: Props) {
  const { city } = await params;
  const cityName = formatCity(city);

  let listings: Awaited<ReturnType<typeof searchListings>>["items"] = [];
  let total = 0;
  try {
    const data = await searchListings({ city: cityName, sort: "newest", limit: 12 });
    listings = data.items;
    total = data.total;
  } catch {
    listings = [];
  }
  const imageSlots = buildListingImageSlots(listings);

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <nav className="text-sm text-slate-600">
        <Link href="/" className="hover:text-emerald-700">
          Home
        </Link>
        <span className="mx-2">/</span>
        <span>Used cars in {cityName}</span>
      </nav>
      <h1 className="mt-4 text-3xl font-bold text-slate-900">Used cars in {cityName}</h1>
      <p className="mt-2 text-slate-600">
        {total > 0
          ? `${total} used car${total === 1 ? "" : "s"} available in ${cityName}.`
          : `Search used cars for sale in ${cityName}.`}
      </p>

      <Link
        href={`/search?city=${encodeURIComponent(cityName)}`}
        className="mt-4 inline-block text-sm font-medium text-emerald-700 hover:underline"
      >
        View all in {cityName} →
      </Link>

      <div className="mt-8 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {listings.map((listing) => (
          <ListingCard key={listing.id} listing={listing} imageSlot={imageSlots.get(listing.id) ?? 0} />
        ))}
      </div>

      {listings.length === 0 && (
        <p className="mt-8 rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
          No listings in {cityName} right now.{" "}
          <Link href="/search" className="text-emerald-700 hover:underline">
            Browse all India
          </Link>
        </p>
      )}
    </main>
  );
}
