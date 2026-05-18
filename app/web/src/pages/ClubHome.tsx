import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import type { ClubData, Event } from "../../ClubTypes";

export default function ClubHome() {
  const { clubId: id } = useParams<{ clubId: string }>();
  const [club, setClub] = useState<ClubData | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isMember, setIsMember] = useState(false);

  useEffect(() => {
    const fetchClubData = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/clubs/${id}`);

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(
            errorData.detail || `HTTP error! status: ${response.status}`,
          );
        }

        const clubData = (await response.json()) as ClubData;
        setClub(clubData);
        setIsMember(clubData.is_member || false);

        setError(null);

        // Fetch events separately - don't block on this
        try {
          const eventsResponse = await fetch(`/api/clubs/${id}/events`);
          if (eventsResponse && eventsResponse.ok) {
            const eventsData = (await eventsResponse.json()) as Event[];
            setEvents(eventsData);
          }
        } catch (err) {
          // Events fetch failed, but don't block - just show empty events
          setEvents([]);
        }
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to load club";
        setError(message);
      } finally {
        setLoading(false);
      }
    };

    fetchClubData();
  }, [id]);

  const handleJoinLeave = async () => {
    try {
      const endpoint = isMember
        ? `/api/clubs/${id}/leave`
        : `/api/clubs/${id}/join`;
      const response = await fetch(endpoint, { method: "POST" });

      if (response?.ok) {
        setIsMember(!isMember);
      }
    } catch (err) {
      console.error("Failed to update membership:", err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <span className="loading loading-spinner loading-lg"></span>
          <p>Loading club information...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div role="alert" className="alert alert-error max-w-md">
          <div>
            <span>{error}</span>
          </div>
        </div>
      </div>
    );
  }

  if (!club) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div role="alert" className="alert alert-warning max-w-md">
          <div>
            <span>Club not found</span>
          </div>
        </div>
      </div>
    );
  }

  const tags = club.tags.split(",").map((tag) => tag.trim());

  return (
    <div className="min-h-screen bg-base-100 p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Club Header Section */}
        <div className="card bg-base-200 shadow-lg mb-8">
          <div className="card-body">
            <h1 className="card-title text-4xl md:text-5xl mb-4">
              {club.name}
            </h1>

            {/* Description */}
            <p className="text-lg text-base-content/80 mb-6">
              {club.description}
            </p>

            {/* Tags */}
            <div className="flex flex-wrap gap-2 mb-6">
              {tags.map((tag) => (
                <span key={tag} className="badge badge-primary badge-lg">
                  {tag}
                </span>
              ))}
            </div>

            {/* Club Info */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div>
                <p className="text-sm text-base-content/70">Meeting Time</p>
                <p className="text-base font-semibold">{club.meeting_time}</p>
              </div>
              <div>
                <p className="text-sm text-base-content/70">Location</p>
                <p className="text-base font-semibold">{club.location}</p>
              </div>
              <div>
                <p className="text-sm text-base-content/70">Members</p>
                <p className="text-base font-semibold">
                  {club.members_count} members
                </p>
              </div>
            </div>

            {/* Join/Leave Button */}
            <div className="card-actions">
              <button
                onClick={handleJoinLeave}
                className={`btn btn-lg ${
                  isMember ? "btn-error" : "btn-primary"
                }`}
              >
                {isMember ? "Leave Club" : "Join Club"}
              </button>
            </div>
          </div>
        </div>

        {/* Events Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-6">Upcoming Events</h2>
          {events.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {events.map((event) => (
                <div
                  key={event.id}
                  className="card bg-base-100 shadow-md border border-base-300"
                >
                  <div className="card-body">
                    <h3 className="card-title text-xl mb-2">{event.title}</h3>
                    <p className="text-base-content/80 mb-4">
                      {event.description}
                    </p>
                    <div className="card-actions">
                      <button className="btn btn-primary btn-sm">
                        Attending?
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div role="alert" className="alert alert-info">
              <span>No upcoming events</span>
            </div>
          )}
        </div>

        {/* Members Section */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold mb-6">Members Preview</h2>
          {club.member_preview.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {club.member_preview.map((member) => (
                <a
                  key={member.id}
                  href={`/users/${member.id}`}
                  className="card bg-base-100 shadow-md hover:shadow-lg transition-shadow cursor-pointer text-center"
                >
                  <div className="card-body items-center gap-2 p-4">
                    <div className="avatar placeholder">
                      <div className="bg-primary text-primary-content rounded-full w-12">
                        <span className="text-sm font-bold">
                          {member.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                    </div>
                    <h3 className="card-title text-sm truncate">
                      {member.name}
                    </h3>
                    <p className="text-xs text-base-content/70">
                      {member.year}
                    </p>
                  </div>
                </a>
              ))}
            </div>
          ) : (
            <div role="alert" className="alert alert-info">
              <span>No members</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
