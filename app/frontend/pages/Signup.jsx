// src/pages/Signup.jsx
import { useState } from "react";
import api from "../api/axios";

export default function Signup() {
  const [form, setForm] = useState({ email: "", password: "", name: "" });

  const handleSignup = async () => {
    try {
      await api.post("/auth/signup", form);
      alert("회원가입 성공!");
    } catch {
      alert("회원가입 실패");
    }
  };

  return (
    <div>
      <h2>Signup</h2>
      <input placeholder="Email" onChange={e => setForm({ ...form, email: e.target.value })} />
      <input placeholder="Name" onChange={e => setForm({ ...form, name: e.target.value })} />
      <input type="password" placeholder="Password" onChange={e => setForm({ ...form, password: e.target.value })} />
      <button onClick={handleSignup}>Signup</button>
    </div>
  );
}
