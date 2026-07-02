"use client";

import { useEffect } from "react";
import { useAuth } from "@/components/AuthProvider";
import { api } from "@/lib/api";

type Props = {
  listingId: string;
};

export function TrackListingView({ listingId }: Props) {
  const { isLoggedIn } = useAuth();

  useEffect(() => {
    if (!isLoggedIn) return;
    api.users.trackListingView(listingId).catch(() => {
      // Non-blocking analytics-style tracking
    });
  }, [isLoggedIn, listingId]);

  return null;
}
