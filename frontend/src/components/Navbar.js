import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">🎫 Support Desk</Link>
      <div className="navbar-links">
        {user ? (
          <>
            <span className="navbar-user">{user.name} ({user.role})</span>
            {user.role === "customer" && (
              <Link to="/tickets/new" className="btn btn-small">New Ticket</Link>
            )}
            <button className="btn btn-outline btn-small" onClick={handleLogout}>Logout</button>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register">Register</Link>
          </>
        )}
      </div>
    </nav>
  );
}
