import { useState } from "react";
import { Scanner, type IDetectedBarcode } from "@yudiel/react-qr-scanner";

import {
  inputClass,
  buttonClass,
  cardClass,
  secondaryButtonClass,
} from "../styles";

export function ScanPanel({
  onScan,
  sendError,
}: {
  onScan: (scanType: string, code: string) => void;
  sendError: string;
}) {
  const [code, setCode] = useState("");
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState("");

  function handleScan(results: IDetectedBarcode[]) {
    if (results.length === 0) {
      return;
    }
    setCode(results[0].rawValue);
    setScanning(false);
  }

  function handleError() {
    setError("Camera is not available");
    setScanning(false);
  }

  function toggleScanning() {
    setError("");
    setScanning((prev) => !prev);
  }

  const noCode = code.trim() === "";

  return (
    <section className={cardClass}>
      <h2 className="text-lg font-semibold mb-3">Scan</h2>
      <button
        className={`${secondaryButtonClass} w-full mb-3`}
        onClick={toggleScanning}
      >
        {scanning ? "Cancel" : "Scan QR-code"}
      </button>
      {scanning && (
        <Scanner
          onScan={handleScan}
          onError={handleError}
          formats={["qr_code"]}
        />
      )}
      <input
        className={inputClass}
        value={code}
        onChange={(e) => setCode(e.target.value)}
      />
      <div className="flex gap-3 mt-3">
        <button
          className={`${buttonClass} flex-1`}
          disabled={noCode}
          onClick={() => onScan("check_in", code)}
        >
          Check in
        </button>
        <button
          className={`${buttonClass} flex-1`}
          disabled={noCode}
          onClick={() => onScan("check_out", code)}
        >
          Check out
        </button>
      </div>
      {sendError && <p className="text-red-600 text-sm">{sendError}</p>}
      {error && <p className="text-red-600 text-sm">{error}</p>}
    </section>
  );
}
