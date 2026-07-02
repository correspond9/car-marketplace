import Link from "next/link";
import type { Listing } from "@/lib/api";
import { formatPrice } from "@/lib/api";
import { getListingFallbackImage, buildListingImageSlots, resolveListingImageSrc } from "@/lib/listingImages";

export function ListingCard({
  listing,
  imageSlot = 0,
}: {
  listing: Listing;
  imageSlot?: number;
}) {
  const cover = listing.images.find((i) => i.is_cover) ?? listing.images[0];
  const fallback = getListingFallbackImage(listing.make, listing.model, imageSlot);
  const imageSrc = resolveListingImageSrc(cover?.thumbnail_url ?? cover?.url, fallback);
  return (
    <Link
      href={`/listing/${listing.id}`}
      className="matte-glass group block overflow-hidden transition duration-200 hover:-translate-y-0.5 hover:shadow-[0_8px_32px_-10px_rgba(15,23,42,0.12)] active:scale-[0.99]"
    >
      <div className="flex aspect-[16/10] items-center justify-center bg-slate-100/80 text-sm text-slate-400">
        {imageSrc ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={imageSrc}
            alt={`${listing.make} ${listing.model}`}
            className="h-full w-full object-cover transition duration-300 group-hover:scale-[1.02]"
          />
        ) : (
          "No photo"
        )}
      </div>
      <div className="border-t border-slate-100/80 p-4">
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

export { buildListingImageSlots };
