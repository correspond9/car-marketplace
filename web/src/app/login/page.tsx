"use client";

import { Suspense, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useAuth } from "@/components/AuthProvider";
import { api, ApiError, normalizePhone } from "@/lib/api";

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refreshUser, isLoggedIn } = useAuth();
  const redirect = searchParams.get("redirect") ?? "/";

  const [step, setStep] = useState<"phone" | "otp">("phone");
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isLoggedIn) router.replace(redirect);
  }, [isLoggedIn, redirect, router]);

  async function handleRequestOtp(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.auth.requestOtp(phone);
      setStep("otp");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not send OTP");
    } finally {
      setLoading(false);
    }
  }

  async function handleVerifyOtp(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      await api.auth.verifyOtp(phone, otp);
      await refreshUser();
      router.replace(redirect);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Invalid OTP");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-md px-4 py-12">
      <div className="animate-fade-up">
        <h1 className="text-2xl font-bold text-slate-900">Log in to Car-Market</h1>
        <p className="mt-2 text-sm text-slate-600">
          Enter your mobile number. We will send a one-time password (OTP) to verify you.
        </p>

        {step === "phone" ? (
          <form onSubmit={handleRequestOtp} className="matte-glass mt-8 space-y-4 p-6">
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-slate-700">
                Mobile number
              </label>
              <input
                id="phone"
                type="tel"
                inputMode="numeric"
                placeholder="10-digit mobile number"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                required
                className="input-matte mt-1"
              />
              <p className="mt-1 text-xs text-slate-500">Example: {normalizePhone("9876543210")}</p>
            </div>
            {error && <p className="text-sm text-red-600">{error}</p>}
            <button type="submit" disabled={loading} className="btn-matte-primary w-full disabled:opacity-60">
              {loading ? "Sending OTP…" : "Send OTP"}
            </button>
          </form>
        ) : (
          <form onSubmit={handleVerifyOtp} className="matte-glass mt-8 space-y-4 p-6">
          <p className="text-sm text-slate-600">
            OTP sent to <strong>{normalizePhone(phone)}</strong>.{" "}
            <button type="button" onClick={() => setStep("phone")} className="text-emerald-700 hover:underline">
              Change number
            </button>
          </p>
          <div>
            <label htmlFor="otp" className="block text-sm font-medium text-slate-700">
              Enter OTP
            </label>
            <input
              id="otp"
              type="text"
              inputMode="numeric"
              autoComplete="one-time-code"
              value={otp}
              onChange={(e) => setOtp(e.target.value)}
              required
              minLength={4}
              maxLength={8}
              className="input-matte mt-1 tracking-widest"
            />
          </div>
          {error && <p className="text-sm text-red-600">{error}</p>}
          <button type="submit" disabled={loading} className="btn-matte-primary w-full disabled:opacity-60">
            {loading ? "Verifying…" : "Verify & log in"}
          </button>
        </form>
      )}

      <p className="mt-6 text-center text-xs text-slate-500">
        By continuing, you agree to our{" "}
        <Link href="/terms" className="text-emerald-700 hover:underline">
          Terms
        </Link>{" "}
        and{" "}
        <Link href="/privacy" className="text-emerald-700 hover:underline">
          Privacy Policy
        </Link>
        .
      </p>
      </div>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<main className="px-4 py-12 text-center text-slate-600">Loading…</main>}>
      <LoginForm />
    </Suspense>
  );
}
