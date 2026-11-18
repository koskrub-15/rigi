import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";

import { MemoryRouter } from "react-router";

import { LoginPage } from "./LoginPage";

const fetchMock = vi.fn<typeof fetch>();

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
  localStorage.clear();
});

afterEach(() => {
  vi.unstubAllGlobals();
});

test("successful login", async () => {
  fetchMock.mockResolvedValue(
    Response.json({
      access_token: "a1",
      refresh_token: "r1",
    }),
  );

  const onLogin = vi.fn();
  const user = userEvent.setup();

  render(
    <MemoryRouter>
      <LoginPage onLogin={onLogin} />
    </MemoryRouter>,
  );

  await user.type(screen.getByPlaceholderText("Email"), "test@example.com");
  await user.type(screen.getByPlaceholderText("Password"), "password123");
  await user.click(screen.getByRole("button", { name: /submit/i }));

  await vi.waitFor(() => {
    expect(onLogin).toHaveBeenCalledWith("a1");
  });

  expect(fetchMock.mock.calls[0][0]).toMatch(/\/auth\/login$/);
  expect(String(fetchMock.mock.calls[0][1]?.body)).toBe(
    "username=test%40example.com&password=password123",
  );
  expect(localStorage.getItem("access_token")).toBe("a1");
  expect(localStorage.getItem("refresh_token")).toBe("r1");
});

test("invalid credentials", async () => {
  fetchMock.mockResolvedValue(Response.json({}, { status: 401 }));
  const onLogin = vi.fn();
  const user = userEvent.setup();

  render(
    <MemoryRouter>
      <LoginPage onLogin={onLogin} />
    </MemoryRouter>,
  );

  await user.type(screen.getByPlaceholderText("Email"), "test@example.com");
  await user.type(screen.getByPlaceholderText("Password"), "password123");
  await user.click(screen.getByRole("button", { name: /submit/i }));
  await screen.findByText("incorrect password or email");
  expect(onLogin).not.toHaveBeenCalled();
  expect(localStorage.getItem("access_token")).toBeNull();
});
