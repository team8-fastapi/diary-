// src/components/DiaryCard.jsx
import { Link } from "react-router-dom";

export default function DiaryCard({ diary }) {
  return (
    <div className="bg-white rounded-xl shadow p-4 hover:shadow-md transition">
      <h2 className="text-lg font-semibold text-gray-800">{diary.title}</h2>
      <p className="text-gray-600 text-sm mt-1">{diary.content.slice(0, 100)}...</p>
      <div className="text-right mt-3">
        <Link
          to={`/diaries/${diary.id}`}
          className="text-blue-500 hover:underline text-sm"
        >
          자세히 보기 →
        </Link>
      </div>
    </div>
  );
}
