// src/components/Navbar.jsx
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import { logout } from "../api/auth";

export default function Navbar() {
  const { user, refetch } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    await refetch(); // useAuth 상태 초기화
    navigate("/login");
  };

  return (
    <nav className="bg-white border-b shadow-sm px-4 py-3 flex justify-between items-center">
      <Link to="/" className="text-xl font-bold text-blue-600">
        📘 Diary App
      </Link>

      <div className="space-x-4">
        {user ? (
          <>
            <Link to="/mypage" className="text-gray-700 hover:underline">
              마이페이지
            </Link>
            <button
              onClick={handleLogout}
              className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600"
            >
              로그아웃
            </button>
          </>
        ) : (
          <>
            <Link to="/login" className="text-gray-700 hover:underline">
              로그인
            </Link>
            <Link to="/signup" className="text-gray-700 hover:underline">
              회원가입
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}
