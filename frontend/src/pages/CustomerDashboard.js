import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";

const statusLabel = { open: "Open", in_progress: "In Progress", resolved: "Resolved", closed: "Closed" };

export default function CustomerDashboard() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    const params = {};
    if (search) params.search = search;
    if (statusFilter) params.status = statusFilter;

    api
      .get("/tickets", { params })
      .then(({ data }) => {
        if (active) setTickets(data.results || data);
      })
      .catch(() => active && setError("Could not load your tickets."))
      .finally(() => active && setLoading(false));

    return () => {
      active = false;
    };
  }, [search, statusFilter]);

  return (
    <div className="page">
      <div className="page-header">
        <h1>My Tickets</h1>
        <Link to="/tickets/new" className="btn btn-primary">+ New Ticket</Link>
      </div>

      <div className="filters">
        <input
          placeholder="Search tickets…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All statuses</option>
          {Object.entries(statusLabel).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </div>

      {loading && <p>Loading tickets…</p>}
      {error && <div className="alert alert-error">{error}</div>}

      {!loading && !error && tickets.length === 0 && (
        <p className="empty-state">You haven't raised any tickets yet.</p>
      )}

      <div className="ticket-list">
        {tickets.map((t) => (
          <Link to={`/tickets/${t.id}`} key={t.id} className="ticket-card">
            <div className="ticket-card-top">
              <span className="ticket-id">#{t.id}</span>
              <span className={`badge badge-priority-${t.priority}`}>{t.priority}</span>
              <span className={`badge badge-status-${t.status}`}>{statusLabel[t.status]}</span>
            </div>
            <h3>{t.subject}</h3>
            <p className="ticket-meta">{t.comment_count} comment(s) · updated {new Date(t.updated_at).toLocaleString()}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
