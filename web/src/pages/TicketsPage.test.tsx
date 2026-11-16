import { render, screen } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";

import { apiFetch } from "../api";
import { TicketsPage } from "./TicketsPage";

vi.mock("../api", () => ({
  apiFetch: vi.fn(),
}));

const mockFetch = vi.mocked(apiFetch);

beforeEach(() => {
  mockFetch.mockReset();
});

test("shows the current bill and empty closed bills state", async () => {
  mockFetch.mockImplementation(async (path) => {
    if (path.startsWith("/bills/preview")) {
      return Response.json({
        tickets: [
          {
            type: "day_ticket",
            valid_from: "2026-11-03T00:00:00",
            price: 9.4,
          },
        ],
        total: 9.4,
        currency: "EUR",
      });
    }
    return Response.json([]);
  });

  render(<TicketsPage onLogout={vi.fn()} />);

  await screen.findByText("Day ticket");
  await screen.findByText("No closed bills yet");
});

test("calls onLogout once when preview returns 401", async () => {
  const onLogout = vi.fn();
  mockFetch.mockImplementation(async (path) => {
    if (path.startsWith("/bills/preview")) {
      return Response.json({}, { status: 401 });
    }
    return Response.json([]);
  });

  render(<TicketsPage onLogout={onLogout} />);

  await vi.waitFor(() => {
    expect(onLogout).toHaveBeenCalledOnce();
  });
});
