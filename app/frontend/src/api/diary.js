import axios from './axiosInstance';

export const createDiary = (data) => axios.post('/diaries', data);
export const getDiaries = (skip = 0, limit = 10) =>
  axios.get(`/diaries?skip=${skip}&limit=${limit}`);
export const getDiary = (id) => axios.get(`/diaries/${id}`);
export const updateDiary = (id, data) => axios.patch(`/diaries/${id}`, data);
export const deleteDiary = (id) => axios.delete(`/diaries/${id}`);
