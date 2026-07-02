"use client";

import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, type PlatformSettings } from "@/lib/api";
import { DEFAULT_LOGO_URL, resolveBrandLogoUrl } from "@/lib/listingImages";

const DEFAULT_BRAND: PlatformSettings = {
  brand_name: "Car-Market",
  brand_domain: "carmarket.in",
  logo_url: DEFAULT_LOGO_URL,
};

type BrandContextValue = PlatformSettings & { loading: boolean };

const BrandContext = createContext<BrandContextValue>({ ...DEFAULT_BRAND, loading: true });

export function BrandProvider({ children }: { children: ReactNode }) {
  const [brand, setBrand] = useState<PlatformSettings>(DEFAULT_BRAND);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.platform
      .getSettings()
      .then((settings) =>
        setBrand({
          ...DEFAULT_BRAND,
          ...settings,
          logo_url: resolveBrandLogoUrl(settings.logo_url),
        }),
      )
      .catch(() => setBrand(DEFAULT_BRAND))
      .finally(() => setLoading(false));
  }, []);

  return <BrandContext.Provider value={{ ...brand, loading }}>{children}</BrandContext.Provider>;
}

export function useBrand() {
  return useContext(BrandContext);
}
