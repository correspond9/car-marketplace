import Link from "next/link";
import { ListingCard } from "@/components/ListingCard";
import { searchListings } from "@/lib/api";

export default async function HomePage() {
  let listings: Awaited<ReturnType<typeof searchListings>>["items"] = [];
  try {
    const data = await searchListings({ sort: "newest", limit: 8 });
    listings = data.items;
  } catch {
    listings = [];
  }

  return (
    <main>
      <section className="bg-emerald-700 px-4 py-16 text-white">
        <div className="mx-auto max-w-6xl">
          <h1 className="text-4xl font-bold tracking-tight sm:text-5xl">
            Find your next used car in India
          </h1>
          <p className="mt-4 max-w-2xl text-lg text-emerald-50">
            Browse listings from individuals and verified dealers. Compare prices, km, and location — all in one place.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link
              href="/search"
              className="inline-block rounded-lg bg-white px-6 py-3 font-semibold text-emerald-800 hover:bg-emerald-50"
            >
              Search cars
            </Link>
            <Link
              href="/sell"
              className="inline-block rounded-lg border border-emerald-200 px-6 py-3 font-semibold text-white hover:bg-emerald-600"
            >
              Sell your car
            </Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-12">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-slate-900">Latest listings</h2>
          <Link href="/search" className="text-sm font-medium text-emerald-700 hover:underline">
            View all
          </Link>
        </div>
        {listings.length === 0 ? (
          <p className="rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
            No live listings yet. Start the API and publish listings to see them here.
          </p>
        ) : (
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {listings.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
