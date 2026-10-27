import { test, expect } from "vitest";
import { monthBounds } from "./month";

test("middle of october", () => {
  expect(monthBounds(new Date(2026, 9, 15))).toEqual([
    new Date(2026, 9, 1),
    new Date(2026, 10, 1),
  ]);
});

test("middle of december", () => {
  expect(monthBounds(new Date(2026, 11, 15))).toEqual([
    new Date(2026, 11, 1),
    new Date(2027, 0, 1),
  ]);
});
