import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ListingActions } from "@/components/ListingActions";
import { TrackListingView } from "@/components/TrackListingView";
import { formatPrice, getListing } from "@/lib/api";
import { getListingFallbackImage, imageSlotFromVariant, resolveListingImageSrc } from "@/lib/listingImages";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { id } = await params;
  try {
    const listing = await getListing(id);
    return {
      title: `${listing.make} ${listing.model} ${listing.manufacturing_year}`,
      description: `Used ${listing.make} ${listing.model} in ${listing.city}. ${formatPrice(listing.asking_price)}.`,
    };
  } catch {
    return { title: "Listing" };
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

  const title = `${listing.make} ${listing.model}${listing.variant ? ` ${listing.variant}` : ""}`;
  const cover = listing.images.find((i) => i.is_cover) ?? listing.images[0];
  const fallback = getListingFallbackImage(
    listing.make,
    listing.model,
    imageSlotFromVariant(listing.make, listing.model, listing.variant),
  );
  const coverSrc = resolveListingImageSrc(cover?.url, fallback);

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
    <main className="mx-auto max-w-6xl px-4 py-8">
      <TrackListingView listingId={listing.id} />
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <Link href="/search" className="text-sm text-emerald-700 hover:underline">
        ← Back to search
      </Link>
      <div className="matte-glass mt-6 grid gap-8 overflow-hidden lg:grid-cols-2">
        <div className="p-2 sm:p-3">
          <div className="flex aspect-[4/3] items-center justify-center overflow-hidden rounded-xl bg-slate-100/80 text-slate-500">
            {coverSrc ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img src={coverSrc} alt={title} className="h-full w-full object-cover" />
            ) : (
              "No photos uploaded"
            )}
          </div>
          {listing.images.length > 1 && (
            <div className="mt-3 grid grid-cols-4 gap-2">
              {listing.images.slice(0, 8).map((img, index) => (
                // eslint-disable-next-line @next/next/no-img-element
                <img
                  key={img.id}
                  src={
                    resolveListingImageSrc(
                      img.thumbnail_url ?? img.url,
                      index === 0 ? fallback : null,
                    ) ?? ""
                  }
                  alt=""
                  className="aspect-square rounded-lg object-cover"
                />
              ))}
            </div>
          )}
        </div>
        <div className="border-t border-slate-100/80 p-6 lg:border-l lg:border-t-0">
          <p className="text-sm uppercase tracking-wide text-slate-500">{listing.status.replace("_", " ")}</p>
          <h1 className="text-3xl font-bold text-slate-900">{title}</h1>
          <p className="mt-2 text-3xl font-bold text-emerald-700">{formatPrice(listing.asking_price)}</p>
          {listing.negotiable && <p className="text-sm text-slate-600">Price is negotiable</p>}
          <ul className="mt-6 space-y-2 text-slate-700">
            <li>Year: {listing.manufacturing_year}</li>
            <li>Odometer: {listing.odometer_km.toLocaleString("en-IN")} km</li>
            <li>Fuel: {listing.fuel_type}</li>
            <li>Transmission: {listing.transmission}</li>
            <li>Body: {listing.body_type}</li>
            <li>Owners: {listing.num_owners}</li>
            <li>
              Location: {listing.city}
              {listing.locality ? `, ${listing.locality}` : ""}
            </li>
            {listing.registration_number_masked && <li>Reg: {listing.registration_number_masked}</li>}
            {listing.test_drive_available && <li>Test drive available</li>}
          </ul>
          {listing.reason_for_selling && (
            <p className="matte-glass mt-4 p-4 text-sm text-slate-700">{listing.reason_for_selling}</p>
          )}
          {listing.seller_contact_phone && (
            <p className="mt-4 rounded-xl border border-emerald-200/80 bg-emerald-50/90 p-4 text-sm text-slate-800">
              Seller phone:{" "}
              <a href={`tel:${listing.seller_contact_phone}`} className="font-semibold text-emerald-800">
                {listing.seller_contact_phone}
              </a>
            </p>
          )}
          <ListingActions listingId={listing.id} listingTitle={title} />
        </div>
      </div>
    </main>
  );
}
