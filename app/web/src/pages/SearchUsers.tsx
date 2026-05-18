import { FormEvent, useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

type UserSearchResult = {
  id: number;
  name: string;
  year: string;
  major: string;
  interests: string[];
  joined_clubs: { id: number; name: string }[];
  medal_count: number;
  event_attendance_count: number;
};

export default function SearchUsers() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [query, setQuery] = useState(searchParams.get("search") || "");
  const [results, setResults] = useState<UserSearchResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const queryValue = searchParams.get("search") || "";
    setQuery(queryValue);

    const controller = new AbortController();
    setLoading(true);
    setError(null);

    const url = queryValue
      ? `/api/users?search=${encodeURIComponent(queryValue)}`
      : "/api/users";

    fetch(url, { signal: controller.signal })
      .then(async (response) => {
        if (!response.ok) {
          const payload = await response.json().catch(() => null);
          throw new Error(payload?.detail || "Unable to fetch users");
        }
        return response.json();
      })
      .then((data: UserSearchResult[]) => {
        setResults(data);
      })
      .catch((fetchError) => {
        if (fetchError.name !== "AbortError") {
          setError(fetchError.message || "Unable to fetch users");
        }
      })
      .finally(() => {
        setLoading(false);
      });

    return () => controller.abort();
  }, [searchParams]);

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const nextParams = query.trim() ? { search: query.trim() } : {};
    setSearchParams(nextParams);
  };

  return (
    <div className="mx-auto max-w-4xl p-6">
      <div className="mb-6 rounded-3xl border border-base-200 bg-base-100 p-6 shadow-sm">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-3xl font-semibold">Discover users</h1>
            <p className="text-base-content/70">Search by name to find public profiles.</p>
          </div>
          <Link to="/" className="btn btn-ghost">
            Back home
          </Link>
        </div>

        <form className="mt-6 flex flex-col gap-3 sm:flex-row" onSubmit={handleSubmit}>
          <input
            type="search"
            className="input input-bordered w-full flex-1"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search users by name"
            aria-label="Search users"
          />
          <button type="submit" className="btn btn-primary sm:shrink-0">
            Find
          </button>
        </form>
      </div>

      {loading ? (
        <div className="rounded-3xl border border-base-200 bg-base-100 p-6 text-base-content/70 shadow-sm">
          Loading users...
        </div>
      ) : error ? (
        <div className="rounded-3xl border border-error bg-error/10 p-6 text-error shadow-sm">
          {error}
        </div>
      ) : results.length === 0 ? (
        <div className="rounded-3xl border border-base-200 bg-base-100 p-6 text-base-content/70 shadow-sm">
          No users found.
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {results.map((user) => (
            <Link
              key={user.id}
              to={`/users/${user.id}`}
              className="group rounded-3xl border border-base-200 bg-base-100 p-5 transition hover:border-primary"
            >
              <div className="mb-3 flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-xl font-semibold">{user.name}</h2>
                  <p className="text-sm text-base-content/70">{user.year} • {user.major}</p>
                </div>
                <div className="rounded-2xl bg-primary px-3 py-1 text-sm font-semibold text-white">
                  {user.medal_count} medals
                </div>
              </div>
              <div className="mb-3 flex flex-wrap gap-2">
                {user.interests.map((interest) => (
                  <span
                    key={interest}
                    className="rounded-full border border-base-200 bg-base-200 px-3 py-1 text-xs"
                  >
                    {interest}
                  </span>
                ))}
              </div>
              <p className="text-sm text-base-content/70">Joined clubs: {user.joined_clubs.length}</p>
              <p className="text-sm text-base-content/70">Event attendance: {user.event_attendance_count}</p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
