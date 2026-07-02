import { clearAuthCookies, setAuthCookies } from "@/lib/auth-cookie";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

const TOKEN_KEYS = {
  access: "cm_access_token",
  refresh: "cm_refresh_token",
} as const;

// ── Enums & shared types ────────────────────────────────────────────────────

export type UserRole = "user" | "dealer" | "moderator" | "admin";
export type ListingStatus =
  | "draft"
  | "pending_review"
  | "live"
  | "sold"
  | "expired"
  | "removed";
export type FuelType = "petrol" | "diesel" | "cng" | "ev" | "hybrid";
export type Transmission = "manual" | "automatic" | "amt" | "dct";
export type BodyType =
  | "hatchback"
  | "sedan"
  | "suv"
  | "muv"
  | "coupe"
  | "convertible"
  | "pickup"
  | "van";
export type RCStatus = "valid" | "pending_transfer";
export type LoanStatus = "cleared" | "ongoing";
export type InquiryStatus = "open" | "accepted" | "declined" | "closed";
export type ReviewTargetType = "user" | "dealer_store";
export type ReportReason =
  | "scam"
  | "wrong_info"
  | "duplicate"
  | "offensive"
  | "already_sold";
export type SortOption =
  | "relevance"
  | "price_asc"
  | "price_desc"
  | "newest"
  | "lowest_km";

export type ModerationMode = "manual" | "auto";

export type PlatformSettings = {
  brand_name: string;
  brand_domain: string;
  logo_url: string | null;
};

export type PlatformSettingsAdmin = PlatformSettings & {
  moderation_mode: ModerationMode;
  enable_featured_listings: boolean;
  enable_dealer_subscriptions: boolean;
  enable_paid_listings: boolean;
  updated_at: string;
};

export type ApiErrorBody = {
  error: { code: string; message: string; details?: string[] };
};

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type UserPublic = {
  id: string;
  display_name: string | null;
  city: string | null;
  role: UserRole;
  created_at: string;
};

export type UserMe = UserPublic & {
  phone: string;
  email: string | null;
  phone_verified: boolean;
  email_verified: boolean;
  profile_photo_url: string | null;
};

export type ListingImage = {
  id: string;
  url: string;
  thumbnail_url: string | null;
  sort_order: number;
  is_cover: boolean;
};

export type Listing = {
  id: string;
  seller_id: string;
  dealer_store_id: string | null;
  make: string;
  model: string;
  variant: string | null;
  manufacturing_year: number;
  registration_year: number | null;
  body_type: BodyType;
  fuel_type: FuelType;
  transmission: Transmission;
  engine_capacity_cc: number | null;
  odometer_km: number;
  num_owners: number;
  accident_history: boolean;
  flood_history: boolean;
  service_history_available: boolean;
  registration_state: string | null;
  registration_city: string | null;
  registration_number_masked: string | null;
  rc_status: RCStatus | null;
  insurance_expiry: string | null;
  puc_expiry: string | null;
  loan_status: LoanStatus | null;
  asking_price: number;
  negotiable: boolean;
  exchange_accepted: boolean;
  reason_for_selling: string | null;
  city: string;
  locality: string | null;
  pincode: string | null;
  test_drive_available: boolean;
  show_contact_publicly?: boolean;
  status: ListingStatus;
  published_at: string | null;
  expires_at: string | null;
  created_at: string;
  images: ListingImage[];
  seller_contact_phone?: string | null;
  is_featured?: boolean;
};

export type ListingListResponse = {
  items: Listing[];
  total: number;
  page: number;
  limit: number;
  pages: number;
};

export type ListingCreateInput = {
  make: string;
  model: string;
  variant?: string | null;
  manufacturing_year: number;
  registration_year?: number | null;
  body_type: BodyType;
  fuel_type: FuelType;
  transmission: Transmission;
  engine_capacity_cc?: number | null;
  odometer_km: number;
  num_owners?: number;
  accident_history?: boolean;
  flood_history?: boolean;
  service_history_available?: boolean;
  registration_state?: string | null;
  registration_city?: string | null;
  registration_number?: string | null;
  rc_status?: RCStatus | null;
  insurance_expiry?: string | null;
  puc_expiry?: string | null;
  loan_status?: LoanStatus | null;
  asking_price: number;
  negotiable?: boolean;
  exchange_accepted?: boolean;
  reason_for_selling?: string | null;
  city: string;
  locality?: string | null;
  pincode?: string | null;
  test_drive_available?: boolean;
  show_contact_publicly?: boolean;
};

export type ListingUpdateInput = Partial<ListingCreateInput>;

export type PresignImageRequest = {
  content_type: string;
  filename: string;
};

export type PresignImageResponse = {
  upload_url: string;
  storage_key: string;
  url: string;
  image_id?: string;
  fields?: Record<string, string>;
};

export type ConfirmImageInput = {
  storage_key: string;
  url: string;
  is_cover?: boolean;
  sort_order?: number;
};

export type DealerStore = {
  id: string;
  owner_id: string;
  name: string;
  slug: string;
  description: string | null;
  logo_url: string | null;
  banner_url: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  pincode: string | null;
  latitude: number | null;
  longitude: number | null;
  phone: string | null;
  whatsapp: string | null;
  business_hours: Record<string, string> | null;
  rating_avg: number;
  rating_count: number;
  verification_status: "pending" | "verified" | "rejected";
  created_at: string;
  listings?: Listing[];
};

export type DealerStoreCreateInput = {
  name: string;
  slug?: string;
  description?: string | null;
  address?: string | null;
  city?: string | null;
  state?: string | null;
  pincode?: string | null;
  phone?: string | null;
  whatsapp?: string | null;
};

export type Inquiry = {
  id: string;
  listing_id: string;
  buyer_id: string;
  seller_id: string;
  message: string;
  status: InquiryStatus;
  created_at: string;
  seller_phone?: string | null;
  buyer_phone?: string | null;
  listing?: Listing;
};

export type InquiryListResponse = {
  items: Inquiry[];
  total: number;
  page: number;
  limit: number;
};

export type RecentlyViewedItem = {
  listing_id: string;
  viewed_at: string;
  listing: Listing | null;
};

export type RecentlyViewedListResponse = {
  items: RecentlyViewedItem[];
  total: number;
};

export type Review = {
  id: string;
  reviewer_id: string;
  target_type: ReviewTargetType;
  target_id: string;
  rating: number;
  text: string | null;
  seller_reply: string | null;
  status: string;
  created_at: string;
};

export type Favorite = {
  id: string;
  listing_id: string;
  created_at: string;
  listing?: Listing;
};

export type ReportCreateInput = {
  entity_type: "listing" | "user" | "dealer_store" | "review";
  entity_id: string;
  reason: ReportReason;
  details?: string | null;
};

export type SearchListingsParams = {
  q?: string;
  make?: string;
  model?: string;
  min_price?: number;
  max_price?: number;
  min_year?: number;
  max_year?: number;
  max_km?: number;
  fuel?: FuelType;
  transmission?: Transmission;
  body_type?: BodyType;
  city?: string;
  state?: string;
  seller_type?: "individual" | "dealer";
  sort?: SortOption;
  page?: number;
  limit?: number;
};

// ── Token storage (browser only) ────────────────────────────────────────────

export const tokenStorage = {
  getAccessToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(TOKEN_KEYS.access);
  },
  getRefreshToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem(TOKEN_KEYS.refresh);
  },
  setTokens(access: string, refresh: string): void {
    if (typeof window === "undefined") return;
    localStorage.setItem(TOKEN_KEYS.access, access);
    localStorage.setItem(TOKEN_KEYS.refresh, refresh);
    setAuthCookies(access);
  },
  clearTokens(): void {
    if (typeof window === "undefined") return;
    localStorage.removeItem(TOKEN_KEYS.access);
    localStorage.removeItem(TOKEN_KEYS.refresh);
    clearAuthCookies();
  },
  isLoggedIn(): boolean {
    return !!this.getAccessToken();
  },
};

// ── HTTP helpers ──────────────────────────────────────────────────────────────

type RequestOptions = {
  method?: string;
  body?: unknown;
  auth?: boolean;
  cache?: RequestCache;
  next?: NextFetchRequestConfig;
};

async function parseError(response: Response): Promise<ApiError> {
  try {
    const data = (await response.json()) as ApiErrorBody;
    const err = data.error ?? { code: "UNKNOWN", message: response.statusText };
    return new ApiError(response.status, err.code, err.message);
  } catch {
    return new ApiError(response.status, "UNKNOWN", response.statusText);
  }
}

async function refreshTokensInternal(): Promise<boolean> {
  const refreshToken = tokenStorage.getRefreshToken();
  if (!refreshToken) return false;
  try {
    const response = await fetch(`${API_BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!response.ok) {
      tokenStorage.clearTokens();
      return false;
    }
    const tokens = (await response.json()) as TokenResponse;
    tokenStorage.setTokens(tokens.access_token, tokens.refresh_token);
    return true;
  } catch {
    tokenStorage.clearTokens();
    return false;
  }
}

async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = "GET", body, auth = false, cache, next } = options;
  const headers: Record<string, string> = {
    Accept: "application/json",
  };
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (auth) {
    const token = tokenStorage.getAccessToken();
    if (token) headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
    cache,
    next,
  });

  if (response.status === 401 && auth && tokenStorage.getRefreshToken()) {
    const refreshed = await refreshTokensInternal();
    if (refreshed) return request<T>(path, options);
  }

  if (!response.ok) {
    throw await parseError(response);
  }

  if (response.status === 204 || response.headers.get("content-length") === "0") {
    return undefined as T;
  }

  return response.json() as Promise<T>;
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

export function formatPrice(amount: number): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: "INR",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function normalizePhone(phone: string): string {
  const digits = phone.replace(/\D/g, "");
  if (digits.length === 10) return digits;
  if (digits.length === 12 && digits.startsWith("91")) return digits.slice(2);
  return digits;
}

// ── Server-only fetchers (use in Server Components) ─────────────────────────
// Import from @/lib/api-server instead of here.

// ── Full API client (browser; uses localStorage tokens) ───────────────────────

export const api = {
  auth: {
    requestOtp(phone: string) {
      return request<void>("/auth/otp/request", {
        method: "POST",
        body: { phone: normalizePhone(phone) },
      });
    },
    async verifyOtp(phone: string, otp: string) {
      const tokens = await request<TokenResponse>("/auth/otp/verify", {
        method: "POST",
        body: { phone: normalizePhone(phone), otp },
      });
      tokenStorage.setTokens(tokens.access_token, tokens.refresh_token);
      return tokens;
    },
    async refresh() {
      const refreshToken = tokenStorage.getRefreshToken();
      if (!refreshToken) throw new ApiError(401, "NO_REFRESH", "Not logged in");
      const tokens = await request<TokenResponse>("/auth/refresh", {
        method: "POST",
        body: { refresh_token: refreshToken },
      });
      tokenStorage.setTokens(tokens.access_token, tokens.refresh_token);
      return tokens;
    },
    async logout() {
      const refreshToken = tokenStorage.getRefreshToken();
      if (refreshToken) {
        try {
          await request<void>("/auth/logout", {
            method: "POST",
            body: { refresh_token: refreshToken },
          });
        } catch {
          /* ignore */
        }
      }
      tokenStorage.clearTokens();
    },
    deleteAccount() {
      return request<void>("/auth/account", { method: "DELETE", auth: true });
    },
  },

  users: {
    getMe() {
      return request<UserMe>("/users/me", { auth: true });
    },
    updateMe(data: { display_name?: string | null; email?: string | null; city?: string | null }) {
      return request<UserMe>("/users/me", { method: "PATCH", body: data, auth: true });
    },
    getPublic(id: string) {
      return request<UserPublic>(`/users/${id}`);
    },
    recentlyViewed() {
      return request<RecentlyViewedListResponse>("/users/me/recently-viewed", { auth: true });
    },
    trackListingView(listingId: string) {
      return request<void>(`/listings/${listingId}/view`, { method: "POST", auth: true });
    },
  },

  listings: {
    search(params: SearchListingsParams = {}) {
      return request<ListingListResponse>(
        `/listings${buildQuery(params as Record<string, string | number | undefined>)}`,
        { auth: true },
      );
    },
    get(id: string) {
      return request<Listing>(`/listings/${id}`, { auth: true });
    },
    getMine(params: { page?: number; limit?: number } = {}) {
      return request<ListingListResponse>(
        `/listings/me${buildQuery(params as Record<string, string | number | undefined>)}`,
        { auth: true },
      );
    },
    create(data: ListingCreateInput) {
      return request<Listing>("/listings", { method: "POST", body: data, auth: true });
    },
    update(id: string, data: ListingUpdateInput) {
      return request<Listing>(`/listings/${id}`, { method: "PATCH", body: data, auth: true });
    },
    publish(id: string) {
      return request<Listing>(`/listings/${id}/publish`, { method: "POST", auth: true });
    },
    delete(id: string) {
      return request<void>(`/listings/${id}`, { method: "DELETE", auth: true });
    },
    markSold(id: string) {
      return request<Listing>(`/listings/${id}/sold`, { method: "POST", auth: true });
    },
    presignImage(listingId: string, data: PresignImageRequest) {
      return request<PresignImageResponse>(`/listings/${listingId}/images/presign`, {
        method: "POST",
        body: data,
        auth: true,
      });
    },
    confirmImage(listingId: string, data: ConfirmImageInput) {
      return request<ListingImage>(`/listings/${listingId}/images/confirm`, {
        method: "POST",
        body: data,
        auth: true,
      });
    },
    async uploadImage(listingId: string, file: File, options?: { is_cover?: boolean; sort_order?: number }) {
      const presign = await api.listings.presignImage(listingId, {
        content_type: file.type || "image/jpeg",
        filename: file.name,
      });
      const uploadHeaders: Record<string, string> = { "Content-Type": file.type || "image/jpeg" };
      const uploadResponse = await fetch(presign.upload_url, {
        method: presign.fields ? "POST" : "PUT",
        headers: presign.fields ? undefined : uploadHeaders,
        body: presign.fields
          ? (() => {
              const form = new FormData();
              for (const [k, v] of Object.entries(presign.fields!)) form.append(k, v);
              form.append("file", file);
              return form;
            })()
          : file,
      });
      if (!uploadResponse.ok) {
        throw new ApiError(uploadResponse.status, "UPLOAD_FAILED", "Image upload failed");
      }
      return api.listings.confirmImage(listingId, {
        storage_key: presign.storage_key,
        url: presign.url,
        is_cover: options?.is_cover,
        sort_order: options?.sort_order,
      });
    },
  },

  dealers: {
    create(data: DealerStoreCreateInput) {
      return request<DealerStore>("/dealer-stores", { method: "POST", body: data, auth: true });
    },
    getBySlug(slug: string) {
      return request<DealerStore>(`/dealer-stores/${slug}`, { auth: true });
    },
    updateMine(data: Partial<DealerStoreCreateInput>) {
      return request<DealerStore>("/dealer-stores/me", { method: "PATCH", body: data, auth: true });
    },
    getMyListings(params: { page?: number; limit?: number } = {}) {
      return request<ListingListResponse>(
        `/dealer-stores/me/listings${buildQuery(params as Record<string, string | number | undefined>)}`,
        { auth: true },
      );
    },
  },

  inquiries: {
    create(listingId: string, message: string) {
      return request<Inquiry>(`/listings/${listingId}/inquiries`, {
        method: "POST",
        body: { message },
        auth: true,
      });
    },
    listSent(params: { page?: number; limit?: number } = {}) {
      return request<InquiryListResponse>(
        `/inquiries/sent${buildQuery(params as Record<string, string | number | undefined>)}`,
        { auth: true },
      );
    },
    listInbox(params: { page?: number; limit?: number } = {}) {
      return request<InquiryListResponse>(
        `/inquiries/inbox${buildQuery(params as Record<string, string | number | undefined>)}`,
        { auth: true },
      );
    },
    accept(inquiryId: string) {
      return request<Inquiry>(`/inquiries/${inquiryId}/accept`, {
        method: "PATCH",
        auth: true,
      });
    },
    decline(inquiryId: string) {
      return request<Inquiry>(`/inquiries/${inquiryId}/decline`, {
        method: "PATCH",
        auth: true,
      });
    },
  },

  reviews: {
    list(targetType: ReviewTargetType, targetId: string) {
      return request<Review[]>(
        `/reviews${buildQuery({ target_type: targetType, target_id: targetId })}`,
      );
    },
    create(data: {
      target_type: ReviewTargetType;
      target_id: string;
      rating: number;
      text?: string | null;
    }) {
      return request<Review>("/reviews", { method: "POST", body: data, auth: true });
    },
  },

  favorites: {
    list(params: { page?: number; limit?: number } = {}) {
      return request<Favorite[]>(
        `/favorites${buildQuery(params as Record<string, string | number | undefined>)}`,
        { auth: true },
      );
    },
    add(listingId: string) {
      return request<Favorite>("/favorites", {
        method: "POST",
        body: { listing_id: listingId },
        auth: true,
      });
    },
    remove(listingId: string) {
      return request<void>(`/favorites/${listingId}`, { method: "DELETE", auth: true });
    },
  },

  reports: {
    create(data: ReportCreateInput) {
      return request<{ id: string }>("/reports", { method: "POST", body: data, auth: true });
    },
  },

  moderation: {
    listPending(params: { page?: number; limit?: number } = {}) {
      return request<Listing[]>(
        `/moderation/listings${buildQuery(params as Record<string, string | number | undefined>)}`,
        { auth: true },
      );
    },
    approve(listingId: string) {
      return request<Listing>(`/moderation/listings/${listingId}/approve`, {
        method: "POST",
        auth: true,
      });
    },
    reject(listingId: string, reason: string) {
      return request<Listing>(`/moderation/listings/${listingId}/reject`, {
        method: "POST",
        body: { reason },
        auth: true,
      });
    },
  },

  platform: {
    getSettings() {
      return request<PlatformSettings>("/platform/settings");
    },
  },

  admin: {
    getPlatformSettings() {
      return request<PlatformSettingsAdmin>("/admin/platform-settings", { auth: true });
    },
    updatePlatformSettings(data: Partial<Omit<PlatformSettingsAdmin, "updated_at">>) {
      return request<PlatformSettingsAdmin>("/admin/platform-settings", {
        method: "PATCH",
        body: data,
        auth: true,
      });
    },
    async uploadLogo(file: File) {
      const presign = await request<{ upload_url: string; storage_key: string }>(
        "/admin/platform-settings/logo/presign",
        {
          method: "POST",
          body: { filename: file.name, content_type: file.type || "image/png" },
          auth: true,
        },
      );
      const uploadResponse = await fetch(presign.upload_url, {
        method: "PUT",
        body: file,
        headers: { "Content-Type": file.type || "image/png" },
      });
      if (!uploadResponse.ok) {
        throw new ApiError(uploadResponse.status, "UPLOAD_FAILED", "Logo upload failed");
      }
      return request<PlatformSettingsAdmin>("/admin/platform-settings/logo/confirm", {
        method: "POST",
        body: { storage_key: presign.storage_key },
        auth: true,
      });
    },
  },
};
