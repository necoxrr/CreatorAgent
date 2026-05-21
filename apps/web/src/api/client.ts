import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' }
})

api.interceptors.response.use(
  res => {
    if (res.data.code !== 0) throw new Error(res.data.message)
    return res.data.data
  },
  err => Promise.reject(err)
)

export default api