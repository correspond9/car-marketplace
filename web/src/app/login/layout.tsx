import { LoginBackgroundVideo } from "@/components/LoginBackgroundVideo";

export default function LoginLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      {/* Fixed layer fills the main area below the header on desktop and mobile web. */}
      <div
        aria-hidden
        className="pointer-events-none fixed inset-x-0 bottom-0 top-[4.25rem] z-0 sm:top-[4.75rem]"
      >
        <LoginBackgroundVideo />
      </div>
      <div className="relative z-10 flex min-h-[calc(100svh-4.25rem)] flex-1 flex-col sm:min-h-[calc(100svh-4.75rem)]">
        {children}
      </div>
    </>
  );
}
