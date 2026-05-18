/* @vitest-environment happy-dom */

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import UserProfile from "./UserProfile";

describe("UserProfile", () => {
  beforeEach(() => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve({
            id: 1,
            name: "Alice Zhang",
            year: "Sophomore",
            major: "Computer Science",
            interests: ["Robotics", "AI"],
            joined_clubs: [
              { id: 101, name: "Robotics Club" },
              { id: 102, name: "AI Society" },
            ],
            medal_count: 3,
            event_attendance_count: 12,
          }),
      } as Response)
    ) as unknown as typeof fetch;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders a user profile from the API", async () => {
    render(
      <MemoryRouter initialEntries={["/users/1"]}>
        <Routes>
          <Route path="/users/:userId" element={<UserProfile />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByRole("heading", { name: "Alice Zhang" })).toBeTruthy();
    expect(screen.getByText("Computer Science")).toBeTruthy();
    expect(screen.getByText("Sophomore")).toBeTruthy();
    expect(screen.getByText("Robotics")).toBeTruthy();
    expect(screen.getByText("AI")).toBeTruthy();
    expect(screen.getByText("Robotics Club")).toBeTruthy();
    expect(screen.getByText("AI Society")).toBeTruthy();
    expect(screen.getByText("3")).toBeTruthy();
    expect(screen.getByText("12")).toBeTruthy();
  });

  it("shows edit fields and saves updated profile", async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            id: 1,
            name: "Alice Zhang",
            year: "Sophomore",
            major: "Computer Science",
            interests: ["Robotics", "AI"],
            joined_clubs: [{ id: 101, name: "Robotics Club" }],
            medal_count: 3,
            event_attendance_count: 12,
          }),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            id: 1,
            name: "Alice Updated",
            year: "Senior",
            major: "Computer Engineering",
            interests: ["Robotics", "AI", "Leadership"],
            joined_clubs: [{ id: 101, name: "Robotics Club" }],
            medal_count: 3,
            event_attendance_count: 12,
          }),
      } as Response);

    global.fetch = fetchMock as unknown as typeof fetch;

    render(
      <MemoryRouter initialEntries={["/users/1"]}>
        <Routes>
          <Route path="/users/:userId" element={<UserProfile />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByRole("heading", { name: "Alice Zhang" })).toBeTruthy();
    const user = userEvent.setup();
    const editButtons = screen.getAllByRole("button", { name: "Edit profile" });

    await user.click(editButtons[0]);

    expect((screen.getByPlaceholderText("Name") as HTMLInputElement).value).toBe("Alice Zhang");
    expect((screen.getByPlaceholderText("Major") as HTMLInputElement).value).toBe("Computer Science");
    expect((screen.getByPlaceholderText("Year") as HTMLInputElement).value).toBe("Sophomore");

    const nameInput = screen.getByPlaceholderText("Name");
    await user.clear(nameInput);
    await user.type(nameInput, "Alice Updated");

    await user.click(screen.getByRole("button", { name: "Save profile" }));

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(await screen.findByRole("heading", { name: "Alice Updated" })).toBeTruthy();
    expect(screen.getByText("Computer Engineering")).toBeTruthy();
    expect(screen.getByText("Senior")).toBeTruthy();
  });
});
