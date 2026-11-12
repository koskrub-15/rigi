export const TICKET_NAMES: Record<string, string> = {
  single_ticket: "Single ticket",
  day_ticket: "Day ticket",
  weekly_ticket: "Weekly ticket",
};
export const TIME_FORMAT = { hour: "2-digit", minute: "2-digit" } as const;

export function formatMoney(amount: number, currency: string): string {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
  }).format(amount);
}
