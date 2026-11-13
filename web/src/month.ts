import type { Period } from "./types";

export function monthBounds(now: Date): [Date, Date] {
  const dateFrom = new Date(now.getFullYear(), now.getMonth(), 1);
  const dateTo = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  return [dateFrom, dateTo];
}

export function previousMonth(now: Date): [year: number, month: number] {
  const prev = new Date(now.getFullYear(), now.getMonth() - 1, 1);
  return [prev.getFullYear(), prev.getMonth() + 1];
}

export function periodBounds(period: Period, now: Date): [Date, Date] {
  const [, dateTo] = monthBounds(now);
  const dateFrom =
    period === 12
      ? new Date(now.getFullYear(), 0, 1)
      : new Date(now.getFullYear(), now.getMonth() - period + 1, 1);

  return [dateFrom, dateTo];
}
