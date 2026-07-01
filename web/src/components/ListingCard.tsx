import Link from "next/link";
import type { Listing } from "@/lib/api";
import { formatPrice } from "@/lib/api";

export function ListingCard({ listing }: { listing: Listing }) {
  const cover = listing.images.find((i) => i.is_cover) ?? listing.images[0];
  return (
    <Link
      href={`/listing/${listing.id}`}
      className="block overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm transition hover:shadow-md"
    >
      <div className="flex aspect-[16/10] items-center justify-center bg-slate-100 text-sm text-slate-400">
        {cover ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={cover.thumbnail_url ?? cover.url}
            alt={`${listing.make} ${listing.model}`}
            className="h-full w-full object-cover"
          />
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
        <p className="mt-2 text-lg font-bold text-emerald-700">{formatPrice(listing.asking_price)}</p>
      </div>
    </Link>
  );
}
