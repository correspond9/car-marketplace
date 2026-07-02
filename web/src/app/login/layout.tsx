import { LoginBackgroundVideo } from "@/components/LoginBackgroundVideo";

export default function LoginLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="relative flex min-h-[calc(100dvh-7.5rem)] flex-1 flex-col overflow-hidden bg-slate-950">
      <LoginBackgroundVideo />
      <div className="relative z-10 flex flex-1 flex-col">{children}</div>
    </div>
  );
}
