// src/pages/MyPage.jsx
import { useAuth } from "../hooks/useAuth";

export default function MyPage() {
  const { user } = useAuth();

  if (!user) return <p>Loading...</p>;

  return (
    <div className="max-w-md mx-auto mt-10 space-y-4">
      <h1 className="text-2xl font-bold">마이페이지</h1>
      <p><strong>이메일:</strong> {user.email}</p>
      <p><strong>닉네임:</strong> {user.nickname}</p>
    </div>
  );
}
