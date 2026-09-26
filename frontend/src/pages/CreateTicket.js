import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

export default function CreateTicket() {
  const [subject, setSubject] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("medium");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  const validate = () => {
    if (!subject.trim()) return "Subject is required.";
    if (!description.trim()) return "Description is required.";
    return "";
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }
    setError("");
    setSubmitting(true);
    try {
      const { data } = await api.post("/tickets", { subject, description, priority });
      navigate(`/tickets/${data.id}`);
    } catch (err) {
      setError("Could not create the ticket. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page">
      <form className="card form-card" onSubmit={handleSubmit}>
        <h2>New support ticket</h2>
        {error && <div className="alert alert-error">{error}</div>}
        <label>Subject</label>
        <input value={subject} onChange={(e) => setSubject(e.target.value)} placeholder="Short summary of the issue" />
        <label>Description</label>
        <textarea rows={6} value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Describe the issue in detail" />
        <label>Priority</label>
        <select value={priority} onChange={(e) => setPriority(e.target.value)}>
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
        <button className="btn btn-primary" type="submit" disabled={submitting}>
          {submitting ? "Submitting…" : "Submit ticket"}
        </button>
      </form>
    </div>
  );
}
