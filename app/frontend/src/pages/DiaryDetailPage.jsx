// src/pages/DiaryDetailPage.jsx
import { useEffect, useState } from "react";
import { getDiary, deleteDiary } from "../api/diaries";
import { useNavigate, useParams, Link } from "react-router-dom";

export default function DiaryDetailPage() {
  const { id } = useParams();
  const [diary, setDiary] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    getDiary(id).then(setDiary);
  }, [id]);

  const handleDelete = async () => {
    await deleteDiary(id);
    navigate("/");
  };

  if (!diary) return <p>불러오는 중...</p>;

  return (
    <div className="max-w-2xl mx-auto mt-10 space-y-4">
      <h1 className="text-2xl font-bold">{diary.title}</h1>
      <p>{diary.content}</p>
      <div className="flex gap-2 mt-4">
        <Link
          to={`/diaries/${id}/edit`}
          className="bg-yellow-500 text-white px-4 py-1 rounded"
        >
          수정
        </Link>
        <button
          onClick={handleDelete}
          className="bg-red-500 text-white px-4 py-1 rounded"
        >
          삭제
        </button>
      </div>
    </div>
  );
}
