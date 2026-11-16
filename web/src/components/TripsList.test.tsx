import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";
import { TripsList } from "./TripsList";
import type { Trip } from "../types";
import userEvent from "@testing-library/user-event";

const trips: Trip[] = [
  {
    start: "2026-10-01T08:09:00",
    end: "2026-10-01T08:34:00",
    from_zone: "D",
    to_zone: "A",
    zones: 3,
    forgotten: false,
  },
  {
    start: "2026-10-01T17:04:00",
    end: "2026-10-01T17:29:00",
    from_zone: "E",
    to_zone: "A",
    zones: 3,
    forgotten: false,
  },
  {
    start: "2026-10-02T08:03:00",
    end: "2026-10-02T08:28:00",
    from_zone: "E",
    to_zone: "B",
    zones: 4,
    forgotten: false,
  },
  {
    start: "2026-10-02T17:02:00",
    end: "2026-10-02T17:27:00",
    from_zone: "A",
    to_zone: "D",
    zones: 3,
    forgotten: false,
  },
  {
    start: "2026-10-03T08:15:00",
    end: "2026-10-03T08:40:00",
    from_zone: "A",
    to_zone: "E",
    zones: 3,
    forgotten: false,
  },
  {
    start: "2026-10-03T17:27:00",
    end: "2026-10-03T17:52:00",
    from_zone: "A",
    to_zone: "E",
    zones: 3,
    forgotten: false,
  },
];
test("renders empty trips list", () => {
  render(<TripsList trips={[]} />);
  expect(screen.getByText("There are no trips yet")).toBeInTheDocument();
});

test("shows five trips and a Show all button", () => {
  render(<TripsList trips={trips} />);
  expect(screen.getAllByRole("listitem")).toHaveLength(5);
  expect(
    screen.getByRole("button", { name: "Show all (6)" }),
  ).toBeInTheDocument();
});

test("renders five trips and expands to six", async () => {
  render(<TripsList trips={trips} />);
  await userEvent.click(screen.getByRole("button", { name: "Show all (6)" }));
  expect(screen.getAllByRole("listitem")).toHaveLength(6);
  expect(screen.getByRole("button", { name: "Show less" })).toBeInTheDocument();
});

test("renders forgotten badge", () => {
  const forgottenTrip: Trip = {
    start: "2026-11-13T19:10:09.561000",
    end: "2026-11-13T22:10:09.561000",
    from_zone: "C",
    to_zone: "F",
    zones: 3,
    forgotten: true,
  };
  render(<TripsList trips={[forgottenTrip]} />);
  expect(screen.getByText("forgotten")).toBeInTheDocument();
});
