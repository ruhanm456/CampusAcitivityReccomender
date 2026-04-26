import "./App.css";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import ChatWindow from "./pages/ChatWindow";
import Home from "./pages/Home";
import SignupForm from "./pages/SignUp";

export const SERVER_URL = "http://127.0.0.1:8000";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route
          path="/chat"
          element={
            <div className="h-screen">
              <ChatWindow />
            </div>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
        <Route path="/signup" element={<SignupForm />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
