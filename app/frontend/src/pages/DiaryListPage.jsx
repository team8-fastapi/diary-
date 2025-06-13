// src/pages/DiaryListPage.jsx
import { useEffect, useState } from "react";
import { getDiaries } from "../api/diaries";
import DiaryCard from "../components/DiaryCard";
import { Link } from "react-router-dom";

export default function DiaryListPage() {
  const [diaries, setDiaries] = useState([]);

  useEffect(() => {
    getDiaries().then(setDiaries);
  }, []);

  return (
    <div className="max-w-2xl mx-auto mt-8 space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-bold">📒 나의 다이어리</h1>
        <Link
          to="/diaries/new"
          className="bg-blue-500 text-white px-4 py-1 rounded hover:bg-blue-600"
        >
          새 다이어리
        </Link>
      </div>
      {diaries.length === 0 ? (
        <p>작성한 다이어리가 없습니다.</p>
      ) : (
        diaries.map((diary) => <DiaryCard key={diary.id} diary={diary} />)
      )}
    </div>
  );
}

