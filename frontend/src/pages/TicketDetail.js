import React, { useCallback, useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import api from "../api/axios";
import { useAuth } from "../context/AuthContext";

const statusOptions = ["open", "in_progress", "resolved", "closed"];
const priorityOptions = ["low", "medium", "high"];

export default function TicketDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [ticket, setTicket] = useState(null);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [commentText, setCommentText] = useState("");
  const [posting, setPosting] = useState(false);
  const [saving, setSaving] = useState(false);

  const isAgent = user?.role === "agent";

  const loadTicket = useCallback(() => {
    setLoading(true);
    setError("");
    api
      .get(`/tickets/${id}`)
      .then(({ data }) => setTicket(data))
      .catch((err) => {
        if (err.response?.status === 404) setError("Ticket not found.");
        else if (err.response?.status === 403) setError("You do not have access to this ticket.");
        else setError("Something went wrong loading this ticket.");
      })
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    loadTicket();
  }, [loadTicket]);

  useEffect(() => {
    if (isAgent) {
      api.get("/users", { params: { role: "agent" } }).then(({ data }) => setAgents(data)).catch(() => {});
    }
  }, [isAgent]);

  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!commentText.trim()) return;
    setPosting(true);
    try {
      await api.post(`/tickets/${id}/comments`, { comment: commentText });
      setCommentText("");
      loadTicket();
    } catch {
      setError("Could not post your comment.");
    } finally {
      setPosting(false);
    }
  };

  const updateField = async (field, value) => {
    setSaving(true);
    try {
      const { data } = await api.put(`/tickets/${id}`, { [field]: value });
      setTicket(data);
    } catch {
      setError("Could not save that change.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="page"><p>Loading ticket…</p></div>;
  if (error && !ticket) return <div className="page"><div className="alert alert-error">{error}</div></div>;
  if (!ticket) return null;

  return (
    <div className="page">
      <button className="btn-link" onClick={() => navigate(-1)}>&larr; Back</button>
      <div className="card ticket-detail-card">
        <div className="page-header">
          <h1>#{ticket.id} — {ticket.subject}</h1>
        </div>
        <p className="ticket-meta">
          Raised by {ticket.customer?.name} ({ticket.customer?.email}) on {new Date(ticket.created_at).toLocaleString()}
        </p>

        {error && <div className="alert alert-error">{error}</div>}

        <p className="ticket-description">{ticket.description}</p>

        <div className="ticket-controls">
          <div>
            <label>Priority</label>
            {isAgent ? (
              <select value={ticket.priority} onChange={(e) => updateField("priority", e.target.value)} disabled={saving}>
                {priorityOptions.map((p) => <option key={p} value={p}>{p}</option>)}
              </select>
            ) : (
              <span className={`badge badge-priority-${ticket.priority}`}>{ticket.priority}</span>
            )}
          </div>
          <div>
            <label>Status</label>
            {isAgent ? (
              <select value={ticket.status} onChange={(e) => updateField("status", e.target.value)} disabled={saving}>
                {statusOptions.map((s) => <option key={s} value={s}>{s}</option>)}
              </select>
            ) : (
              <span className={`badge badge-status-${ticket.status}`}>{ticket.status}</span>
            )}
          </div>
          {isAgent && (
            <div>
              <label>Assigned to</label>
              <select
                value={ticket.assigned_to || ""}
                onChange={(e) => updateField("assigned_to", e.target.value ? Number(e.target.value) : null)}
                disabled={saving}
              >
                <option value="">Unassigned</option>
                {agents.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
              </select>
            </div>
          )}
        </div>
      </div>

      <div className="card">
        <h2>Comments</h2>
        <div className="comment-list">
          {ticket.comments.length === 0 && <p className="empty-state">No comments yet.</p>}
          {ticket.comments.map((c) => (
            <div key={c.id} className="comment">
              <div className="comment-header">
                <strong>{c.author?.name}</strong>
                <span className="comment-date">{new Date(c.created_at).toLocaleString()}</span>
              </div>
              <p>{c.comment}</p>
            </div>
          ))}
        </div>
        <form onSubmit={handleAddComment} className="comment-form">
          <textarea
            rows={3}
            placeholder="Add a comment…"
            value={commentText}
            onChange={(e) => setCommentText(e.target.value)}
          />
          <button className="btn btn-primary" type="submit" disabled={posting}>
            {posting ? "Posting…" : "Add comment"}
          </button>
        </form>
      </div>
    </div>
  );
}
