"use client";

import { useEffect, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";

function getUsernameFromStoredAuth(): string | null {
  if (typeof window === "undefined") return null;

  const auth = localStorage.getItem("auth");
  if (!auth) return null;

  try {
    const decoded = atob(auth);
    const username = decoded.split(":")[0];
    return username || null;
  } catch {
    return null;
  }
}

function subscribeToAuthChanges(onStoreChange: () => void): () => void {
  if (typeof window === "undefined") return () => {};

  window.addEventListener("storage", onStoreChange);
  window.addEventListener("auth", onStoreChange as EventListener);

  return () => {
    window.removeEventListener("storage", onStoreChange);
    window.removeEventListener("auth", onStoreChange as EventListener);
  };
}

export default function HomePage() {
  const router = useRouter();
  const user = useSyncExternalStore(
    subscribeToAuthChanges,
    getUsernameFromStoredAuth,
    () => null
  );
  const isHydrated = useSyncExternalStore(
    subscribeToAuthChanges,
    () => true,
    () => false
  );

  useEffect(() => {
    if (!isHydrated) return;

    if (!user) {
      router.replace("/login");
    }
  }, [isHydrated, router, user]);

  if (!user) {
    return <p>Loading...</p>;
  }

  return (
    <div className="page-container">
      {/* Blank Home Page */}
    </div>
  );
}

