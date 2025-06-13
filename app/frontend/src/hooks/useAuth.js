// hooks/useAuth.js
import { useEffect, useState } from 'react';
import { getMe } from '../api/auth';

export default function useAuth() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    getMe()
      .then(res => setUser(res.data))
      .catch(() => setUser(null));
  }, []);

  return user;
}
