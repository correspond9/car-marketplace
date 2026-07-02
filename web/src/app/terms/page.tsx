import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Terms of Use",
  description: "Car-Market India terms of use for buyers, sellers, and dealers.",
};

export default function TermsPage() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <article className="space-y-6 text-slate-700">
      <h1 className="text-3xl font-bold text-slate-900">Terms of Use</h1>
      <p className="text-sm text-slate-500">Last updated: 2 July 2026</p>

      <section>
      <h2 className="text-xl font-semibold text-slate-900">1. About Car-Market</h2>
      <p>
        Car-Market (&quot;Platform&quot;, &quot;we&quot;, &quot;us&quot;) operates an online marketplace that connects buyers and
        sellers of used motor vehicles in India. We act as an <strong>intermediary</strong> under the Information
        Technology Act, 2000 and the Information Technology (Intermediary Guidelines and Digital Media Ethics
        Code) Rules, 2021. We do not own the vehicles listed and are not a party to transactions between users.
      </p>
      </section>

      <section>
      <h2 className="text-xl font-semibold text-slate-900">2. Eligibility</h2>
      <p>
        You must be at least 18 years old and competent to contract under the Indian Contract Act, 1872. By using
        the Platform, you confirm that information you provide is accurate and that you have authority to list or
        inquire about vehicles.
      </p>
      </section>

      <section>
      <h2 className="text-xl font-semibold text-slate-900">3. User accounts</h2>
      <p>
        Registration requires a verified mobile number via OTP. You are responsible for activity on your account.
        Dealers must provide accurate business details and comply with applicable motor vehicle and trade laws.
      </p>
      </section>

      <section>
      <h2 className="text-xl font-semibold text-slate-900">4. Listings and content</h2>
      <ul className="list-disc space-y-1 pl-5">
        <li>Sellers must describe vehicles truthfully, including km, ownership, accident history, and encumbrances.</li>
        <li>Prohibited content includes fraudulent listings, stolen vehicles, misleading photos, and hate speech.</li>
        <li>We may remove, reject, or moderate content that violates these terms or applicable law.</li>
      </ul>
      </section>

      <section>
      <h2 className="text-xl font-semibold text-slate-900">5. Transactions</h2>
      <p>
        All price negotiations, payments, registration transfer, and delivery are solely between buyer and seller.
        Car-Market does not guarantee vehicle condition, title, or completion of sale. Users should inspect vehicles
        and verify documents independently.
      </p>
      </section>

      <section>
      <h2 className="text-xl font-semibold text-slate-900">6. Fees</h2>
      <p>
        Basic listing may be free during early access. We may introduce paid features or dealer subscriptions with
        prior notice on the Platform.
      </p>
      </section>

      <section>
      <h2 className="text-xl font-semibold text-slate-900">7. Limitation of liability</h2>
      <p>
        To the maximum extent permitted by law, Car-Market is not liable for indirect, incidental, or consequential
        damages arising from use of the Platform or user interactions. Our aggregate liability shall not exceed fees
        paid to us in the preceding twelve months, if any.
      </p>
      </section>

      <section>
      <h2 className="text-xl font-semibold text-slate-900">8. Governing law</h2>
      <p>
        These terms are governed by the laws of India. Courts at Mumbai, Maharashtra shall have exclusive
        jurisdiction, subject to applicable consumer protection laws.
      </p>
      </section>

      <section>
        <h2 className="text-xl font-semibold text-slate-900">9. Contact</h2>
        <p>
          For legal or compliance queries:{" "}
          <a href="mailto:legal@carmarket.in" className="text-emerald-700">
            legal@carmarket.in
          </a>
        </p>
        <p className="text-sm">
          See also our{" "}
          <Link href="/privacy" className="text-emerald-700">
            Privacy Policy
          </Link>{" "}
          and{" "}
          <Link href="/disclaimer" className="text-emerald-700">
            Disclaimer
          </Link>
          .
        </p>
      </section>
      </article>
    </main>
  );
}
