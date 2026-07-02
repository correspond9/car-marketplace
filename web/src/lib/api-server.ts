import "server-only";

import { cookies } from "next/headers";
import { AUTH_COOKIE } from "@/lib/auth-cookie";
import {
  ApiError,
  type DealerStore,
  type Listing,
  type ListingListResponse,
  type SearchListingsParams,
} from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function getServerAccessToken(): Promise<string | null> {
  const cookieStore = await cookies();
  const raw = cookieStore.get(AUTH_COOKIE.access)?.value;
  return raw ? decodeURIComponent(raw) : null;
}

function buildQuery(params: Record<string, string | number | undefined | boolean>): string {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      query.set(key, String(value));
    }
  }
  const qs = query.toString();
  return qs ? `?${qs}` : "";
}

async function serverRequest<T>(path: string, options: { next?: NextFetchRequestConfig } = {}): Promise<T> {
  const token = await getServerAccessToken();
  const headers: Record<string, string> = { Accept: "application/json" };
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_BASE}${path}`, {
    headers,
    next: options.next,
  });

  if (!response.ok) {
    try {
      const data = (await response.json()) as { error?: { code: string; message: string } };
      const err = data.error ?? { code: "UNKNOWN", message: response.statusText };
      throw new ApiError(response.status, err.code, err.message);
    } catch (error) {
      if (error instanceof ApiError) throw error;
      throw new ApiError(response.status, "UNKNOWN", response.statusText);
    }
  }

  return response.json() as Promise<T>;
}

export function searchListings(params: SearchListingsParams = {}) {
  return serverRequest<ListingListResponse>(
    `/listings${buildQuery(params as Record<string, string | number | undefined>)}`,
    { next: { revalidate: 60 } },
  );
}

export function getListing(id: string) {
  return serverRequest<Listing>(`/listings/${id}`, { next: { revalidate: 60 } });
}

export function getDealerStore(slug: string) {
  return serverRequest<DealerStore>(`/dealer-stores/${slug}`, { next: { revalidate: 120 } });
}
