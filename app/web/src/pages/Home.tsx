import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

type Club = {
  id: number;
  name: string;
  description?: string;
  location?: string;
  members_count: number;
};

export default function Home() {
  const [clubs, setClubs] = useState<Club[]>([]);
  const [joinedClubIds, setJoinedClubIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    fetch("/api/clubs?limit=4", { signal: controller.signal })
      .then(async (clubsRes) => {
        if (!clubsRes.ok) throw new Error("Unable to load club listings");
        const clubsData = await clubsRes.json();
        setClubs(clubsData);
      })
      .catch((fetchError) => {
        if (fetchError.name !== "AbortError") {
          setError(fetchError.message || "Unable to load clubs");
        }
      })
      .finally(() => setLoading(false));

    fetch("/api/users/1/joined-clubs", { signal: controller.signal })
      .then(async (joinedRes) => {
        if (!joinedRes.ok) return;
        const joinedData = await joinedRes.json();
        setJoinedClubIds(joinedData.map((club: Club) => club.id));
      })
      .catch(() => {
        // Silence joined-clubs failures for unauthenticated/default scenarios.
      });

    return () => controller.abort();
  }, []);

  const handleJoin = async (clubId: number) => {
    try {
      const response = await fetch(`/api/clubs/${clubId}/join`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: 1 }),
      });
      if (!response.ok) {
        const errorPayload = await response.json().catch(() => null);
        throw new Error(errorPayload?.detail || "Unable to join club");
      }
      setJoinedClubIds((prev) => [...new Set([...prev, clubId])]);
      setClubs((current) =>
        current.map((club) =>
          club.id === clubId
            ? { ...club, members_count: club.members_count + 1 }
            : club
        )
      );
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : String(fetchError));
    }
  };

  return (
    <div className="space-y-6 p-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-semibold">Campus Activity Recommender</h1>
        <p className="max-w-xl text-base-content/70">
          Explore clubs, events, and public profiles for campus users.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Link to="/feed" className="btn btn-primary">
          View event feed
        </Link>
        <Link to="/users" className="btn btn-secondary">
          Discover users
        </Link>
      </div>

      <section className="rounded-3xl border border-base-200 bg-base-100 p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold">Suggested clubs</h2>
            <p className="text-base-content/70">Join campus clubs and start receiving event recommendations.</p>
          </div>
        </div>

        {loading ? (
          <p className="text-base-content/70">Loading clubs…</p>
        ) : error ? (
          <p className="text-error">{error}</p>
        ) : clubs.length === 0 ? (
          <p className="text-base-content/70">No clubs available yet.</p>
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {clubs.map((club) => (
              <div key={club.id} className="rounded-3xl border border-base-200 bg-white p-4 shadow-sm">
                <div className="mb-3">
                  <h3 className="text-lg font-semibold">{club.name}</h3>
                  <p className="text-sm text-base-content/70">{club.location || "Campus"}</p>
                </div>
                <p className="mb-3 text-sm text-base-content/70">{club.description || "No description available."}</p>
                <div className="flex items-center justify-between gap-3">
                  <span className="text-sm text-base-content/70">Members: {club.members_count}</span>
                  <button
                    className="btn btn-sm btn-primary"
                    disabled={joinedClubIds.includes(club.id)}
                    onClick={() => handleJoin(club.id)}
                  >
                    {joinedClubIds.includes(club.id) ? "Joined" : "Join"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
