import "./App.css";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import ChatWindow from "./pages/ChatWindow";
import ClubPage from "./pages/ClubPage";
import EventsFeed from "./pages/EventsFeed";
import Home from "./pages/Home";
import SearchUsers from "./pages/SearchUsers";
import UserProfile from "./pages/UserProfile";
// import Home from "./pages/Home";
import SignupForm from "./pages/SignUp";

export const SERVER_URL = "http://127.0.0.1:8000";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* <Route path="/" element={<Home />} /> */}
        <Route
          path="/chat"
          element={
            <div className="h-screen">
              <ChatWindow />
            </div>
          }
        />
        <Route path="/feed" element={<EventsFeed />} />
        <Route path="/clubs/:clubId" element={<ClubPage />} />
        <Route path="/users" element={<SearchUsers />} />
        <Route path="/users/:userId" element={<UserProfile />} />
        <Route path="*" element={<Navigate to="/" replace />} />
        <Route path="/" element={<SignupForm />} />{" "}
        {/* todo: change route back to /signup */}
      </Routes>
    </BrowserRouter>
  );
}

export default App;
