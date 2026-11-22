import { act, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { apiFetch } from "../api";
import { ClosedBills } from "./ClosedBills";

vi.mock("../api", () => ({
  apiFetch: vi.fn(),
}));

const mockFetch = vi.mocked(apiFetch);

beforeEach(() => {
  mockFetch.mockReset();
  vi.useFakeTimers({ toFake: ["Date"] });
  vi.setSystemTime(new Date(2026, 10, 22));
});

afterEach(() => {
  vi.useRealTimers();
});

test("hides the close button when the previous month is already closed", async () => {
  mockFetch.mockImplementation(async () =>
    Response.json([
      {
        id: 1,
        year: 2026,
        month: 10,
        tickets: [],
        total: 0,
        currency: "EUR",
        closed_at: "2026-11-01T00:00:00",
        paid_at: null,
      },
    ]),
  );

  render(<ClosedBills onLogout={vi.fn()} />);

  await screen.findByText("Nothing to pay");
  expect(screen.queryByRole("button", { name: "Close 2026-10" })).toBeNull();
});

test("shows the close button when the previous month is not closed", async () => {
  let resolveBills: (response: Response) => void = () => {};
  mockFetch.mockImplementation(
    () =>
      new Promise((resolve) => {
        resolveBills = resolve;
      }),
  );

  render(<ClosedBills onLogout={vi.fn()} />);

  expect(screen.queryByRole("button", { name: "Close 2026-10" })).toBeNull();
  await act(async () =>
    resolveBills(
      Response.json([
        {
          id: 1,
          year: 2026,
          month: 9,
          tickets: [],
          total: 0,
          currency: "EUR",
          closed_at: "2026-10-01T00:00:00",
          paid_at: null,
        },
      ]),
    ),
  );
  await screen.findByText("Nothing to pay");
  expect(
    screen.getByRole("button", { name: "Close 2026-10" }),
  ).toBeInTheDocument();
});
