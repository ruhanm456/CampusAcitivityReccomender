import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

type Club = {
  id: number;
  name: string;
  description?: string;
  meeting_time?: string;
  location?: string;
  members_count: number;
};

type UserClub = {
  id: number;
  name: string;
};

export default function ClubPage() {
  const { clubId } = useParams<{ clubId: string }>();
  const [club, setClub] = useState<Club | null>(null);
  const [joinedClubIds, setJoinedClubIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (!clubId) return;

    const controller = new AbortController();

    fetch(`/api/clubs/${clubId}`, { signal: controller.signal })
      .then(async (clubRes) => {
        if (!clubRes.ok) throw new Error("Unable to load club details");
        const clubData = await clubRes.json();
        setClub(clubData);
      })
      .catch((fetchError) => {
        if (fetchError.name !== "AbortError") {
          setError(fetchError.message || "Unable to load club details");
        }
      })
      .finally(() => setLoading(false));

    fetch("/api/users/1/joined-clubs", { signal: controller.signal })
      .then(async (joinedRes) => {
        if (!joinedRes.ok) return;
        const joinedData = await joinedRes.json();
        setJoinedClubIds(joinedData.map((club: UserClub) => club.id));
      })
      .catch(() => {
        // Ignore joined-clubs failures when the default user is unavailable.
      });

    return () => controller.abort();
  }, [clubId]);

  const isMember = club ? joinedClubIds.includes(club.id) : false;

  const handleMembershipToggle = async () => {
    if (!club) return;
    setIsSubmitting(true);
    try {
      if (isMember) {
        const response = await fetch(`/api/clubs/${club.id}/leave?user_id=1`, {
          method: "DELETE",
        });
        if (!response.ok) {
          const errorPayload = await response.json().catch(() => null);
          throw new Error(errorPayload?.detail || "Unable to leave club");
        }
        setJoinedClubIds((current) => current.filter((id) => id !== club.id));
        setClub({ ...club, members_count: Math.max(0, club.members_count - 1) });
      } else {
        const response = await fetch(`/api/clubs/${club.id}/join`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_id: 1 }),
        });
        if (!response.ok) {
          const errorPayload = await response.json().catch(() => null);
          throw new Error(errorPayload?.detail || "Unable to join club");
        }
        setJoinedClubIds((current) => [...new Set([...current, club.id])]);
        setClub({ ...club, members_count: club.members_count + 1 });
      }
    } catch (fetchError) {
      setError(fetchError instanceof Error ? fetchError.message : String(fetchError));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <p className="text-base-content/70">Loading club details…</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <p className="text-error">{error}</p>
        <Link to="/" className="btn btn-sm mt-4">
          Back home
        </Link>
      </div>
    );
  }

  if (!club) {
    return null;
  }

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-6 rounded-3xl border border-base-200 bg-base-100 p-6 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <h1 className="text-3xl font-semibold">{club.name}</h1>
            <p className="mt-2 text-base-content/70">{club.description || "No description available."}</p>
          </div>
          <button
            className="btn btn-primary"
            disabled={isSubmitting}
            onClick={handleMembershipToggle}
          >
            {isMember ? "Leave club" : "Join club"}
          </button>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <div className="rounded-3xl border border-base-200 bg-base-200 p-4">
            <p className="text-sm uppercase text-base-content/50">Meeting time</p>
            <p>{club.meeting_time || "TBD"}</p>
          </div>
          <div className="rounded-3xl border border-base-200 bg-base-200 p-4">
            <p className="text-sm uppercase text-base-content/50">Location</p>
            <p>{club.location || "Campus"}</p>
          </div>
          <div className="rounded-3xl border border-base-200 bg-base-200 p-4">
            <p className="text-sm uppercase text-base-content/50">Members</p>
            <p>{club.members_count}</p>
          </div>
        </div>
      </div>

      <Link to="/" className="btn btn-outline">
        Back home
      </Link>
    </div>
  );
}
