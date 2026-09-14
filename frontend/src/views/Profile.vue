<template>
  <div class="profile-page">
    <div class="page-header">
      <h1 class="page-title">User Profile & Account</h1>
      <p class="page-subtitle">Manage your personal details, credentials, and view sharing statistics</p>
    </div>

    <div v-if="successMsg" class="alert alert-success">
      ✅ {{ successMsg }}
    </div>
    <div v-if="errorMsg" class="alert alert-danger">
      ⚠️ {{ errorMsg }}
    </div>

    <div class="profile-layout">
      <!-- Profile Summary Card -->
      <div class="profile-card">
        <div class="user-avatar-large">👤</div>
        <h2 class="user-name">{{ user?.username }}</h2>
        <span class="user-email">{{ user?.email }}</span>

        <div class="roles-box">
          <span v-for="r in user?.roles" :key="r" class="role-badge">
            {{ r }}
          </span>
        </div>

        <div class="stats-overview">
          <div class="stat-box">
            <span class="stat-n">{{ user?.equipment_count || 0 }}</span>
            <span class="stat-l">Gear Listed</span>
          </div>
          <div class="stat-box">
            <span class="stat-n">{{ user?.rentals_made_count || 0 }}</span>
            <span class="stat-l">Rentals Taken</span>
          </div>
          <div class="stat-box">
            <span class="stat-n">{{ user?.rentals_received_count || 0 }}</span>
            <span class="stat-l">Rentals Lent</span>
          </div>
        </div>

        <div class="member-since">
          Member since {{ formatDate(user?.created_at) }}
        </div>
      </div>

      <!-- Account Settings Form -->
      <div class="settings-card">
        <h3>Edit Profile & Security</h3>

        <form @submit.prevent="updateProfile">
          <div class="form-group">
            <label>Username</label>
            <input v-model="form.username" type="text" required />
          </div>

          <div class="form-group">
            <label>Email Address</label>
            <input :value="user?.email" type="email" disabled class="disabled-input" />
            <small class="hint">Email address cannot be changed directly.</small>
          </div>

          <hr class="divider" />

          <h4>Change Password</h4>
          <p class="form-sub">Leave blank if you don't wish to change your password.</p>

          <div class="form-group">
            <label>Current Password</label>
            <input 
              v-model="form.current_password" 
              type="password" 
              placeholder="••••••••" 
            />
          </div>

          <div class="form-group">
            <label>New Password (min. 6 characters)</label>
            <input 
              v-model="form.new_password" 
              type="password" 
              placeholder="••••••••" 
              minlength="6"
            />
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Saving Changes...' : 'Save Profile Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import client from '../api/client'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const user = ref(null)
const saving = ref(false)
const successMsg = ref('')
const errorMsg = ref('')

const form = reactive({
  username: '',
  current_password: '',
  new_password: ''
})

function formatDate(iso) {
  if (!iso) return '2026'
  return new Date(iso).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
}

async function loadProfile() {
  try {
    const data = await auth.fetchMe()
    user.value = data
    form.username = data.username
  } catch (err) {
    errorMsg.value = 'Failed to load profile details'
  }
}

async function updateProfile() {
  errorMsg.value = ''
  successMsg.value = ''

  if (form.new_password && !form.current_password) {
    errorMsg.value = 'Please provide your current password to set a new password.'
    return
  }

  saving.value = true
  try {
    const res = await client.put('/auth/profile', {
      username: form.username,
      current_password: form.current_password,
      new_password: form.new_password
    })
    user.value = res.data.user
    form.current_password = ''
    form.new_password = ''
    successMsg.value = 'Profile updated successfully!'
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to update profile.'
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-page {
  max-width: 960px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-title {
  font-size: 2.1rem;
  font-weight: 800;
  color: #0f172a;
}

.page-subtitle {
  color: var(--text-muted);
}

.profile-layout {
  display: grid;
  grid-template-columns: 1fr 1.6fr;
  gap: 2rem;
  align-items: flex-start;
}

.profile-card, .settings-card {
  background: white;
  border-radius: 14px;
  border: 1px solid var(--border);
  padding: 2rem;
  box-shadow: var(--shadow);
}

.profile-card {
  text-align: center;
}

.user-avatar-large {
  font-size: 3.5rem;
  background: #f1f5f9;
  width: 90px;
  height: 90px;
  border-radius: 9999px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
}

.user-name {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
}

.user-email {
  color: var(--text-muted);
  font-size: 0.9rem;
  display: block;
  margin-bottom: 1rem;
}

.roles-box {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  margin-bottom: 1.5rem;
}

.role-badge {
  background: #eff6ff;
  color: #1d4ed8;
  font-weight: 700;
  font-size: 0.75rem;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
}

.stats-overview {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.5rem;
  background: #f8fafc;
  padding: 1rem;
  border-radius: 10px;
  margin-bottom: 1.5rem;
}

.stat-box {
  display: flex;
  flex-direction: column;
}

.stat-n {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
}

.stat-l {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.member-since {
  font-size: 0.8rem;
  color: var(--text-muted);
}

/* Settings Card */
.settings-card h3 {
  font-size: 1.3rem;
  font-weight: 800;
  margin-bottom: 1.5rem;
}

.settings-card h4 {
  font-size: 1.05rem;
  font-weight: 700;
  margin-top: 1.5rem;
  margin-bottom: 0.25rem;
}

.form-sub {
  color: var(--text-muted);
  font-size: 0.85rem;
  margin-bottom: 1rem;
}

.disabled-input {
  background: #f1f5f9;
  cursor: not-allowed;
  color: var(--text-muted);
}

.hint {
  font-size: 0.78rem;
  color: var(--text-muted);
  display: block;
  margin-top: 0.25rem;
}

.divider {
  border: 0;
  border-top: 1px solid var(--border);
  margin: 1.5rem 0;
}

.form-actions {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
}

@media (max-width: 768px) {
  .profile-layout {
    grid-template-columns: 1fr;
  }
}
</style>
