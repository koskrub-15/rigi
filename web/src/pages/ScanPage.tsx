import { useState, useEffect } from "react";
import { apiFetch } from "../api";
import { ScanPanel } from "../components/ScanPanel";
import type { OpenedTrip } from "../types";
import { CurrentTrip } from "../components/CurrentTrip";
import { TIME_FORMAT } from "../format";

export function ScanPage({ onLogout }: { onLogout: () => void }) {
  const [error, setError] = useState("");
  const [openedTrip, setOpenedTrip] = useState<OpenedTrip | null | undefined>(
    undefined,
  );
  const [confirmation, setConfirmation] = useState("");

  async function scan(scanType: string, code: string) {
    setError("");
    setConfirmation("");
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
        return false;
      }
      const data = await response.json();
      setError(
        typeof data.detail === "string" ? data.detail : "Invalid QR code",
      );
      return false;
    }
    const data = await response.json();
    await loadCurrentTrip();
    const checkType =
      data.scan_type === "check_in" ? "Checked in" : "Checked out";
    const scanTime = new Date(data.timestamp + "Z").toLocaleTimeString(
      undefined,
      TIME_FORMAT,
    );
    setConfirmation(`${checkType} · Zone ${data.zone} · ${scanTime}`);
    return true;
  }
  async function loadCurrentTrip() {
    const tripResponse = await apiFetch(`/trips/current`);
    if (!tripResponse.ok) {
      if (tripResponse.status === 401) {
        onLogout();
      }
      return;
    }
    const tripData = await tripResponse.json();
    setOpenedTrip(tripData);
  }

  useEffect(() => {
    loadCurrentTrip();
  }, []);

  return (
    <div className="flex flex-col gap-4">
      <CurrentTrip trip={openedTrip} />
      <ScanPanel onScan={scan} sendError={error} confirmation={confirmation} />
    </div>
  );
}
