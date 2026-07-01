import { ListingCard, SiteHeader } from "@/components/SiteHeader";
import { searchListings } from "@/lib/api";

type SearchParams = Promise<{ [key: string]: string | string[] | undefined }>;

export default async function SearchPage({ searchParams }: { searchParams: SearchParams }) {
  const params = await searchParams;
  const q = typeof params.q === "string" ? params.q : undefined;
  const city = typeof params.city === "string" ? params.city : undefined;
  const make = typeof params.make === "string" ? params.make : undefined;

  let data: Awaited<ReturnType<typeof searchListings>> | null = null;
  try {
    data = await searchListings({ q, city, make, sort: "newest", limit: 24 });
  } catch {
    data = null;
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <SiteHeader />
      <main className="mx-auto max-w-6xl px-4 py-8">
        <h1 className="text-2xl font-bold text-slate-900">Browse used cars</h1>
        <form method="get" className="mt-6 grid gap-4 rounded-xl border border-slate-200 bg-white p-4 sm:grid-cols-4">
          <input
            name="q"
            defaultValue={q}
            placeholder="Search make, model..."
            className="rounded-lg border border-slate-300 px-3 py-2 sm:col-span-2"
          />
          <input
            name="city"
            defaultValue={city}
            placeholder="City"
            className="rounded-lg border border-slate-300 px-3 py-2"
          />
          <button
            type="submit"
            className="rounded-lg bg-emerald-700 px-4 py-2 font-medium text-white hover:bg-emerald-800"
          >
            Search
          </button>
        </form>

        <p className="mt-6 text-sm text-slate-600">
          {data ? `${data.total} car${data.total === 1 ? "" : "s"} found` : "Could not load listings"}
        </p>

        <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {data?.items.map((listing) => (
            <ListingCard key={listing.id} listing={listing} />
          ))}
        </div>
      </main>
    </div>
  );
}
