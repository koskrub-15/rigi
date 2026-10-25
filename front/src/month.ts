export function monthBounds(now: Date): [Date, Date] {
  const dateFrom = new Date(now.getFullYear(), now.getMonth(), 1);
  const dateTo = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  return [dateFrom, dateTo];
}
