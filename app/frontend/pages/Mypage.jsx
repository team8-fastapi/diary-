// src/pages/MyPage.jsx
import { useEffect, useState } from "react";
import api from "../api/axios";

export default function MyPage() {
  const [me, setMe] = useState(null);

  useEffect(() => {
    api.get("/auth/me").then(res => setMe(res.data)).catch(() => alert("로그인 필요"));
  }, []);

  const handleLogout = async () => {
    await api.post("/auth/logout");
    alert("로그아웃!");
  };

  const handleDelete = async () => {
    await api.delete("/auth/me");
    alert("계정 삭제됨");
  };

  if (!me) return <div>Loading...</div>;

  return (
    <div>
      <h2>My Info</h2>
      <p>Email: {me.email}</p>
      <p>Name: {me.name}</p>
      <button onClick={handleLogout}>Logout</button>
      <button onClick={handleDelete}>Delete Account</button>
    </div>
  );
}
