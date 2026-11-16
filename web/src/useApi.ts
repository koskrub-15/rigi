import { useEffect, useState } from "react";
import { apiFetch } from "./api";

export function useApi<T>(
  path: string,
  onLogout: () => void,
): {
  data: T | null;
  error: string;
} {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    setData(null);
    setError("");

    async function run() {
      try {
        const response = await apiFetch(path);

        if (!response.ok) {
          if (response.status === 401) {
            onLogout();
          } else {
            setError("Could not load");
          }

          return;
        }

        const result = (await response.json()) as T;
        setData(result);
      } catch {
        setError("Could not load");
      }
    }
    run();
  }, [path]);
  return { data, error };
}
