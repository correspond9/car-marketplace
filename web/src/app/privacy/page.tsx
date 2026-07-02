import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "How Car-Market India collects, uses, and protects your personal data under DPDP Act.",
};

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="space-y-2">
      <h2 className="text-xl font-semibold text-slate-900">{title}</h2>
      <div className="space-y-2 text-slate-700">{children}</div>
    </section>
  );
}

export default function PrivacyPage() {
  return (
    <main className="mx-auto max-w-3xl px-4 py-10">
      <article className="space-y-6">
        <h1 className="text-3xl font-bold text-slate-900">Privacy Policy</h1>
        <p className="text-sm text-slate-500">Last updated: 2 July 2026</p>

        <Section title="1. Introduction">
          <p>
            Car-Market India (&quot;we&quot;, &quot;us&quot;) respects your privacy. This policy explains how we collect, use, store,
            and share personal data when you use our website and mobile applications. We process data in accordance
            with the Digital Personal Data Protection Act, 2023 (DPDP Act) and applicable rules.
          </p>
        </Section>

        <Section title="2. Data we collect">
          <ul className="list-disc space-y-1 pl-5">
            <li>
              <strong>Identity &amp; contact:</strong> mobile number, name, email, city, profile photo (optional).
            </li>
            <li>
              <strong>Listing data:</strong> vehicle details, photos, location, registration information (masked in
              public views).
            </li>
            <li>
              <strong>Usage data:</strong> search queries, favorites, inquiries, device type, IP address, cookies.
            </li>
            <li>
              <strong>Dealer data:</strong> business name, address, GST/trade documents where provided for verification.
            </li>
          </ul>
        </Section>

        <Section title="3. Purpose of processing">
          <p>We use your data to:</p>
          <ul className="list-disc space-y-1 pl-5">
            <li>Authenticate you via OTP and maintain your account</li>
            <li>Display and moderate listings and dealer stores</li>
            <li>Enable buyer–seller inquiries and notifications</li>
            <li>Improve search, safety, fraud prevention, and customer support</li>
            <li>Comply with legal obligations and respond to lawful requests</li>
          </ul>
        </Section>

        <Section title="4. Legal basis">
          <p>
            Processing is based on your consent (e.g., account creation, marketing where opted in), performance of
            contract (providing marketplace services), and legitimate interests (security, analytics, moderation)
            balanced against your rights.
          </p>
        </Section>

        <Section title="5. Sharing of data">
          <p>We may share data with:</p>
          <ul className="list-disc space-y-1 pl-5">
            <li>Other users — e.g., seller contact when you send an inquiry</li>
            <li>Service providers — SMS/OTP, cloud hosting, analytics (under contract)</li>
            <li>Authorities — when required by law or to protect rights and safety</li>
          </ul>
          <p>We do not sell your personal data.</p>
        </Section>

        <Section title="6. Retention">
          <p>
            We retain data while your account is active and as needed for legal, tax, and dispute resolution purposes.
            Deleted accounts are soft-deleted and purged per our retention schedule unless law requires longer storage.
          </p>
        </Section>

        <Section title="7. Your rights (DPDP Act)">
          <p>You may request access, correction, erasure, consent withdrawal, and nomination under the DPDP Act.</p>
          <p>
            Contact{" "}
            <a href="mailto:privacy@carmarket.in" className="text-emerald-700 hover:underline">
              privacy@carmarket.in
            </a>
            . You may lodge a complaint with the Data Protection Board of India if unsatisfied with our response.
          </p>
        </Section>

        <Section title="8. Security">
          <p>
            We use encryption in transit (HTTPS), access controls, and monitoring. No method of transmission over the
            internet is 100% secure; please use strong device security.
          </p>
        </Section>

        <Section title="9. Children">
          <p>The Platform is not intended for users under 18. We do not knowingly collect data from children.</p>
        </Section>

        <Section title="10. Changes">
          <p>
            We may update this policy. Material changes will be notified on the Platform. Continued use after notice
            constitutes acceptance where permitted by law.
          </p>
        </Section>

        <p className="text-sm text-slate-600">
          <Link href="/terms" className="text-emerald-700 hover:underline">
            Terms of Use
          </Link>{" "}
          ·{" "}
          <Link href="/disclaimer" className="text-emerald-700 hover:underline">
            Disclaimer
          </Link>
        </p>
      </article>
    </main>
  );
}
