// src/api/axios.js
import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000", // FastAPI 주소
  withCredentials: true, // 쿠키 포함
});

export default api;
