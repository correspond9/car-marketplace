"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, tokenStorage, type UserMe } from "@/lib/api";
import { syncAuthCookiesFromStorage } from "@/lib/auth-cookie";

type AuthContextValue = {
  user: UserMe | null;
  loading: boolean;
  isLoggedIn: boolean;
  refreshUser: () => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserMe | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    if (!tokenStorage.isLoggedIn()) {
      setUser(null);
      return;
    }
    syncAuthCookiesFromStorage(() => tokenStorage.getAccessToken());
    try {
      const me = await api.users.getMe();
      setUser(me);
      syncAuthCookiesFromStorage(() => tokenStorage.getAccessToken());
    } catch {
      tokenStorage.clearTokens();
      setUser(null);
    }
  }, []);

  useEffect(() => {
    refreshUser().finally(() => setLoading(false));
  }, [refreshUser]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    syncAuthCookiesFromStorage(() => tokenStorage.getAccessToken());
  }, []);

  const logout = useCallback(async () => {
    await api.auth.logout();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      loading,
      isLoggedIn: !!user,
      refreshUser,
      logout,
    }),
    [user, loading, refreshUser, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
