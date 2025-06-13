import axios from './axiosInstance';

export const signup = (data) => axios.post('/auth/signup', data);
export const login = (data) => axios.post('/auth/login', data);
export const getMe = () => axios.get('/auth/me');
export const updateMe = (data) => axios.patch('/auth/me', data);
export const deleteMe = () => axios.delete('/auth/me');
export const logout = () => axios.post('/auth/logout');
