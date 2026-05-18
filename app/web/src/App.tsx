import "./App.css";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Home from "./pages/Home";
import SearchUsers from "./pages/SearchUsers";
import UserProfile from "./pages/UserProfile";
import SignupForm from "./pages/SignUp";
import ClubHome from "./pages/ClubHome";

export const SERVER_URL = "http://127.0.0.1:8000";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/users" element={<SearchUsers />} />
        <Route path="/users/:userId" element={<UserProfile />} />
        <Route path="*" element={<Navigate to="/" replace />} />
        <Route path="/signup" element={<SignupForm />} />
        <Route path="/clubs/:clubId" element={<ClubHome />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
