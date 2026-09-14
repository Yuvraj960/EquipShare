<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <span class="auth-icon">🔐</span>
        <h2>Welcome Back</h2>
        <p>Log in to your EquipShare account</p>
      </div>

      <div v-if="error" class="alert alert-danger">
        ⚠️ {{ error }}
      </div>

      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="form-group">
          <label>Email Address</label>
          <input 
            v-model="email" 
            type="email" 
            placeholder="you@example.com" 
            required 
            autocomplete="email"
          />
        </div>

        <div class="form-group">
          <label>Password</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="••••••••" 
            required 
            autocomplete="current-password"
          />
        </div>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Signing In...' : 'Log In' }}
        </button>
      </form>

      <!-- Quick Demo Account Fillers -->
      <div class="demo-accounts">
        <span class="demo-title">Quick Demo Login:</span>
        <div class="demo-buttons">
          <button type="button" @click="fillDemo('yuvraj@equipshare.test', 'user123')" class="btn-demo">
            User: Yuvraj
          </button>
          <button type="button" @click="fillDemo('ananya@equipshare.test', 'user123')" class="btn-demo">
            User: Ananya
          </button>
          <button type="button" @click="fillDemo('admin@equipshare.test', 'admin123')" class="btn-demo admin">
            Admin: admin
          </button>
        </div>
      </div>

      <div class="auth-footer">
        Don't have an account? <router-link to="/register">Create one here</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth'

const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

function fillDemo(demoEmail, demoPass) {
  email.value = demoEmail
  password.value = demoPass
  error.value = ''
}

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to sign in. Check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem 0;
}

.auth-card {
  background: white;
  border-radius: 16px;
  border: 1px solid var(--border);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
  width: 100%;
  max-width: 440px;
  padding: 2.25rem 2rem;
}

.auth-header {
  text-align: center;
  margin-bottom: 1.75rem;
}

.auth-icon {
  font-size: 2.25rem;
  display: block;
  margin-bottom: 0.5rem;
}

.auth-header h2 {
  font-size: 1.65rem;
  font-weight: 800;
  color: #0f172a;
}

.auth-header p {
  color: var(--text-muted);
  font-size: 0.92rem;
  margin-top: 0.25rem;
}

.btn-submit {
  width: 100%;
  background: var(--primary);
  color: white;
  border: none;
  padding: 0.8rem;
  border-radius: 8px;
  font-weight: 700;
  font-size: 1rem;
  margin-top: 0.5rem;
  transition: background 0.15s ease;
}

.btn-submit:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.demo-accounts {
  margin-top: 1.75rem;
  padding-top: 1.5rem;
  border-top: 1px dashed var(--border);
  text-align: center;
}

.demo-title {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-muted);
  display: block;
  margin-bottom: 0.6rem;
}

.demo-buttons {
  display: flex;
  gap: 0.4rem;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-demo {
  background: #f1f5f9;
  border: 1px solid var(--border);
  color: #334155;
  font-size: 0.78rem;
  font-weight: 600;
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-demo:hover {
  background: #e2e8f0;
}

.btn-demo.admin {
  background: #fef3c7;
  border-color: #fde68a;
  color: #92400e;
}

.auth-footer {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.88rem;
  color: var(--text-muted);
}

.auth-footer a {
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
}

.auth-footer a:hover {
  text-decoration: underline;
}
</style>
