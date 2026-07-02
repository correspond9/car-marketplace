"use client";

import Script from "next/script";
import { useEffect, useState } from "react";
import { api, ApiError } from "@/lib/api";

declare global {
  interface Window {
    Razorpay?: new (options: Record<string, unknown>) => { open: () => void };
  }
}

export default function PaymentTestPage() {
  const [config, setConfig] = useState<{ configured: boolean; key_id: string | null; mode: string } | null>(null);
  const [amount, setAmount] = useState("1");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [scriptReady, setScriptReady] = useState(false);

  useEffect(() => {
    api.payments
      .razorpayConfig()
      .then(setConfig)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load payment config"));
  }, []);

  async function startTestPayment() {
    setLoading(true);
    setError(null);
    setMessage(null);

    try {
      if (!window.Razorpay) {
        throw new Error("Razorpay checkout is still loading. Please wait a moment and try again.");
      }

      const order = await api.payments.createRazorpayOrder(Number(amount));
      const rzp = new window.Razorpay({
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: "Car-Market",
        description: "Production payment gateway test",
        order_id: order.order_id,
        theme: { color: "#15803d" },
        handler: async (response: {
          razorpay_order_id: string;
          razorpay_payment_id: string;
          razorpay_signature: string;
        }) => {
          try {
            const verified = await api.payments.verifyRazorpayPayment(response);
            setMessage(`Payment verified successfully. Payment ID: ${verified.payment_id}`);
          } catch (err) {
            setError(err instanceof ApiError ? err.message : "Payment verification failed");
          }
        },
        modal: {
          ondismiss: () => setMessage("Payment window closed."),
        },
      });
      rzp.open();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : err instanceof Error ? err.message : "Payment failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="mx-auto max-w-lg px-4 py-10">
      <Script
        src="https://checkout.razorpay.com/v1/checkout.js"
        strategy="afterInteractive"
        onLoad={() => setScriptReady(true)}
      />

      <div className="matte-glass p-6">
        <h1 className="text-2xl font-bold text-slate-900">Payment gateway test</h1>
        <p className="mt-2 text-sm text-slate-600">
          Use Razorpay test mode on production. This page is for staff testing only.
        </p>

        {config && (
          <div className="mt-4 rounded-xl border border-slate-200 bg-white/70 p-4 text-sm text-slate-700">
            <p>
              Gateway status:{" "}
              <strong className={config.configured ? "text-emerald-700" : "text-red-600"}>
                {config.configured ? "Connected" : "Not configured on server"}
              </strong>
            </p>
            <p className="mt-1">Mode: {config.mode}</p>
            {config.key_id && <p className="mt-1 break-all">Key ID: {config.key_id}</p>}
          </div>
        )}

        <div className="mt-6">
          <label htmlFor="amount" className="block text-sm font-medium text-slate-700">
            Test amount (₹)
          </label>
          <input
            id="amount"
            type="number"
            min="1"
            max="5000"
            step="1"
            value={amount}
            onChange={(e) => setAmount(e.target.value)}
            className="input-matte mt-1"
          />
          <p className="mt-1 text-xs text-slate-500">Use ₹1 for a quick test. Razorpay test cards apply.</p>
        </div>

        <button
          type="button"
          disabled={loading || !scriptReady || !config?.configured}
          onClick={startTestPayment}
          className="btn-matte-primary mt-6 w-full disabled:opacity-60"
        >
          {loading ? "Opening Razorpay…" : "Pay with Razorpay (test)"}
        </button>

        {error && <p className="mt-4 text-sm text-red-600">{error}</p>}
        {message && <p className="mt-4 text-sm text-emerald-700">{message}</p>}

        <p className="mt-6 text-xs text-slate-500">
          Razorpay test card: 4111 1111 1111 1111 · any future expiry · any CVV · OTP 123456.
        </p>
      </div>
    </main>
  );
}
