import Link from "next/link";
import { ListingCard, buildListingImageSlots } from "@/components/ListingCard";
import { searchListings } from "@/lib/api-server";

export default async function HomePage() {
  let listings: Awaited<ReturnType<typeof searchListings>>["items"] = [];
  try {
    const data = await searchListings({ sort: "newest", limit: 8 });
    listings = data.items;
  } catch {
    listings = [];
  }
  const imageSlots = buildListingImageSlots(listings);

  return (
    <main>
      <section className="relative px-4 py-12 sm:py-16">
        <div className="mx-auto max-w-6xl animate-fade-up">
          <div className="matte-glass-hero p-8 sm:p-12">
            <h1 className="text-4xl font-bold tracking-tight text-slate-900 sm:text-5xl">
              Find your next used car in India
            </h1>
            <p className="mt-4 max-w-2xl text-lg text-slate-600">
              Browse listings from individuals and verified dealers. Compare prices, km, and location — all in one place.
            </p>
            <div className="mt-8 flex flex-wrap gap-4">
              <Link href="/search" className="btn-matte-primary">
                Search cars
              </Link>
              <Link href="/sell" className="btn-matte-secondary">
                Sell your car
              </Link>
            </div>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 pb-12">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-slate-900">Latest listings</h2>
          <Link href="/search" className="text-sm font-medium text-emerald-700 hover:underline">
            View all
          </Link>
        </div>
        {listings.length === 0 ? (
          <p className="matte-glass p-8 text-center text-slate-600">
            No live listings yet. Start the API and publish listings to see them here.
          </p>
        ) : (
          <div className="stagger-children grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {listings.map((listing) => (
              <ListingCard key={listing.id} listing={listing} imageSlot={imageSlots.get(listing.id) ?? 0} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
