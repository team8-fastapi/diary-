// src/pages/DiaryEditPage.jsx
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getDiary, updateDiary } from "../api/diaries";

export default function DiaryEditPage() {
  const { id } = useParams();
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    getDiary(id).then((d) => {
      setTitle(d.title);
      setContent(d.content);
    });
  }, [id]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    await updateDiary(id, { title, content });
    navigate(`/diaries/${id}`);
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto mt-10 space-y-4">
      <h1 className="text-xl font-bold">다이어리 수정</h1>
      <input
        className="w-full border px-3 py-2 rounded"
        placeholder="제목"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />
      <textarea
        className="w-full border px-3 py-2 rounded"
        placeholder="내용"
        rows={6}
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />
      <button className="bg-yellow-600 text-white px-4 py-2 rounded">수정하기</button>
    </form>
  );
}
