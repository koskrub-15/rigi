export type Trip = {
  start: string;
  end: string;
  from_zone: string;
  to_zone: string;
  zones: number;
  forgotten: boolean;
};

export type Ticket = {
  type: string;
  valid_from: string;
  price: number;
};

export type Bill = {
  tickets: Ticket[];
  total: number;
  currency: string;
};

export type PerDay = {
  day: string;
  trips: number;
};

export type Stats = {
  trips_count: number;
  paid: number;
  singles_price: number;
  per_day: PerDay[];
  currency: string;
};

export type ClosedBill = Bill & {
  id: number;
  year: number;
  month: number;
  closed_at: string;
  paid_at: string | null;
};
