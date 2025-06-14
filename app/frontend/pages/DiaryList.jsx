// src/pages/DiaryList.jsx
import { useEffect, useState } from "react";
import api from "../api/axios";
import { Link } from "react-router-dom";

export default function DiaryList() {
  const [diaries, setDiaries] = useState([]);

  const fetchData = async () => {
    try {
      const res = await api.get("/diaries");
      setDiaries(res.data);
    } catch {
      alert("로그인 필요");
    }
  };

  const handleDelete = async (id) => {
    await api.delete(`/diaries/${id}`);
    fetchData();
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div>
      <h2>Diaries</h2>
      <Link to="/new">+ New Diary</Link>
      <ul>
        {diaries.map(d => (
          <li key={d.id}>
            <strong>{d.title}</strong>
            <p>{d.content}</p>
            <Link to={`/edit/${d.id}`}>Edit</Link>
            <button onClick={() => handleDelete(d.id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
