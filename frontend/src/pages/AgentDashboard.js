import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../api/axios";

const statusLabel = { open: "Open", in_progress: "In Progress", resolved: "Resolved", closed: "Closed" };

export default function AgentDashboard() {
  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [ordering, setOrdering] = useState("-created_at");

  useEffect(() => {
    api.get("/tickets/stats").then(({ data }) => setStats(data)).catch(() => {});
  }, []);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    const params = { ordering };
    if (search) params.search = search;
    if (statusFilter) params.status = statusFilter;
    if (priorityFilter) params.priority = priorityFilter;

    api
      .get("/tickets", { params })
      .then(({ data }) => active && setTickets(data.results || data))
      .catch(() => active && setError("Could not load tickets."))
      .finally(() => active && setLoading(false));

    return () => {
      active = false;
    };
  }, [search, statusFilter, priorityFilter, ordering]);

  return (
    <div className="page">
      <h1>Agent Dashboard</h1>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card"><span className="stat-number">{stats.total}</span><span>Total tickets</span></div>
          <div className="stat-card"><span className="stat-number">{stats.by_status.open || 0}</span><span>Open</span></div>
          <div className="stat-card"><span className="stat-number">{stats.by_status.in_progress || 0}</span><span>In Progress</span></div>
          <div className="stat-card"><span className="stat-number">{stats.unassigned}</span><span>Unassigned</span></div>
        </div>
      )}

      <div className="filters">
        <input placeholder="Search tickets…" value={search} onChange={(e) => setSearch(e.target.value)} />
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All statuses</option>
          {Object.entries(statusLabel).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
        <select value={priorityFilter} onChange={(e) => setPriorityFilter(e.target.value)}>
          <option value="">All priorities</option>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <select value={ordering} onChange={(e) => setOrdering(e.target.value)}>
          <option value="-created_at">Newest first</option>
          <option value="created_at">Oldest first</option>
          <option value="-priority">Priority (high→low)</option>
        </select>
      </div>

      {loading && <p>Loading tickets…</p>}
      {error && <div className="alert alert-error">{error}</div>}
      {!loading && !error && tickets.length === 0 && <p className="empty-state">No tickets match these filters.</p>}

      <table className="ticket-table">
        <thead>
          <tr>
            <th>ID</th><th>Subject</th><th>Customer</th><th>Priority</th><th>Status</th><th>Assigned To</th><th>Updated</th>
          </tr>
        </thead>
        <tbody>
          {tickets.map((t) => (
            <tr key={t.id}>
              <td><Link to={`/tickets/${t.id}`}>#{t.id}</Link></td>
              <td><Link to={`/tickets/${t.id}`}>{t.subject}</Link></td>
              <td>{t.customer?.name}</td>
              <td><span className={`badge badge-priority-${t.priority}`}>{t.priority}</span></td>
              <td><span className={`badge badge-status-${t.status}`}>{statusLabel[t.status]}</span></td>
              <td>{t.assigned_to_detail?.name || "—"}</td>
              <td>{new Date(t.updated_at).toLocaleDateString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
