// src/pages/DiaryForm.jsx
import { useEffect, useState } from "react";
import api from "../api/axios";
import { useNavigate, useParams } from "react-router-dom";

export default function DiaryForm({ editMode }) {
  const [form, setForm] = useState({ title: "", content: "" });
  const navigate = useNavigate();
  const { id } = useParams();

  useEffect(() => {
    if (editMode) {
      api.get(`/diaries/${id}`).then(res => setForm(res.data));
    }
  }, [editMode]);

  const handleSubmit = async () => {
    if (editMode) {
      await api.patch(`/diaries/${id}`, form);
    } else {
      await api.post("/diaries", form);
    }
    navigate("/");
  };

  return (
    <div>
      <h2>{editMode ? "Edit" : "New"} Diary</h2>
      <input placeholder="Title" value={form.title} onChange={e => setForm({ ...form, title: e.target.value })} />
      <textarea placeholder="Content" value={form.content} onChange={e => setForm({ ...form, content: e.target.value })} />
      <button onClick={handleSubmit}>Save</button>
    </div>
  );
}
