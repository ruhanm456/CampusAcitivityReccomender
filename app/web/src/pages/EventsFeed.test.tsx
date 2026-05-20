/* @vitest-environment happy-dom */

import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import EventsFeed from "./EventsFeed";

describe("EventsFeed", () => {
  beforeEach(() => {
    global.fetch = vi.fn(() =>
      Promise.resolve({
        ok: true,
        json: () =>
          Promise.resolve([
            {
              id: 1,
              club_name: "Robotics Club",
              title: "Intro to Robotics",
              start_time: "2026-06-01T18:00:00Z",
              location: "Lab 1",
              attendee_count: 5,
            },
          ]),
      } as Response)
    ) as unknown as typeof fetch;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders event cards from the feed", async () => {
    render(
      <MemoryRouter initialEntries={["/feed"]}>
        <Routes>
          <Route path="/feed" element={<EventsFeed />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByRole("heading", { name: /Upcoming events/i })).toBeTruthy();
    expect(await screen.findByText("Intro to Robotics")).toBeTruthy();
    expect(screen.getByText("Robotics Club")).toBeTruthy();
    expect(screen.getByRole("button", { name: "Mark Attending" })).toBeTruthy();
  });

  it("marks attending and updates attendee count", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve([
            {
              id: 1,
              club_name: "Robotics Club",
              title: "Intro to Robotics",
              start_time: "2026-06-01T18:00:00Z",
              location: "Lab 1",
              attendee_count: 5,
            },
          ]),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ event_id: 1, user_id: 1, attendee_count: 6 }),
      } as Response);

    global.fetch = fetchMock as unknown as typeof fetch;

    render(
      <MemoryRouter initialEntries={["/feed"]}>
        <Routes>
          <Route path="/feed" element={<EventsFeed />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText("Intro to Robotics")).toBeTruthy();

    const button = screen.getByRole("button", { name: "Mark Attending" });
    const user = userEvent.setup();
    await user.click(button);

    expect(fetchMock).toHaveBeenLastCalledWith("/api/events/1/attend", expect.objectContaining({
      method: "POST",
    }));
    expect(await screen.findByText("Attendees: 6")).toBeTruthy();
  });
});
