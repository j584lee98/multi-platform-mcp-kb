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
    <div>
      <h1>Home</h1>
      <p>Welcome, {user}!</p>
      <p>This is a placeholder home page.</p>
      <button onClick={handleLogout}>Logout</button>
    </div>
  );
}
