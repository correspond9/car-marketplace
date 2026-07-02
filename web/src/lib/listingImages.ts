/** Royalty-free demo photos from /public/listings (Media folder). */

export const DEFAULT_LOGO_URL = "/brand/logo.png";

/** [standard image, second image with "2" in the filename] */
const CAR_IMAGE_PAIRS: Record<string, [string, string]> = {
  "maruti|swift": ["/listings/maruti-swift.jpeg", "/listings/maruti-swift2.jpg"],
  "hyundai|creta": ["/listings/hyundai-creta.jpg", "/listings/hyundai-creta2.jpg"],
  "tata|nexon": ["/listings/tata-nexon.jpg", "/listings/tata-nexon2.jpg"],
};

function norm(value: string): string {
  return value.trim().toLowerCase();
}

function carKey(make: string, model: string): string {
  return `${norm(make)}|${norm(model)}`;
}

/** Local MinIO URLs are not publicly readable in dev — use bundled /public/listings photos instead. */
export function isLocalDevStorageUrl(url: string | null | undefined): boolean {
  if (!url) return false;
  try {
    const { hostname, port } = new URL(url);
    return (hostname === "localhost" || hostname === "127.0.0.1") && port === "9000";
  } catch {
    return false;
  }
}

export function resolveBrandLogoUrl(logoUrl: string | null | undefined): string {
  if (logoUrl && !isLocalDevStorageUrl(logoUrl)) return logoUrl;
  return DEFAULT_LOGO_URL;
}

export function resolveListingImageSrc(
  apiUrl: string | null | undefined,
  fallback: string | null,
): string | null {
  if (fallback && (!apiUrl || isLocalDevStorageUrl(apiUrl))) return fallback;
  return apiUrl ?? fallback;
}

/** Assign slot 0/1 as listings appear in a list (first Swift → image 1, second → image 2). */
export function buildListingImageSlots(listings: Array<{ id: string; make: string; model: string }>) {
  const seen = new Map<string, number>();
  const slots = new Map<string, number>();
  for (const listing of listings) {
    const key = carKey(listing.make, listing.model);
    const slot = seen.get(key) ?? 0;
    seen.set(key, slot + 1);
    slots.set(listing.id, slot);
  }
  return slots;
}

export function getListingFallbackImage(
  make: string,
  model: string,
  imageSlot = 0,
): string | null {
  const pair = CAR_IMAGE_PAIRS[carKey(make, model)];
  if (!pair) return null;
  return pair[imageSlot % 2];
}

/** Detail pages: the "2" image goes with the second variant in our sample data. */
export function imageSlotFromVariant(make: string, model: string, variant?: string | null): number {
  const v = norm(variant ?? "");
  const key = carKey(make, model);
  if (key === "maruti|swift" && v === "zxi") return 1;
  if (key === "hyundai|creta" && v.includes("sx(o)")) return 1;
  if (key === "tata|nexon" && v === "ev max") return 1;
  return 0;
}
