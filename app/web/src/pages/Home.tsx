import { Link } from "react-router-dom";

export default function Home() {
  return (
    <>
      <h1>Hello World</h1>

      <div className="card">
        <Link to="/chat">Open campus chat</Link>
      </div>
    </>
  );
}
