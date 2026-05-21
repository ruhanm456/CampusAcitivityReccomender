/* @vitest-environment happy-dom */

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import ClubHome from "./ClubHome";

describe("ClubHome", () => {
  beforeEach(() => {
    globalThis.fetch = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("displays club name, description, tags as pills, meeting time, and location", async () => {
    const mockClubData = {
      id: 1,
      name: "Photography Club",
      description: "Learn and share photography skills",
      tags: "photography,art,creative",
      meeting_time: "Friday 19:00",
      location: "Room 205, Arts Building",
      members_count: 24,
      created_at: "2024-01-15T10:30:00Z",
      member_preview: [],
    };

    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockClubData),
    } as Response);

    render(
      <MemoryRouter initialEntries={["/clubs/1"]}>
        <Routes>
          <Route path="/clubs/:id" element={<ClubHome />} />
        </Routes>
      </MemoryRouter>,
    );

    // Verify club name renders large
    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "Photography Club", level: 1 }),
      ).toBeInTheDocument();
    });

    // Verify description
    expect(
      screen.getByText("Learn and share photography skills"),
    ).toBeInTheDocument();

    // Verify tags render as pills
    expect(screen.getByText("photography")).toBeInTheDocument();
    expect(screen.getByText("art")).toBeInTheDocument();
    expect(screen.getByText("creative")).toBeInTheDocument();

    // Verify meeting time and location
    expect(screen.getByText(/Friday 19:00/)).toBeInTheDocument();
    expect(screen.getByText(/Room 205, Arts Building/)).toBeInTheDocument();

    // Verify member count
    expect(screen.getByText(/24 members/i)).toBeInTheDocument();
  });

  it("displays Join Club button when user is not a member", async () => {
    const mockClubData = {
      id: 1,
      name: "Photography Club",
      description: "Learn and share photography skills",
      tags: "photography,art,creative",
      meeting_time: "Friday 19:00",
      location: "Room 205, Arts Building",
      members_count: 24,
      created_at: "2024-01-15T10:30:00Z",
      member_preview: [],
      is_member: false,
    };

    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockClubData),
    } as Response);

    render(
      <MemoryRouter initialEntries={["/clubs/1"]}>
        <Routes>
          <Route path="/clubs/:id" element={<ClubHome />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /join club/i }),
      ).toBeInTheDocument();
    });
  });

  it("displays Leave Club button when user is a member", async () => {
    const mockClubData = {
      id: 1,
      name: "Photography Club",
      description: "Learn and share photography skills",
      tags: "photography,art,creative",
      meeting_time: "Friday 19:00",
      location: "Room 205, Arts Building",
      members_count: 24,
      created_at: "2024-01-15T10:30:00Z",
      member_preview: [],
      is_member: true,
    };

    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockClubData),
    } as Response);

    render(
      <MemoryRouter initialEntries={["/clubs/1"]}>
        <Routes>
          <Route path="/clubs/:id" element={<ClubHome />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /leave club/i }),
      ).toBeInTheDocument();
    });
  });

  it("displays upcoming events with RSVP buttons", async () => {
    const mockClubData = {
      id: 1,
      name: "Photography Club",
      description: "Learn and share photography skills",
      tags: "photography,art,creative",
      meeting_time: "Friday 19:00",
      location: "Room 205, Arts Building",
      members_count: 24,
      created_at: "2024-01-15T10:30:00Z",
      member_preview: [],
    };

    const mockEventsData = [
      {
        id: 101,
        club_id: 1,
        title: "Photography Walk in the Park",
        description: "Outdoor photography session",
        created_at: "2024-05-01T14:00:00Z",
        updated_at: "2024-05-01T14:00:00Z",
      },
      {
        id: 102,
        club_id: 1,
        title: "Photo Editing Workshop",
        description: "Learn Lightroom and Photoshop basics",
        created_at: "2024-05-05T15:00:00Z",
        updated_at: "2024-05-05T15:00:00Z",
      },
    ];

    (globalThis.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockClubData),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockEventsData),
      } as Response);

    render(
      <MemoryRouter initialEntries={["/clubs/1"]}>
        <Routes>
          <Route path="/clubs/:id" element={<ClubHome />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(
        screen.getByText("Photography Walk in the Park"),
      ).toBeInTheDocument();
    });

    expect(screen.getByText("Photo Editing Workshop")).toBeInTheDocument();
    expect(screen.getByText("Outdoor photography session")).toBeInTheDocument();

    // Verify RSVP buttons are present
    const rsvpButtons = screen.getAllByRole("button", { name: /attending\?/i });
    expect(rsvpButtons.length).toBeGreaterThanOrEqual(2);
  });

  it("displays member avatars and names in a grid", async () => {
    const mockClubData = {
      id: 1,
      name: "Photography Club",
      description: "Learn and share photography skills",
      tags: "photography,art,creative",
      meeting_time: "Friday 19:00",
      location: "Room 205, Arts Building",
      members_count: 24,
      created_at: "2024-01-15T10:30:00Z",
      member_preview: [
        {
          id: 10,
          name: "Alice Zhang",
          email: "alice@university.edu",
          year: "Junior",
          major: "Computer Science",
        },
        {
          id: 11,
          name: "Bob Johnson",
          email: "bob@university.edu",
          year: "Senior",
          major: "Art",
        },
        {
          id: 12,
          name: "Carol Davis",
          email: "carol@university.edu",
          year: "Sophomore",
          major: "Photography",
        },
      ],
    };

    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockClubData),
    } as Response);

    render(
      <MemoryRouter initialEntries={["/clubs/1"]}>
        <Routes>
          <Route path="/clubs/:id" element={<ClubHome />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText("Alice Zhang")).toBeInTheDocument();
    });

    expect(screen.getByText("Bob Johnson")).toBeInTheDocument();
    expect(screen.getByText("Carol Davis")).toBeInTheDocument();

    // Verify member links navigate to profiles
    const memberLinks = screen.getAllByRole("link", {
      name: /alice zhang|bob johnson|carol davis/i,
    });
    expect(memberLinks.length).toBe(3);
  });

  it("shows loading state while fetching club data", () => {
    (globalThis.fetch as any).mockReturnValueOnce(
      new Promise(() => {}), // Never resolves, simulating loading
    );

    render(
      <MemoryRouter initialEntries={["/clubs/1"]}>
        <Routes>
          <Route path="/clubs/:id" element={<ClubHome />} />
        </Routes>
      </MemoryRouter>,
    );

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it("shows error message when club data fetch fails", async () => {
    (globalThis.fetch as any).mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ detail: "Club not found" }),
    } as Response);

    render(
      <MemoryRouter initialEntries={["/clubs/1"]}>
        <Routes>
          <Route path="/clubs/:id" element={<ClubHome />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(screen.getByText(/club not found|error/i)).toBeInTheDocument();
    });
  });

  it("renders empty state when club has no upcoming events or members", async () => {
    const mockClubData = {
      id: 1,
      name: "New Club",
      description: "A brand new club",
      tags: "new",
      meeting_time: "Monday 18:00",
      location: "Room 101",
      members_count: 2,
      created_at: "2024-05-15T10:30:00Z",
      member_preview: [],
    };

    (globalThis.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockClubData),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      } as Response);

    render(
      <MemoryRouter initialEntries={["/clubs/1"]}>
        <Routes>
          <Route path="/clubs/:id" element={<ClubHome />} />
        </Routes>
      </MemoryRouter>,
    );

    await waitFor(() => {
      expect(
        screen.getByRole("heading", { name: "New Club" }),
      ).toBeInTheDocument();
    });

    expect(screen.getAllByText(/no upcoming events/i).length).toBeGreaterThan(
      0,
    );
    expect(screen.getAllByText(/no members/i).length).toBeGreaterThan(0);
  });

  it("toggles Join/Leave Club button when clicked", async () => {
    const user = userEvent.setup();
    const mockClubData = {
      id: 1,
      name: "Photography Club",
      description: "Learn and share photography skills",
      tags: "photography,art,creative",
      meeting_time: "Friday 19:00",
      location: "Room 205, Arts Building",
      members_count: 24,
      created_at: "2024-01-15T10:30:00Z",
      member_preview: [],
      is_member: false,
    };

    (globalThis.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockClubData),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([]),
      } as Response)
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ message: "Successfully joined club" }),
      } as Response);

    render(
      <MemoryRouter initialEntries={["/clubs/1"]}>
        <Routes>
          <Route path="/clubs/:id" element={<ClubHome />} />
        </Routes>
      </MemoryRouter>,
    );

    const joinButtons = await screen.findAllByRole("button", {
      name: /join club/i,
    });
    expect(joinButtons.length).toBeGreaterThan(0);
    const joinButton = joinButtons[0];

    await user.click(joinButton);

    // After clicking, button should change to Leave Club
    await waitFor(() => {
      expect(
        screen.getByRole("button", { name: /leave club/i }),
      ).toBeInTheDocument();
    });
  });
});
