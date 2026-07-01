"use client";

const COMPARE_KEY = "cm_compare_ids";
export const MAX_COMPARE = 4;

export function getCompareIds(): string[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = sessionStorage.getItem(COMPARE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as string[];
    return Array.isArray(parsed) ? parsed.slice(0, MAX_COMPARE) : [];
  } catch {
    return [];
  }
}

export function setCompareIds(ids: string[]): void {
  if (typeof window === "undefined") return;
  sessionStorage.setItem(COMPARE_KEY, JSON.stringify(ids.slice(0, MAX_COMPARE)));
}

export function addToCompare(id: string): string[] {
  const current = getCompareIds().filter((x) => x !== id);
  const next = [id, ...current].slice(0, MAX_COMPARE);
  setCompareIds(next);
  return next;
}

export function removeFromCompare(id: string): string[] {
  const next = getCompareIds().filter((x) => x !== id);
  setCompareIds(next);
  return next;
}

export function compareQueryString(ids: string[]): string {
  return ids.length ? `?ids=${ids.join(",")}` : "";
}
