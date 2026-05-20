import { useEffect, useState } from "react";

type EventFeedItem = {
  id: number;
  club_name: string;
  title: string;
  start_time: string;
  location?: string | null;
  attendee_count: number;
};

export default function EventsFeed() {
  const [events, setEvents] = useState<EventFeedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submittingId, setSubmittingId] = useState<number | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    fetch("/api/feed/events?user_id=1", {
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          const payload = await response.json().catch(() => null);
          throw new Error(payload?.detail || "Unable to load events");
        }
        return response.json();
      })
      .then((data: EventFeedItem[]) => setEvents(data))
      .catch((fetchError) => {
        if (fetchError.name !== "AbortError") {
          setError(fetchError.message || "Failed to fetch events");
        }
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, []);

  const handleMarkAttending = async (eventId: number) => {
    setSubmittingId(eventId);
    try {
      const response = await fetch(`/api/events/${eventId}/attend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: 1 }),
      });
      if (!response.ok) {
        const errorPayload = await response.json().catch(() => null);
        throw new Error(errorPayload?.detail || "Unable to mark attending");
      }
      const data = await response.json();
      setEvents((current) =>
        current.map((event) =>
          event.id === eventId
            ? { ...event, attendee_count: data.attendee_count }
            : event
        )
      );
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : String(fetchError));
    } finally {
      setSubmittingId(null);
    }
  };

  return (
    <div className="mx-auto max-w-5xl p-6">
      <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-semibold">Upcoming events</h1>
          <p className="text-base-content/70">Events from clubs you have joined, sorted by next start time.</p>
        </div>
      </div>

      {loading ? (
        <p className="text-base-content/70">Loading events…</p>
      ) : error ? (
        <p className="text-error">{error}</p>
      ) : events.length === 0 ? (
        <p className="text-base-content/70">No upcoming events found. Join a club to see its events.</p>
      ) : (
        <div className="grid gap-4">
          {events.map((event) => (
            <div key={event.id} className="rounded-3xl border border-base-200 bg-base-100 p-6 shadow-sm">
              <div className="mb-2 flex flex-wrap items-center justify-between gap-3">
                <div>
                  <p className="text-sm uppercase text-base-content/50">{event.club_name}</p>
                  <h2 className="text-xl font-semibold">{event.title}</h2>
                </div>
                <div className="text-right text-sm text-base-content/70">
                  <div>{new Date(event.start_time).toLocaleString()}</div>
                  <div>{event.location || "Online / campus"}</div>
                </div>
              </div>
              <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                <span className="text-sm text-base-content/70">Attendees: {event.attendee_count}</span>
                <button
                  className="btn btn-sm btn-primary"
                  disabled={submittingId === event.id}
                  onClick={() => handleMarkAttending(event.id)}
                >
                  {submittingId === event.id ? "Saving…" : "Mark Attending"}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
