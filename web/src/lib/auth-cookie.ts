export const AUTH_COOKIE = {
  access: "cm_access_token",
  loggedIn: "cm_logged_in",
} as const;

const COOKIE_MAX_AGE = 60 * 60 * 24 * 30;

export function authCookieOptions(): string {
  return `path=/; max-age=${COOKIE_MAX_AGE}; SameSite=Lax`;
}

export function setAuthCookies(accessToken: string): void {
  if (typeof document === "undefined") return;
  const opts = authCookieOptions();
  document.cookie = `${AUTH_COOKIE.access}=${encodeURIComponent(accessToken)}; ${opts}`;
  document.cookie = `${AUTH_COOKIE.loggedIn}=1; ${opts}`;
}

export function clearAuthCookies(): void {
  if (typeof document === "undefined") return;
  document.cookie = `${AUTH_COOKIE.access}=; path=/; max-age=0`;
  document.cookie = `${AUTH_COOKIE.loggedIn}=; path=/; max-age=0`;
}
