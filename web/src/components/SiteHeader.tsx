"use client";

import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";

export function SiteHeader() {
  const { user, loading, logout } = useAuth();
  const isModerator = user?.role === "moderator" || user?.role === "admin";

  return (
    <header className="border-b border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-4">
        <Link href="/" className="text-xl font-bold text-emerald-700">
          CarMarket
        </Link>
        <nav className="flex flex-wrap items-center gap-3 text-sm font-medium text-slate-700">
          <Link href="/search" className="hover:text-emerald-700">
            Browse cars
          </Link>
          <Link href="/compare" className="hover:text-emerald-700">
            Compare
          </Link>
          <Link href="/sell" className="hover:text-emerald-700">
            Sell car
          </Link>
          {user && (
            <>
              <Link href="/favorites" className="hover:text-emerald-700">
                Favorites
              </Link>
              <Link href="/my-listings" className="hover:text-emerald-700">
                My listings
              </Link>
            </>
          )}
          {isModerator && (
            <Link href="/admin" className="hover:text-emerald-700">
              Admin
            </Link>
          )}
          {!loading && (
            user ? (
              <button
                type="button"
                onClick={() => logout()}
                className="rounded-lg border border-slate-300 px-3 py-1.5 hover:border-emerald-600 hover:text-emerald-700"
              >
                Log out
              </button>
            ) : (
              <Link
                href="/login"
                className="rounded-lg bg-emerald-700 px-3 py-1.5 text-white hover:bg-emerald-800"
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
