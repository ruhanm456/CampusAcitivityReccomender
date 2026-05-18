import { ChangeEvent, useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";

type Club = {
  id: number;
  name: string;
};

type EventAttendance = {
  id: number;
  title: string;
  date: string;
};

type UserProfileData = {
  id: number;
  name: string;
  year: string;
  major: string;
  interests: string[];
  joined_clubs: Club[];
  recent_events: EventAttendance[];
  medal_count: number;
  event_attendance_count: number;
  avatar_data?: string;
  avatar_mime?: string;
};

const avatarInitials = (name: string) => {
  return name
    .split(" ")
    .map((part) => part[0] ?? "")
    .slice(0, 2)
    .join("")
    .toUpperCase();
};

export default function UserProfile() {
  const { userId } = useParams<{ userId: string }>();
  const [profile, setProfile] = useState<UserProfileData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [nameInput, setNameInput] = useState("");
  const [yearInput, setYearInput] = useState("");
  const [majorInput, setMajorInput] = useState("");
  const [interestsInput, setInterestsInput] = useState("");
  const [avatarFile, setAvatarFile] = useState<File | null>(null);
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null);

  useEffect(() => {
    if (!userId) return;

    const controller = new AbortController();

    fetch(`/api/users/${userId}/public-profile`, {
      signal: controller.signal,
    })
      .then(async (response) => {
        if (!response.ok) {
          const errorPayload = await response.json().catch(() => null);
          throw new Error(
            errorPayload?.detail || "Unable to load user profile"
          );
        }
        return response.json();
      })
      .then((data: UserProfileData) => {
        setProfile(data);
        setNameInput(data.name);
        setYearInput(data.year);
        setMajorInput(data.major);
        setInterestsInput(data.interests.join(", "));
      })
      .catch((fetchError) => {
        if (fetchError.name !== "AbortError") {
          setError(fetchError.message || "Unable to load user profile");
        }
      })
      .finally(() => {
        setLoading(false);
      });

    return () => {
      controller.abort();
    };
  }, [userId]);

  useEffect(() => {
    if (!avatarFile) {
      setAvatarPreview(null);
      return;
    }

    const url = URL.createObjectURL(avatarFile);
    setAvatarPreview(url);

    return () => {
      URL.revokeObjectURL(url);
    };
  }, [avatarFile]);

  const avatarSrc = useMemo(() => {
    if (avatarPreview) {
      return avatarPreview;
    }
    if (profile?.avatar_data && profile.avatar_mime) {
      return `data:${profile.avatar_mime};base64,${profile.avatar_data}`;
    }
    return null;
  }, [avatarPreview, profile]);

  const handleStartEdit = () => {
    if (!profile) return;
    setIsEditing(true);
    setNameInput(profile.name);
    setYearInput(profile.year);
    setMajorInput(profile.major);
    setInterestsInput(profile.interests.join(", "));
    setAvatarFile(null);
  };

  const handleCancel = () => {
    setIsEditing(false);
    setAvatarFile(null);
    setAvatarPreview(null);
    if (profile) {
      setNameInput(profile.name);
      setYearInput(profile.year);
      setMajorInput(profile.major);
      setInterestsInput(profile.interests.join(", "));
    }
  };

  const handleAvatarChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setAvatarFile(file);
  };

  const handleSave = async () => {
    if (!userId || !profile) return;
    setSubmitting(true);

    const formData = new FormData();
    formData.append("name", nameInput);
    formData.append("year", yearInput);
    formData.append("major", majorInput);
    formData.append("interests", interestsInput);
    if (avatarFile) {
      formData.append("avatar", avatarFile);
    }

    const response = await fetch(`/api/users/${userId}/public-profile`, {
      method: "PUT",
      body: formData,
    });

    if (!response.ok) {
      const errorPayload = await response.json().catch(() => null);
      setError(errorPayload?.detail || "Unable to save profile");
      setSubmitting(false);
      return;
    }

    const data: UserProfileData = await response.json();
    setProfile(data);
    setIsEditing(false);
    setAvatarFile(null);
    setAvatarPreview(null);
    setSubmitting(false);
  };

  if (loading) {
    return (
      <div className="p-6">
        <p className="text-base-content/70">Loading profile…</p>
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

  if (!profile) {
    return null;
  }

  return (
    <div className="mx-auto max-w-3xl p-6">
      <div className="mb-6 rounded-3xl border border-base-200 bg-base-100 p-6 shadow-sm">
        <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="flex h-24 w-24 items-center justify-center rounded-3xl bg-primary text-4xl font-bold text-white">
                {avatarSrc ? null : avatarInitials(profile.name)}
              </div>
              {avatarSrc ? (
                <img
                  src={avatarSrc}
                  alt="Profile"
                  className="h-24 w-24 rounded-3xl object-cover"
                />
              ) : null}
            </div>
            <div>
              {isEditing ? (
                <input
                  value={nameInput}
                  onChange={(event) => setNameInput(event.target.value)}
                  className="input input-bordered w-full max-w-md"
                  placeholder="Name"
                />
              ) : (
                <h1 className="text-3xl font-semibold">{profile.name}</h1>
              )}
              {isEditing ? (
                <div className="mt-3 grid gap-3 sm:grid-cols-2">
                  <input
                    value={majorInput}
                    onChange={(event) => setMajorInput(event.target.value)}
                    className="input input-bordered w-full"
                    placeholder="Major"
                  />
                  <input
                    value={yearInput}
                    onChange={(event) => setYearInput(event.target.value)}
                    className="input input-bordered w-full"
                    placeholder="Year"
                  />
                </div>
              ) : (
                <>
                  <p className="text-sm text-base-content/70">{profile.major}</p>
                  <p className="text-sm text-base-content/70">{profile.year}</p>
                </>
              )}
            </div>
          </div>

          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-3xl border border-base-200 bg-base-200 p-4">
              <p className="text-sm uppercase text-base-content/50">Member of</p>
              <p className="text-2xl font-semibold">{profile.joined_clubs.length} clubs</p>
            </div>
            <div className="rounded-3xl border border-base-200 bg-base-200 p-4">
              <p className="text-sm uppercase text-base-content/50">Events attended</p>
              <p className="text-2xl font-semibold">{profile.event_attendance_count}</p>
            </div>
            <div className="rounded-3xl border border-base-200 bg-base-200 p-4">
              <p className="text-sm uppercase text-base-content/50">Earned</p>
              <p className="text-2xl font-semibold">{profile.medal_count} medals</p>
            </div>
          </div>
        </div>

        <div className="mt-8 grid gap-8">
          <section className="rounded-3xl border border-base-200 bg-base-100 p-6">
            <div className="mb-5 flex items-center justify-between gap-3">
              <div>
                <h2 className="text-xl font-semibold">Joined Clubs</h2>
                <p className="text-sm text-base-content/70">
                  Explore the clubs this user is part of.
                </p>
              </div>
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              {profile.joined_clubs.map((club) => (
                <Link
                  key={club.id}
                  to={`/clubs/${club.id}`}
                  className="rounded-3xl border border-base-200 bg-base-100 p-5 transition hover:border-primary"
                >
                  <h3 className="text-lg font-semibold">{club.name}</h3>
                  <p className="text-sm text-base-content/70">View club details</p>
                </Link>
              ))}
            </div>
          </section>

          <section className="rounded-3xl border border-base-200 bg-base-100 p-6">
            <div className="mb-5">
              <h2 className="text-xl font-semibold">Recent Events Attended</h2>
              <p className="text-sm text-base-content/70">
                Last 10 attended events with dates.
              </p>
            </div>
            {profile.recent_events.length === 0 ? (
              <p className="text-base-content/70">No recent events found.</p>
            ) : (
              <div className="space-y-4">
                {profile.recent_events.slice(0, 10).map((event) => (
                  <div
                    key={event.id}
                    className="rounded-3xl border border-base-200 bg-base-200 p-4"
                  >
                    <p className="font-semibold">{event.title}</p>
                    <p className="text-sm text-base-content/70">
                      {new Date(event.date).toLocaleDateString(undefined, {
                        year: "numeric",
                        month: "short",
                        day: "numeric",
                      })}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </section>
        </div>

        {isEditing ? (
          <div className="mt-6 grid gap-4">
            <label className="block">
              <span className="label-text">Profile picture</span>
              <input
                type="file"
                accept="image/*"
                onChange={handleAvatarChange}
                className="file-input file-input-bordered w-full max-w-xs"
              />
            </label>
            <label className="block">
              <span className="label-text">Interests</span>
              <input
                value={interestsInput}
                onChange={(event) => setInterestsInput(event.target.value)}
                className="input input-bordered w-full"
                placeholder="Robotics, AI, Hackathons"
              />
            </label>
          </div>
        ) : null}
      </div>

      <section className="mb-6 rounded-3xl border border-base-200 bg-base-100 p-6 shadow-sm">
        <div className="flex items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold">Interests</h2>
            <p className="text-sm text-base-content/70">Use comma-separated values when editing.</p>
          </div>
          <div>
            {isEditing ? (
              <div className="flex gap-2">
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={handleCancel}
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={handleSave}
                  disabled={submitting}
                >
                  {submitting ? "Saving..." : "Save profile"}
                </button>
              </div>
            ) : (
              <button type="button" className="btn btn-secondary" onClick={handleStartEdit}>
                Edit profile
              </button>
            )}
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          {(isEditing ? interestsInput.split(",").map((item) => item.trim()).filter(Boolean) : profile.interests).map((interest) => (
            <span key={interest} className="rounded-full border border-base-200 bg-base-200 px-3 py-1 text-sm">
              {interest}
            </span>
          ))}
        </div>
      </section>

      <section className="mb-6 rounded-3xl border border-base-200 bg-base-100 p-6 shadow-sm">
        <h2 className="text-xl font-semibold">Joined clubs</h2>
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          {profile.joined_clubs.map((club) => (
            <Link
              key={club.id}
              to={`/clubs/${club.id}`}
              className="rounded-3xl border border-base-200 bg-base-100 p-4 transition hover:border-primary"
            >
              <p className="text-lg font-semibold">{club.name}</p>
              <p className="text-sm text-base-content/70">View club page</p>
            </Link>
          ))}
        </div>
      </section>

      <Link to="/" className="btn btn-ghost">
        Back to home
      </Link>
    </div>
  );
}
