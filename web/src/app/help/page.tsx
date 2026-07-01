import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";

const faqs = [
  {
    q: "How do I transfer a used car RC in India?",
    a: "Both buyer and seller sign Form 29 & 30, get NOC if needed, pay road tax in the new state, and submit documents at the RTO. Always verify pending loans are cleared before paying.",
  },
  {
    q: "What documents should I check before buying?",
    a: "Original RC, valid insurance, PUC certificate, service records, and Form 35 if hypothecation was closed. Match the engine and chassis numbers with the RC.",
  },
  {
    q: "Is CarMarket involved in the sale?",
    a: "No. CarMarket is an intermediary platform connecting buyers and sellers. The sale agreement is directly between users.",
  },
  {
    q: "How do I contact a seller?",
    a: "Use the Contact seller button on a listing. The seller's phone is shared only after they accept your inquiry.",
  },
  {
    q: "How do I delete my account?",
    a: "Log in on the website or mobile app, go to Profile, and choose Delete account. You can also email our grievance officer listed on the Privacy page.",
  },
];

export default function HelpPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <SiteHeader />
      <main className="mx-auto max-w-3xl flex-1 px-4 py-12">
        <h1 className="text-3xl font-bold text-slate-900">Help centre</h1>
        <p className="mt-2 text-slate-600">Common questions about buying and selling used cars on CarMarket.</p>
        <div className="mt-8 space-y-6">
          {faqs.map((item) => (
            <section key={item.q} className="rounded-xl border border-slate-200 bg-white p-6">
              <h2 className="font-semibold text-slate-900">{item.q}</h2>
              <p className="mt-2 text-slate-600">{item.a}</p>
            </section>
          ))}
        </div>
        <p className="mt-8 text-sm text-slate-600">
          Still need help?{" "}
          <Link href="/privacy" className="text-emerald-700 hover:underline">
            Contact us via the grievance officer on our Privacy page
          </Link>
          .
        </p>
      </main>
      <SiteFooter />
    </div>
  );
}
