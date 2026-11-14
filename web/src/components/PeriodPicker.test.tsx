import { render, screen } from "@testing-library/react";
import { PeriodPicker } from "./PeriodPicker";
import { expect, test, vi } from "vitest";
import userEvent from "@testing-library/user-event";

test("Active button is marked", () => {
  render(<PeriodPicker value={1} onChange={() => {}} />);
  const selectedButton = screen.getByRole("button", {
    name: "This month",
  });
  expect(selectedButton).toHaveAttribute("aria-pressed", "true");
  expect(screen.getByRole("button", { name: "Last 3 months" })).toHaveAttribute(
    "aria-pressed",
    "false",
  );

  expect(screen.getByRole("button", { name: "This year" })).toHaveAttribute(
    "aria-pressed",
    "false",
  );
});

test("calls onChange with 12 when This year is clicked", async () => {
  const onChange = vi.fn();

  render(<PeriodPicker value={1} onChange={onChange} />);

  await userEvent.click(screen.getByRole("button", { name: "This year" }));

  expect(onChange).toHaveBeenCalledWith(12);
});
