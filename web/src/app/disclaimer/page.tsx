import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Disclaimer",
  description: "Important disclaimers for CarMarket India used car marketplace.",
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-2">
      <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
      <div className="space-y-2 text-slate-700">{children}</div>
    </section>
  );
}

export default function DisclaimerPage() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <article className="space-y-6">
        <h1 className="text-3xl font-bold text-slate-900">Disclaimer</h1>
        <p className="text-sm text-slate-500">Last updated: 2 July 2026</p>

        <Section title="Platform role">
          <p>
            CarMarket is an <strong>online intermediary</strong> that provides a venue for users to list and discover used
            vehicles. We are not a motor vehicle dealer, broker, insurer, or financier unless explicitly stated for a
            specific product. We do not take possession of vehicles or buyer payments for the sale itself.
          </p>
        </Section>

        <Section title="No warranty on listings">
          <p>
            Listings, photos, prices, and descriptions are submitted by users. We do not independently verify every
            detail. Buyers must conduct their own inspection, test drive, RC/loan verification, and legal checks before
            purchase. &quot;Verified dealer&quot; badges indicate document review at a point in time and do not guarantee
            future conduct or vehicle condition.
          </p>
        </Section>

        <Section title="Vehicle history">
          <p>
            Odometer readings, accident history, service records, and ownership details depend on seller disclosure.
            CarMarket is not responsible for odometer tampering, hidden defects, or title disputes unless caused by
            our gross negligence.
          </p>
        </Section>

        <Section title="Third-party links and services">
          <p>
            The Platform may link to third-party sites (insurance, finance, maps). We are not responsible for their
            content, pricing, or privacy practices.
          </p>
        </Section>

        <Section title="Availability">
          <p>
            We strive for reliable service but do not guarantee uninterrupted access. Listings may expire, be removed, or
            be marked sold without notice.
          </p>
        </Section>

        <Section title="Investment & advice">
          <p>
            Nothing on CarMarket constitutes financial, legal, or mechanical advice. Consult qualified professionals
            before significant purchase decisions.
          </p>
        </Section>

        <Section title="Reporting concerns">
          <p>
            If you believe a listing is fraudulent or violates our policies, use the report feature or email{" "}
            <a href="mailto:trust@carmarket.in" className="text-emerald-700 hover:underline">
              trust@carmarket.in
            </a>
            .
          </p>
        </Section>

        <p className="text-sm text-slate-600">
          <Link href="/terms" className="text-emerald-700 hover:underline">
            Terms of Use
          </Link>{" "}
          ·{" "}
          <Link href="/privacy" className="text-emerald-700 hover:underline">
            Privacy Policy
          </Link>
        </p>
      </article>
    </main>
  );
}
