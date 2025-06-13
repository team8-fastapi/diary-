// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import MyPage from "./pages/MyPage";
import DiaryListPage from "./pages/DiaryListPage";
import DiaryDetailPage from "./pages/DiaryDetailPage";
import DiaryCreatePage from "./pages/DiaryCreatePage";
import DiaryEditPage from "./pages/DiaryEditPage";
import Header from "./components/Header";
import { AuthProvider } from "./hooks/useAuth";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Header />
        <Routes>
          <Route path="/" element={<DiaryListPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/me" element={<MyPage />} />
          <Route path="/diaries/new" element={<DiaryCreatePage />} />
          <Route path="/diaries/:id" element={<DiaryDetailPage />} />
          <Route path="/diaries/:id/edit" element={<DiaryEditPage />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
