import { Link } from "react-router-dom";

export default function Home() {
  return (
    <div className="space-y-4 p-6">
      <h1 className="text-3xl font-semibold">Campus Activity Recommender</h1>
      <p className="max-w-xl text-base-content/70">
        Explore clubs, events, and public profiles for campus users.
      </p>

      <div className="grid gap-4 sm:grid-cols-2">
        <Link to="/chat" className="btn btn-primary">
          Open campus chat
        </Link>
        <Link to="/users" className="btn btn-secondary">
          Discover users
        </Link>
      </div>
    </div>
  );
}
