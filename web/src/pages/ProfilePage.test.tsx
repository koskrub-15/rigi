import userEvent from "@testing-library/user-event";
import { act, render, screen } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";

import { apiFetch } from "../api";
import type { Stats, Trip } from "../types";
import { ProfilePage } from "./ProfilePage";

vi.mock("../api", () => ({
  apiFetch: vi.fn(),
}));

const mockFetch = vi.mocked(apiFetch);

beforeEach(() => {
  mockFetch.mockReset();
});

const emptyStats: Stats = {
  trips_count: 0,
  paid: 0,
  singles_price: 0,
  per_day: [],
  currency: "EUR",
};

test("loads trips and statistics", async () => {
  mockFetch
    .mockResolvedValueOnce(Response.json([]))
    .mockResolvedValueOnce(Response.json(emptyStats));

  render(<ProfilePage onLogout={vi.fn()} />);

  await screen.findByText("There are no trips yet");
  await screen.findByText("No trips in this period");
  expect(mockFetch).toHaveBeenNthCalledWith(
    1,
    expect.stringMatching(/^\/trips\?/),
  );
  expect(mockFetch).toHaveBeenNthCalledWith(
    2,
    expect.stringMatching(/^\/stats\?/),
  );
});

test("reloads trips when the period changes", async () => {
  const trip: Trip = {
    start: "2026-11-03T08:00:00",
    end: "2026-11-03T08:30:00",
    from_zone: "A",
    to_zone: "B",
    zones: 2,
    forgotten: false,
  };
  mockFetch
    .mockResolvedValueOnce(Response.json([]))
    .mockResolvedValueOnce(Response.json(emptyStats))
    .mockResolvedValueOnce(Response.json([trip]))
    .mockResolvedValueOnce(Response.json(emptyStats));

  const user = userEvent.setup();
  render(<ProfilePage onLogout={vi.fn()} />);

  await screen.findByText("There are no trips yet");
  await screen.findByText("No trips in this period");
  const firstTripsRequest = mockFetch.mock.calls[0][0];

  await user.click(screen.getByRole("button", { name: "Last 3 months" }));
  await screen.findByText("A → B");

  expect(mockFetch).toHaveBeenCalledTimes(4);
  expect(mockFetch.mock.calls[2][0]).not.toBe(firstTripsRequest);
});

test("shows trips in reverse order", async () => {
  const firstTrip: Trip = {
    start: "2026-11-03T08:00:00",
    end: "2026-11-03T08:30:00",
    from_zone: "A",
    to_zone: "B",
    zones: 2,
    forgotten: false,
  };
  const secondTrip: Trip = {
    start: "2026-11-04T08:00:00",
    end: "2026-11-04T08:30:00",
    from_zone: "B",
    to_zone: "C",
    zones: 2,
    forgotten: false,
  };
  mockFetch
    .mockResolvedValueOnce(Response.json([firstTrip, secondTrip]))
    .mockResolvedValueOnce(Response.json(emptyStats));

  render(<ProfilePage onLogout={vi.fn()} />);

  await screen.findByText("B → C");

  expect(
    screen.getAllByText(/ → /).map((element) => element.textContent),
  ).toEqual(["B → C", "A → B"]);
});

test("shows error when trips request fails", async () => {
  mockFetch
    .mockResolvedValueOnce(Response.json({}, { status: 500 }))
    .mockResolvedValueOnce(Response.json(emptyStats));

  render(<ProfilePage onLogout={vi.fn()} />);

  await screen.findByText("Could not load");
});

test("ignores stale trips response", async () => {
  let resolveSlow!: (r: Response) => void;
  const slow = new Promise<Response>((resolve) => {
    resolveSlow = resolve;
  });
  const tripAB: Trip = {
    start: "2026-11-03T08:00:00",
    end: "2026-11-03T08:30:00",
    from_zone: "A",
    to_zone: "B",
    zones: 2,
    forgotten: false,
  };
  const tripBC: Trip = {
    start: "2026-11-04T08:00:00",
    end: "2026-11-04T08:30:00",
    from_zone: "B",
    to_zone: "C",
    zones: 2,
    forgotten: false,
  };
  mockFetch
    .mockReturnValueOnce(slow)
    .mockResolvedValueOnce(Response.json(emptyStats))
    .mockResolvedValueOnce(Response.json([tripBC]))
    .mockResolvedValueOnce(Response.json(emptyStats));

  const user = userEvent.setup();
  render(<ProfilePage onLogout={vi.fn()} />);

  await user.click(screen.getByRole("button", { name: "Last 3 months" }));
  await screen.findByText("B → C");

  await act(async () => {
    resolveSlow(Response.json([tripAB]));
  });
  expect(screen.getByText("B → C")).toBeInTheDocument();

  expect(screen.queryByText("A → B")).not.toBeInTheDocument();
  expect(mockFetch).toHaveBeenCalledTimes(4);
});

test("ignores stale trips error", async () => {
  let rejectSlow!: (reason?: unknown) => void;
  const slow = new Promise<Response>((_, reject) => {
    rejectSlow = reject;
  });

  let resolveFresh!: (response: Response) => void;
  const fresh = new Promise<Response>((resolve) => {
    resolveFresh = resolve;
  });

  const tripBC: Trip = {
    start: "2026-11-04T08:00:00",
    end: "2026-11-04T08:30:00",
    from_zone: "B",
    to_zone: "C",
    zones: 2,
    forgotten: false,
  };

  mockFetch
    .mockReturnValueOnce(slow)
    .mockResolvedValueOnce(Response.json(emptyStats))
    .mockReturnValueOnce(fresh)
    .mockResolvedValueOnce(Response.json(emptyStats));

  const user = userEvent.setup();
  render(<ProfilePage onLogout={vi.fn()} />);

  await user.click(screen.getByRole("button", { name: "Last 3 months" }));

  await act(async () => {
    rejectSlow(new TypeError("Failed to fetch"));
  });
  expect(screen.queryByText("Could not load")).not.toBeInTheDocument();

  await act(async () => {
    resolveFresh(Response.json([tripBC]));
  });

  await screen.findByText("B → C");
  expect(screen.getByText("B → C")).toBeInTheDocument();
  expect(screen.queryByText("Could not load")).not.toBeInTheDocument();
});
