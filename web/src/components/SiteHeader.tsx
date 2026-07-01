import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
        <Link href="/" className="text-xl font-bold text-emerald-700">
          CarMarket
        </Link>
        <nav className="flex gap-4 text-sm font-medium text-slate-700">
          <Link href="/search" className="hover:text-emerald-700">
            Browse cars
          </Link>
          <Link href="/search?seller_type=dealer" className="hover:text-emerald-700">
            Dealers
          </Link>
        </nav>
      </div>
    </header>
  );
}

export function ListingCard({ listing }: { listing: import("@/lib/api").Listing }) {
  const cover = listing.images.find((i) => i.is_cover) ?? listing.images[0];
  return (
    <Link
      href={`/listing/${listing.id}`}
      className="block overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md"
    >
      <div className="aspect-[16/10] bg-slate-100 flex items-center justify-center text-slate-400 text-sm">
        {cover ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={cover.url} alt={`${listing.make} ${listing.model}`} className="h-full w-full object-cover" />
        ) : (
          "No photo"
        )}
      </div>
      <div className="p-4">
        <h3 className="font-semibold text-slate-900">
          {listing.make} {listing.model}
          {listing.variant ? ` ${listing.variant}` : ""}
        </h3>
        <p className="mt-1 text-sm text-slate-600">
          {listing.manufacturing_year} · {listing.odometer_km.toLocaleString("en-IN")} km · {listing.city}
        </p>
        <p className="mt-2 text-lg font-bold text-emerald-700">
          {new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(
            listing.asking_price,
          )}
        </p>
      </div>
    </Link>
  );
}
