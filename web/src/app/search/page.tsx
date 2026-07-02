import { ListingCard } from "@/components/ListingCard";
import { searchListings } from "@/lib/api";
import { buildListingImageSlots } from "@/lib/listingImages";

type SearchParams = Promise<{ [key: string]: string | string[] | undefined }>;

export default async function SearchPage({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const q = typeof params.q === "string" ? params.q : undefined;
  const city = typeof params.city === "string" ? params.city : undefined;
  const make = typeof params.make === "string" ? params.make : undefined;
  const sellerType = typeof params.seller_type === "string" ? params.seller_type : undefined;

  let data: Awaited<ReturnType<typeof searchListings>> | null = null;
  try {
    data = await searchListings({
      q,
      city,
      make,
      seller_type: sellerType as "individual" | "dealer" | undefined,
      sort: "newest",
      limit: 24,
    });
  } catch {
    data = null;
  }
  const imageSlots = buildListingImageSlots(data?.items ?? []);

  return (
    <main className="mx-auto max-w-6xl px-4 py-8">
      <h1 className="animate-fade-up text-2xl font-bold text-slate-900">Browse used cars</h1>
      <form method="get" className="matte-glass mt-6 grid gap-4 p-4 sm:grid-cols-5">
        <input
          name="q"
          defaultValue={q}
          placeholder="Search make, model..."
          className="input-matte sm:col-span-2"
        />
        <input name="city" defaultValue={city} placeholder="City" className="input-matte" />
        <select name="seller_type" defaultValue={sellerType ?? ""} className="input-matte">
          <option value="">All sellers</option>
          <option value="individual">Individuals</option>
          <option value="dealer">Dealers</option>
        </select>
        <button type="submit" className="btn-matte-primary text-sm">
          Search
        </button>
      </form>

      <p className="mt-6 text-sm text-slate-600">
        {data ? `${data.total} car${data.total === 1 ? "" : "s"} found` : "Could not load listings"}
      </p>

      <div className="stagger-children mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {data?.items.map((listing) => (
          <ListingCard key={listing.id} listing={listing} imageSlot={imageSlots.get(listing.id) ?? 0} />
        ))}
      </div>
    </main>
  );
}
