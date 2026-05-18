/* @vitest-environment happy-dom */

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import SearchUsers from "./SearchUsers";

describe("SearchUsers", () => {
  beforeEach(() => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve([
            {
              id: 1,
              name: "Alice Zhang",
              year: "Sophomore",
              major: "Computer Science",
              interests: ["Robotics", "AI"],
              joined_clubs: [{ id: 101, name: "Robotics Club" }],
              medal_count: 3,
              event_attendance_count: 12,
            },
          ]),
      } as Response)
    ) as unknown as typeof fetch;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders search results and navigates to user profile link", async () => {
    render(
      <MemoryRouter initialEntries={["/users?search=Alice"]}>
        <Routes>
          <Route path="/users" element={<SearchUsers />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByRole("heading", { name: "Discover users" })).toBeTruthy();
    expect(await screen.findByText("Alice Zhang")).toBeTruthy();
    expect(screen.getByText("Robotics Club")).toBeTruthy();
    expect(screen.getByRole("link", { name: /Alice Zhang/i })).toHaveAttribute("href", "/users/1");
  });

  it("submits a new search query", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve([
            {
              id: 1,
              name: "Alice Zhang",
              year: "Sophomore",
              major: "Computer Science",
              interests: ["Robotics", "AI"],
              joined_clubs: [{ id: 101, name: "Robotics Club" }],
              medal_count: 3,
              event_attendance_count: 12,
            },
          ]),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve([
            {
              id: 2,
              name: "Brandon Lee",
              year: "Junior",
              major: "Psychology",
              interests: ["Debate"],
              joined_clubs: [{ id: 103, name: "Debate Club" }],
              medal_count: 1,
              event_attendance_count: 5,
            },
          ]),
      } as Response);

    global.fetch = fetchMock as unknown as typeof fetch;

    render(
      <MemoryRouter initialEntries={["/users"]}>
        <Routes>
          <Route path="/users" element={<SearchUsers />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText("Alice Zhang")).toBeTruthy();

    const user = userEvent.setup();
    const input = screen.getByRole("searchbox", { name: "Search users" });
    await user.clear(input);
    await user.type(input, "Brandon");
    await user.click(screen.getByRole("button", { name: "Find" }));

    expect(fetchMock).toHaveBeenLastCalledWith("/api/users?search=Brandon", expect.any(Object));
    expect(await screen.findByText("Brandon Lee")).toBeTruthy();
  });
});
