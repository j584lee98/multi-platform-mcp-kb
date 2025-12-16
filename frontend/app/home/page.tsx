"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const [user, setUser] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    const auth = localStorage.getItem("auth");
    if (!auth) {
      router.push("/login");
      return;
    }

    // Decode username from stored auth
    const decoded = atob(auth);
    const username = decoded.split(":")[0];
    setUser(username);
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem("auth");
    router.push("/login");
  };

  if (!user) {
    return <p>Loading...</p>;
  }

  return (
    <div className="page-container">
      <div className="card text-center">
        <h1>Home</h1>
        <p className="text-lg mb-6">Welcome, <span className="font-semibold">{user}</span>!</p>
        <p className="text-[var(--color-text-muted)] mb-8">This is a placeholder home page.</p>
        <button onClick={handleLogout} className="bg-red-500 hover:bg-red-600">Logout</button>
      </div>
    </div>
  );
}
