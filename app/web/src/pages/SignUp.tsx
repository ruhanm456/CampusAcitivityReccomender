import React, { useState, type SubmitEventHandler } from "react";
import { useNavigate } from "react-router-dom";
import { SERVER_URL } from "../App";

interface SignupResponse {
  message?: string;
  error?: string;
  verify?: boolean;
}

const REDIRECT = "/verify-email";

export default function SignupForm() {
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.SubmitEvent) => {
    e.preventDefault();
    setError("");

    try {
      const res = await fetch(`${SERVER_URL}/auth/register/`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email, password }),
      });

      const data: SignupResponse = await res.json();

      if (!res.ok) {
        setError(data.error || "Something went wrong");
        return;
      }

      // Redirect after successful signup
      navigate(REDIRECT);
    } catch {
      setError("Unable to connect to server. Try again later.");
    }
  };

  return (
    <div className="flex justify-center mt-20">
      <form
        onSubmit={handleSubmit}
        className="w-80 p-6 rounded-xl bg-base-200 shadow-xl flex flex-col gap-4"
      >
        <h2 className="text-xl font-bold text-center">Create Account</h2>
        <input
          placeholder="Chosen Name"
          required
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="input input-bordered w-full"
        />

        <input
          type="email"
          placeholder="Email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="input input-bordered w-full"
        />

        <input
          type="password"
          placeholder="Password (min 8 chars)"
          required
          minLength={8}
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="input input-bordered w-full"
        />

        {error && <p className="text-error text-sm">{error}</p>}

        <button type="submit" className="btn btn-primary w-full">
          Sign Up
        </button>
      </form>
    </div>
  );
}
