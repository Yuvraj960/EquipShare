<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <span class="auth-icon">🚀</span>
        <h2>Create Account</h2>
        <p>Join the EquipShare community today</p>
      </div>

      <div v-if="error" class="alert alert-danger">
        ⚠️ {{ error }}
      </div>

      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="form-group">
          <label>Email Address</label>
          <input 
            v-model="email" 
            type="email" 
            placeholder="you@university.edu" 
            required 
            autocomplete="email"
          />
        </div>

        <div class="form-group">
          <label>Username</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="johndoe" 
            required 
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label>Password (at least 6 characters)</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="••••••••" 
            required 
            minlength="6"
            autocomplete="new-password"
          />
        </div>

        <button type="submit" class="btn-submit" :disabled="loading">
          {{ loading ? 'Creating Account...' : 'Sign Up & Get Started' }}
        </button>
      </form>

      <div class="auth-footer">
        Already have an account? <router-link to="/login">Log in here</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../store/auth'

const email = ref('')
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const router = useRouter()
const auth = useAuthStore()

async function handleRegister() {
  error.value = ''
  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }

  loading.value = true
  try {
    await auth.register(email.value, username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.error || 'Registration failed. Try a different username or email.'
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
