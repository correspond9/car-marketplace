"use client";

import Link from "next/link";
import { useBrand } from "@/components/BrandProvider";

export function SiteFooter() {
  const { brand_name } = useBrand();

  return (
    <footer className="mt-auto border-t border-slate-200 bg-white">
      <div className="mx-auto max-w-6xl px-4 py-10">
        <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4">
          <div>
            <p className="text-lg font-bold text-emerald-700">{brand_name}</p>
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

        <div className="mt-10 flex flex-col items-center justify-center border-t border-slate-100 pt-8">
          <p className="mb-3 text-sm font-medium text-slate-700">Get the Android app</p>
          <a
            href="/downloads/carmarket-android.apk"
            download="CarMarket-android.apk"
            className="matte-glass group flex items-center gap-3 rounded-2xl px-5 py-3 transition hover:-translate-y-0.5 hover:shadow-[0_8px_32px_-10px_rgba(15,23,42,0.12)]"
            aria-label="Download Car-Market Android app"
          >
            <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-700 text-white shadow-sm">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="currentColor"
                className="h-7 w-7"
                aria-hidden
              >
                <path d="M17.6 9.48l1.84-3.18c.16-.28.06-.62-.22-.78a.6.6 0 00-.78.22l-1.87 3.24a11.43 11.43 0 00-8.58 0L5.12 5.74a.6.6 0 00-.78-.22c-.28.16-.38.5-.22.78L5.96 9.48A10.81 10.81 0 001 18h22a10.81 10.81 0 00-4.96-8.52zM7 15.25a1.25 1.25 0 110-2.5 1.25 1.25 0 010 2.5zm10 0a1.25 1.25 0 110-2.5 1.25 1.25 0 010 2.5z" />
              </svg>
            </span>
            <span className="text-left">
              <span className="block text-sm font-semibold text-slate-900 group-hover:text-emerald-800">
                Download APK
              </span>
              <span className="block text-xs text-slate-500">Android · free · dev build</span>
            </span>
          </a>
          <p className="mt-3 max-w-md text-center text-xs text-slate-500">
            On your phone, allow install from unknown sources if asked. Use the same Wi‑Fi as your PC for listings to load.
          </p>
        </div>

        <p className="mt-8 border-t border-slate-100 pt-6 text-center text-xs text-slate-500">
          © {new Date().getFullYear()} {brand_name} India. Operated as an online intermediary under the Information
          Technology Act, 2000.
        </p>
      </div>
    </footer>
  );
}
