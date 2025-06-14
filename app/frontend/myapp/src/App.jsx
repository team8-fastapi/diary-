// src/App.jsx
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Login from "../../pages/Login.jsx";
import Signup from "../../pages/Signup.jsx";
import DiaryList from "../../pages/DiaryList.jsx";
import DiaryForm from "../../pages/DiaryForm.jsx";
import MyPage from "../../pages/Mypage.jsx";

function App() {
  return (
    <Router>
      <nav>
        <Link to="/">Diaries</Link> | <Link to="/login">Login</Link> |{" "}
        <Link to="/signup">Signup</Link> | <Link to="/me">My Page</Link>
      </nav>
      <Routes>
        <Route path="/" element={<DiaryList />} />
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/new" element={<DiaryForm />} />
        <Route path="/edit/:id" element={<DiaryForm editMode />} />
        <Route path="/me" element={<MyPage />} />
      </Routes>
    </Router>
  );
}

export default App;
