"use client";

import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";
import { useBrand } from "@/components/BrandProvider";
import { resolveBrandLogoUrl } from "@/lib/listingImages";

export function SiteHeader() {
  const { user, loading, logout } = useAuth();
  const { brand_name, logo_url } = useBrand();
  const isModerator = user?.role === "moderator" || user?.role === "admin";

  return (
    <header className="matte-glass-header sticky top-0 z-50">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-3.5 sm:py-4">
        <Link
          href="/"
          className="flex shrink-0 items-center rounded-xl bg-white/90 px-2 py-1.5 shadow-sm ring-1 ring-slate-200/80 transition hover:bg-white"
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src={resolveBrandLogoUrl(logo_url)}
            alt={brand_name}
            className="h-12 w-auto min-w-[10rem] max-w-[13rem] object-contain sm:h-14 sm:max-w-[15rem]"
          />
          <span className="sr-only">{brand_name}</span>
        </Link>
        <nav className="flex flex-wrap items-center gap-2 text-sm font-medium text-slate-700 sm:gap-3">
          <Link href="/search" className="rounded-lg px-2 py-1 transition hover:bg-white/60 hover:text-emerald-700">
            Browse cars
          </Link>
          <Link href="/compare" className="rounded-lg px-2 py-1 transition hover:bg-white/60 hover:text-emerald-700">
            Compare
          </Link>
          <Link href="/sell" className="rounded-lg px-2 py-1 transition hover:bg-white/60 hover:text-emerald-700">
            Sell car
          </Link>
          {user && (
            <>
              <Link href="/inquiries" className="rounded-lg px-2 py-1 transition hover:bg-white/60 hover:text-emerald-700">
                Messages
              </Link>
              <Link href="/recently-viewed" className="rounded-lg px-2 py-1 transition hover:bg-white/60 hover:text-emerald-700">
                Recently viewed
              </Link>
              <Link href="/favorites" className="rounded-lg px-2 py-1 transition hover:bg-white/60 hover:text-emerald-700">
                Favorites
              </Link>
              <Link href="/my-listings" className="rounded-lg px-2 py-1 transition hover:bg-white/60 hover:text-emerald-700">
                My listings
              </Link>
            </>
          )}
          {isModerator && (
            <Link href="/admin" className="rounded-lg px-2 py-1 transition hover:bg-white/60 hover:text-emerald-700">
              Admin
            </Link>
          )}
          <a
            href="/downloads/carmarket-android.apk"
            download="CarMarket-android.apk"
            className="btn-matte-secondary inline-flex shrink-0 items-center gap-1.5 px-3 py-1.5 text-sm"
            aria-label="Download Car-Market Android app"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="currentColor"
              className="h-4 w-4 shrink-0"
              aria-hidden
            >
              <path d="M17.6 9.48l1.84-3.18c.16-.28.06-.62-.22-.78a.6.6 0 00-.78.22l-1.87 3.24a11.43 11.43 0 00-8.58 0L5.12 5.74a.6.6 0 00-.78-.22c-.28.16-.38.5-.22.78L5.96 9.48A10.81 10.81 0 001 18h22a10.81 10.81 0 00-4.96-8.52zM7 15.25a1.25 1.25 0 110-2.5 1.25 1.25 0 010 2.5zm10 0a1.25 1.25 0 110-2.5 1.25 1.25 0 010 2.5z" />
            </svg>
            Android app
          </a>
          {!loading && (
            user ? (
              <button
                type="button"
                onClick={() => logout()}
                className="rounded-xl border border-slate-200/90 bg-white/70 px-3 py-1.5 shadow-sm transition hover:border-emerald-300 hover:text-emerald-700 active:scale-[0.98]"
              >
                Log out
              </button>
            ) : (
              <Link
                href="/login"
                className="btn-matte-primary px-4 py-2 text-sm"
              >
                Log in
              </Link>
            )
          )}
        </nav>
      </div>
    </header>
  );
}
