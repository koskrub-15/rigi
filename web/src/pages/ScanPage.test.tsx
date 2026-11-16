import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/react";
import { beforeEach, expect, test, vi } from "vitest";

import { apiFetch } from "../api";
import { ScanPage } from "./ScanPage";

vi.mock("../api", () => ({
  apiFetch: vi.fn(),
}));

const mockFetch = vi.mocked(apiFetch);

beforeEach(() => {
  mockFetch.mockReset();
});

test("shows loading state", () => {
  mockFetch.mockReturnValueOnce(new Promise(() => {}));

  render(<ScanPage onLogout={vi.fn()} />);

  expect(screen.getByText("Loading…")).toBeInTheDocument();
});

test("successfully checks in and loads current trip", async () => {
  mockFetch
    .mockResolvedValueOnce(Response.json(null))
    .mockResolvedValueOnce(
      Response.json({
        scan_type: "check_in",
        zone: "A",
        timestamp: "2026-11-16T08:15:00",
      }),
    )
    .mockResolvedValueOnce(
      Response.json({
        start: "2026-11-16T08:15:00",
        from_zone: "A",
      }),
    );
  const user = userEvent.setup();
  render(<ScanPage onLogout={vi.fn()} />);
  await user.type(screen.getByRole("textbox"), "zone-code");
  await user.click(screen.getByRole("button", { name: "Check in" }));
  await screen.findByText(/Checked in · Zone A/);
  expect(screen.getByRole("textbox")).toHaveValue("");
  await screen.findByText(/On a trip since/);
  expect(mockFetch).toHaveBeenNthCalledWith(
    2,
    "/scans",
    expect.objectContaining({
      method: "POST",
    }),
  );
  expect(mockFetch).toHaveBeenCalledTimes(3);
});

test("shows error for invalid QR code", async () => {
  mockFetch
    .mockResolvedValueOnce(Response.json(null))
    .mockResolvedValueOnce(
      Response.json({ detail: "Invalid QR code signature" }, { status: 422 }),
    );

  const user = userEvent.setup();

  render(<ScanPage onLogout={vi.fn()} />);

  const input = screen.getByRole("textbox");

  await user.type(input, "invalid-code");

  await user.click(screen.getByRole("button", { name: "Check in" }));

  expect(
    await screen.findByText(/Invalid QR code signature/),
  ).toBeInTheDocument();

  expect(input).toHaveValue("invalid-code");
});

test("calls onLogout when loading returns 401", async () => {
  const onLogout = vi.fn();

  mockFetch.mockResolvedValueOnce(Response.json({}, { status: 401 }));

  render(<ScanPage onLogout={onLogout} />);

  await vi.waitFor(() => {
    expect(onLogout).toHaveBeenCalledOnce();
  });
});

test("shows fallback error when detail is not a string", async () => {
  mockFetch
    .mockResolvedValueOnce(Response.json(null))
    .mockResolvedValueOnce(
      Response.json({ detail: ["Field required"] }, { status: 422 }),
    );

  const user = userEvent.setup();

  render(<ScanPage onLogout={vi.fn()} />);

  await user.type(screen.getByRole("textbox"), "invalid-code");

  await user.click(screen.getByRole("button", { name: "Check in" }));

  await screen.findByText("Invalid QR code");
});
