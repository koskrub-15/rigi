export function monthBounds(now: Date): [Date, Date] {
  const dateFrom = new Date(now.getFullYear(), now.getMonth(), 1);
  const dateTo = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  return [dateFrom, dateTo];
}

export function previousMonth(now: Date): [year: number, month: number] {
  const prev = new Date(now.getFullYear(), now.getMonth() - 1, 1);
  return [prev.getFullYear(), prev.getMonth() + 1];
}
