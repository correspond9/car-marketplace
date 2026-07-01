import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="mt-auto border-t border-slate-200 bg-white">
      <div className="mx-auto max-w-6xl px-4 py-10">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <p className="text-lg font-bold text-emerald-700">CarMarket</p>
            <p className="mt-2 text-sm text-slate-600">
              India&apos;s trusted marketplace to buy and sell used cars from individuals and verified dealers.
            </p>
          </div>
          <div>
            <p className="font-semibold text-slate-900">Buy &amp; sell</p>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>
                <Link href="/search" className="hover:text-emerald-700">
                  Browse listings
                </Link>
              </li>
              <li>
                <Link href="/sell" className="hover:text-emerald-700">
                  Sell your car
                </Link>
              </li>
              <li>
                <Link href="/compare" className="hover:text-emerald-700">
                  Compare cars
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <p className="font-semibold text-slate-900">Popular cities</p>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>
                <Link href="/used-cars/mumbai" className="hover:text-emerald-700">
                  Used cars in Mumbai
                </Link>
              </li>
              <li>
                <Link href="/used-cars/delhi" className="hover:text-emerald-700">
                  Used cars in Delhi
                </Link>
              </li>
              <li>
                <Link href="/used-cars/bangalore" className="hover:text-emerald-700">
                  Used cars in Bangalore
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <p className="font-semibold text-slate-900">Legal</p>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>
                <Link href="/terms" className="hover:text-emerald-700">
                  Terms of use
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="hover:text-emerald-700">
                  Privacy policy
                </Link>
              </li>
              <li>
                <Link href="/disclaimer" className="hover:text-emerald-700">
                  Disclaimer
                </Link>
              </li>
            </ul>
          </div>
        </div>
        <p className="mt-8 border-t border-slate-100 pt-6 text-center text-xs text-slate-500">
          © {new Date().getFullYear()} CarMarket India. Operated as an online intermediary under the Information
          Technology Act, 2000.
        </p>
      </div>
    </footer>
  );
}
