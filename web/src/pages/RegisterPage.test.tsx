import userEvent from "@testing-library/user-event";
import { render, screen } from "@testing-library/react";
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { MemoryRouter, Route, Routes } from "react-router";

import { RegisterPage } from "./RegisterPage";

const fetchMock = vi.fn<typeof fetch>();

beforeEach(() => {
  fetchMock.mockReset();
  vi.stubGlobal("fetch", fetchMock);
});

afterEach(() => {
  vi.unstubAllGlobals();
});

async function fillAndSubmit(password: string) {
  const user = userEvent.setup();

  render(
    <MemoryRouter initialEntries={["/register"]}>
      <Routes>
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/login" element={<p>Login screen</p>} />
      </Routes>
    </MemoryRouter>,
  );

  await user.type(screen.getByPlaceholderText("Email"), "test@example.com");
  await user.type(screen.getByPlaceholderText("First name"), "Kolya");
  await user.type(screen.getByPlaceholderText("Last name"), "Examplovich");
  await user.type(screen.getByPlaceholderText("Password"), password);
  await user.click(screen.getByRole("button", { name: /submit/i }));
}

test("successful register", async () => {
  fetchMock.mockResolvedValue(Response.json({}, { status: 201 }));

  await fillAndSubmit("password123");

  expect(JSON.parse(String(fetchMock.mock.calls[0][1]?.body))).toEqual({
    email: "test@example.com",
    first_name: "Kolya",
    last_name: "Examplovich",
    password: "password123",
  });

  expect(fetchMock.mock.calls[0][0]).toMatch(/\/auth\/register$/);
  expect(await screen.findByText("Login screen")).toBeInTheDocument();
});

test("email is already taken", async () => {
  fetchMock.mockResolvedValue(Response.json({}, { status: 409 }));

  await fillAndSubmit("password123");

  await screen.findByText("this email is already registered");
  expect(screen.getByRole("heading", { name: "Sign up" })).toBeInTheDocument();
  expect(screen.queryByText("Login screen")).not.toBeInTheDocument();
});

test("invalid input", async () => {
  fetchMock.mockResolvedValue(Response.json({}, { status: 422 }));

  await fillAndSubmit("password");

  await screen.findByText(/Password must be at least 8 characters/);
  expect(screen.getByRole("heading", { name: "Sign up" })).toBeInTheDocument();
  expect(screen.queryByText("Login screen")).not.toBeInTheDocument();
});

test("shows a generic error on a server error", async () => {
  fetchMock.mockResolvedValue(Response.json({}, { status: 500 }));

  await fillAndSubmit("password");

  await screen.findByText("Something went wrong, try again");
  expect(screen.getByRole("heading", { name: "Sign up" })).toBeInTheDocument();
  expect(screen.queryByText("Login screen")).not.toBeInTheDocument();
});

test("shows a generic error when offline", async () => {
  fetchMock.mockRejectedValue(new TypeError("Failed to fetch"));

  await fillAndSubmit("password123");

  await screen.findByText("Something went wrong, try again");
  expect(screen.getByRole("heading", { name: "Sign up" })).toBeInTheDocument();
  expect(screen.queryByText("Login screen")).not.toBeInTheDocument();
});
