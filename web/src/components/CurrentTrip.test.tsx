import { render, screen } from "@testing-library/react";
import { CurrentTrip } from "./CurrentTrip";
import type { OpenedTrip } from "../types";
import { expect, test } from "vitest";

test("renders empty current trip", () => {
  render(<CurrentTrip trip={null} />);

  expect(screen.getByText("Not on a trip")).toBeInTheDocument();
});

test("renders loading state", () => {
  render(<CurrentTrip trip={undefined} />);

  expect(screen.getByText("Loading…")).toBeInTheDocument();
});
test("renders current trip", () => {
  const trip: OpenedTrip = { start: "2026-11-14T20:50:58", from_zone: "A" };
  render(<CurrentTrip trip={trip} />);
  const tripElement = screen.getByText(/On a trip since/);
  expect(tripElement).toHaveTextContent("Zone A");
  expect(tripElement).not.toHaveTextContent("Invalid Date");
  expect(screen.queryByText("Not on a trip")).not.toBeInTheDocument();
});
