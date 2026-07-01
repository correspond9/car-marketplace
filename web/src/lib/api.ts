const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

export type Listing = {
  id: string;
  make: string;
  model: string;
  variant: string | null;
  manufacturing_year: number;
  fuel_type: string;
  transmission: string;
  body_type: string;
  odometer_km: number;
  asking_price: number;
  negotiable: boolean;
  city: string;
  locality: string | null;
  status: string;
  registration_number_masked: string | null;
  images: Array<{ id: string; url: string; is_cover: boolean }>;
};

export type ListingListResponse = {
  items: Listing[];
  total: number;
  page: number;
  limit: number;
  pages: number;
};

async function fetchApi<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
    next: { revalidate: 60 },
  });
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function formatPrice(paise: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(paise);
}

export function searchListings(params: Record<string, string | number | undefined>) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") {
      query.set(key, String(value));
    }
  }
  const qs = query.toString();
  return fetchApi<ListingListResponse>(`/listings${qs ? `?${qs}` : ""}`);
}

export function getListing(id: string) {
  return fetchApi<Listing>(`/listings/${id}`);
}
