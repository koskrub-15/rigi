import { test, expect } from "vitest";
import { monthBounds, periodBounds, previousMonth } from "./month";

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

test("previous month", () => {
  expect(previousMonth(new Date(2026, 9, 15))).toEqual([2026, 9]);
});

test("previous month before january", () => {
  expect(previousMonth(new Date(2026, 0, 15))).toEqual([2025, 12]);
});

test("period bounds in the middle of the year", () => {
  const now = new Date(2026, 6, 15);

  expect(periodBounds(1, now)).toEqual([
    new Date(2026, 6, 1),
    new Date(2026, 7, 1),
  ]);
  expect(periodBounds(3, now)).toEqual([
    new Date(2026, 4, 1),
    new Date(2026, 7, 1),
  ]);
  expect(periodBounds(12, now)).toEqual([
    new Date(2026, 0, 1),
    new Date(2026, 7, 1),
  ]);
});

test("last three months crosses into the previous year in january", () => {
  expect(periodBounds(3, new Date(2026, 0, 15))).toEqual([
    new Date(2025, 10, 1),
    new Date(2026, 1, 1),
  ]);
});

test("this year ends at january of the next year in december", () => {
  expect(periodBounds(12, new Date(2026, 11, 15))).toEqual([
    new Date(2026, 0, 1),
    new Date(2027, 0, 1),
  ]);
});
