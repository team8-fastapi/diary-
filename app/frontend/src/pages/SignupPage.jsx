// src/pages/SignupPage.jsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { signup } from "../api/auth";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nickname, setNickname] = useState("");
  const navigate = useNavigate();

  const handleSignup = async (e) => {
    e.preventDefault();
    try {
      await signup({ email, password, nickname });
      navigate("/login");
    } catch (err) {
      alert("회원가입 실패");
    }
  };

  return (
    <form onSubmit={handleSignup} className="max-w-md mx-auto mt-10 space-y-4">
      <h1 className="text-2xl font-bold">회원가입</h1>
      <input
        className="w-full border px-3 py-2 rounded"
        placeholder="이메일"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <input
        className="w-full border px-3 py-2 rounded"
        placeholder="닉네임"
        value={nickname}
        onChange={(e) => setNickname(e.target.value)}
      />
      <input
        className="w-full border px-3 py-2 rounded"
        placeholder="비밀번호"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <button className="bg-green-600 text-white px-4 py-2 rounded w-full">가입하기</button>
    </form>
  );
}
