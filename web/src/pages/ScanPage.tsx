import { useState } from "react";
import { apiFetch } from "../api";
import { ScanPanel } from "../components/ScanPanel";

export function ScanPage({ onLogout }: { onLogout: () => void }) {
  const [error, setError] = useState("");

  async function scan(scanType: string, code: string) {
    setError("");
    const response = await apiFetch(`/scans`, {
      headers: { "Content-Type": "application/json" },
      method: "POST",
      body: JSON.stringify({
        scan_type: scanType,
        timestamp: new Date().toISOString(),
        code: code,
      }),
    });
    if (!response.ok) {
      if (response.status === 401) {
        onLogout();
        return;
      }
      const data = await response.json();
      setError(
        typeof data.detail === "string" ? data.detail : "Invalid QR code",
      );
      return;
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <ScanPanel onScan={scan} sendError={error} />
    </div>
  );
}
