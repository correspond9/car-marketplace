import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { ListingCard } from "@/components/ListingCard";
import { getDealerStore, searchListings } from "@/lib/api-server";

type Props = { params: Promise<{ slug: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  try {
    const store = await getDealerStore(slug);
    return {
      title: `${store.name} — Dealer store`,
      description: store.description ?? `Browse used cars from ${store.name} on CarMarket.`,
    };
  } catch {
    return { title: "Dealer store" };
  }
}

export default async function DealerStorePage({ params }: Props) {
  const { slug } = await params;
  let store: Awaited<ReturnType<typeof getDealerStore>>;
  try {
    store = await getDealerStore(slug);
  } catch {
    notFound();
  }

  let inventory = store.listings ?? [];
  if (inventory.length === 0) {
    try {
      const data = await searchListings({ seller_type: "dealer", limit: 24 });
      inventory = data.items.filter((l) => l.dealer_store_id === store.id);
    } catch {
      inventory = [];
    }
  }

  return (
    <main>
      <section className="bg-emerald-800 px-4 py-10 text-white">
        <div className="mx-auto max-w-6xl">
          {store.logo_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={store.logo_url} alt="" className="mb-4 h-16 w-16 rounded-lg bg-white object-contain p-1" />
          )}
          <h1 className="text-3xl font-bold">{store.name}</h1>
          {store.verification_status === "verified" && (
            <span className="mt-2 inline-block rounded-full bg-emerald-600 px-2 py-0.5 text-xs font-medium">
              Verified dealer
            </span>
          )}
          {store.description && <p className="mt-3 max-w-2xl text-emerald-50">{store.description}</p>}
          <div className="mt-4 flex flex-wrap gap-4 text-sm text-emerald-100">
            {store.city && <span>{store.city}{store.state ? `, ${store.state}` : ""}</span>}
            {store.phone && <span>Phone: {store.phone}</span>}
            {store.rating_count > 0 && (
              <span>
                ★ {Number(store.rating_avg).toFixed(1)} ({store.rating_count} reviews)
              </span>
            )}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-6xl px-4 py-10">
        <h2 className="text-xl font-bold text-slate-900">Inventory</h2>
        {inventory.length === 0 ? (
          <p className="mt-6 rounded-lg border border-dashed border-slate-300 bg-white p-8 text-center text-slate-600">
            No live cars listed by this dealer yet.
          </p>
        ) : (
          <div className="mt-6 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {inventory.map((listing) => (
              <ListingCard key={listing.id} listing={listing} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
