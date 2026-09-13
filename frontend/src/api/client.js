import axios from 'axios'

const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' }
})

client.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers['Authentication-Token'] = token
  }
  return config
})

client.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // If unauthorized and not on auth pages, clear invalid token and redirect
      const path = window.location.pathname
      if (localStorage.getItem('token') && !path.includes('/login') && !path.includes('/register')) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export default client
