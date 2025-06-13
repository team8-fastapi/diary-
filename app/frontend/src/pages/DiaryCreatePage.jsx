// src/pages/DiaryCreatePage.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createDiary } from "../api/diaries";

export default function DiaryCreatePage() {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    await createDiary({ title, content });
    navigate("/");
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto mt-10 space-y-4">
      <h1 className="text-xl font-bold">다이어리 작성</h1>
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
      <button className="bg-blue-600 text-white px-4 py-2 rounded">작성하기</button>
    </form>
  );
}
