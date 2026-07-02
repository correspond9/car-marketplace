import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const PUBLIC_PATHS = ["/login", "/terms", "/privacy", "/help", "/disclaimer"];

function isPublicPath(pathname: string): boolean {
  if (pathname.startsWith("/_next")) return true;
  if (pathname.startsWith("/downloads")) return true;
  if (pathname.startsWith("/videos")) return true;
  if (/\.(?:ico|png|jpg|jpeg|svg|webp|mp4|apk|txt|xml)$/i.test(pathname)) return true;
  return PUBLIC_PATHS.some((path) => pathname === path || pathname.startsWith(`${path}/`));
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  if (isPublicPath(pathname)) {
    return NextResponse.next();
  }

  const loggedIn =
    request.cookies.get("cm_logged_in")?.value === "1" &&
    Boolean(request.cookies.get("cm_access_token")?.value);

  if (!loggedIn) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    const redirectTarget = `${pathname}${request.nextUrl.search}`;
    url.searchParams.set("redirect", redirectTarget);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
