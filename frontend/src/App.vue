<template>
  <div class="app-layout">
    <header class="navbar">
      <div class="nav-container">
        <router-link to="/" class="brand">
          <span class="brand-icon">🔄</span>
          <div class="brand-text">
            <span class="brand-name">EquipShare</span>
            <span class="brand-tagline">Equipment Rental & Sharing</span>
          </div>
        </router-link>

        <nav class="nav-links">
          <router-link to="/" class="nav-item">Home</router-link>
          <router-link to="/equipment" class="nav-item">Browse</router-link>

          <template v-if="auth.isAuthenticated">
            <router-link to="/add-equipment" class="nav-item btn-list-gear">+ List Equipment</router-link>
            <router-link to="/my-equipment" class="nav-item">My Listings</router-link>
            <router-link to="/rental-requests" class="nav-item">Requests</router-link>
            <router-link to="/my-rentals" class="nav-item">My Rentals</router-link>
            <router-link to="/notifications" class="nav-item notif-link">
              Notifications
              <span v-if="auth.unreadCount > 0" class="badge">{{ auth.unreadCount }}</span>
            </router-link>
            <router-link v-if="auth.isAdmin" to="/admin" class="nav-item admin-badge">
              🛡️ Admin
            </router-link>
          </template>
        </nav>

        <div class="nav-user">
          <template v-if="auth.isAuthenticated">
            <router-link to="/profile" class="user-pill" title="View Profile">
              <span class="user-avatar">👤</span>
              <span class="user-name">{{ auth.currentUsername }}</span>
            </router-link>
            <button @click="handleLogout" class="btn-logout" title="Sign out">Logout</button>
          </template>
          <template v-else>
            <router-link to="/login" class="btn-secondary">Log In</router-link>
            <router-link to="/register" class="btn-primary">Sign Up</router-link>
          </template>
        </div>
      </div>
    </header>

    <main class="main-content">
      <router-view />
    </main>

    <footer class="footer">
      <div class="footer-container">
        <div class="footer-col">
          <h3>EquipShare</h3>
          <p>Community-powered peer-to-peer equipment rental. Share resources, reduce waste, and build connections in universities, makerspaces, and local communities.</p>
        </div>
        <div class="footer-col">
          <h4>Explore</h4>
          <router-link to="/equipment">Browse Equipment</router-link>
          <router-link to="/add-equipment">List Your Gear</router-link>
          <router-link to="/my-rentals">Track Rentals</router-link>
        </div>
        <div class="footer-col">
          <h4>Accounts & Roles</h4>
          <p><strong>USER:</strong> List, browse, rent, review</p>
          <p><strong>ADMIN:</strong> Moderation, metrics, category management</p>
          <p class="copyright">© 2026 EquipShare Platform. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from './store/auth'

const router = useRouter()
const auth = useAuthStore()

onMounted(async () => {
  if (auth.isAuthenticated) {
    try {
      await auth.fetchMe()
      await auth.fetchUnreadCount()
    } catch (e) {
      console.warn('Initial auth fetch error', e)
    }
  }
})

async function handleLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style>
:root {
  --primary: #1d4ed8;
  --primary-hover: #1e40af;
  --primary-light: #eff6ff;
  --secondary: #475569;
  --success: #16a34a;
  --warning: #d97706;
  --danger: #dc2626;
  --bg-app: #f8fafc;
  --bg-card: #ffffff;
  --border: #e2e8f0;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --radius: 10px;
  --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Inter', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  background-color: var(--bg-app);
  color: var(--text-main);
  line-height: 1.6;
  min-height: 100vh;
}

.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Navbar */
.navbar {
  background: #ffffff;
  border-bottom: 1px solid var(--border);
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1240px;
  margin: 0 auto;
  padding: 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  color: inherit;
}

.brand-icon {
  font-size: 1.75rem;
  background: var(--primary-light);
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-name {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--primary);
  letter-spacing: -0.02em;
}

.brand-tagline {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: 500;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.nav-item {
  color: var(--secondary);
  text-decoration: none;
  font-size: 0.92rem;
  font-weight: 500;
  padding: 0.5rem 0.85rem;
  border-radius: 8px;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.nav-item:hover {
  color: var(--primary);
  background: var(--primary-light);
}

.nav-item.router-link-active {
  color: var(--primary);
  font-weight: 600;
  background: var(--primary-light);
}

.btn-list-gear {
  background: #2563eb;
  color: white !important;
  font-weight: 600;
}

.btn-list-gear:hover {
  background: #1d4ed8 !important;
}

.badge {
  background: var(--danger);
  color: white;
  font-size: 0.7rem;
  padding: 0.15rem 0.45rem;
  border-radius: 9999px;
  font-weight: 700;
}

.admin-badge {
  background: #fef3c7;
  color: #92400e !important;
  font-weight: 600;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-pill {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: #f1f5f9;
  padding: 0.4rem 0.75rem;
  border-radius: 9999px;
  text-decoration: none;
  color: var(--text-main);
  font-size: 0.88rem;
  font-weight: 600;
  transition: background 0.15s ease;
}

.user-pill:hover {
  background: #e2e8f0;
}

.btn-logout {
  background: transparent;
  border: 1px solid var(--border);
  color: var(--secondary);
  font-size: 0.85rem;
  padding: 0.45rem 0.85rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.15s ease;
}

.btn-logout:hover {
  background: #fee2e2;
  color: var(--danger);
  border-color: #fca5a5;
}

.btn-primary {
  background: var(--primary);
  color: white;
  text-decoration: none;
  padding: 0.5rem 1.1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  transition: background 0.15s ease;
}

.btn-primary:hover {
  background: var(--primary-hover);
}

.btn-secondary {
  background: transparent;
  color: var(--primary);
  border: 1px solid var(--primary);
  text-decoration: none;
  padding: 0.45rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  transition: all 0.15s ease;
}

.btn-secondary:hover {
  background: var(--primary-light);
}

/* Main Content */
.main-content {
  flex: 1;
  max-width: 1240px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem 1.5rem 3rem 1.5rem;
}

/* Global Card & Form Styling */
.card {
  background: var(--bg-card);
  border-radius: var(--radius);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.form-group {
  margin-bottom: 1.25rem;
}

.form-group label {
  display: block;
  font-size: 0.88rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
  color: var(--text-main);
}

input, select, textarea {
  width: 100%;
  padding: 0.65rem 0.9rem;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 0.95rem;
  background: #ffffff;
  color: var(--text-main);
  transition: border-color 0.15s, box-shadow 0.15s;
}

input:focus, select:focus, textarea:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}

button {
  cursor: pointer;
}

/* Alerts */
.alert {
  padding: 0.85rem 1.25rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 0.92rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.alert-danger {
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: var(--danger);
}

.alert-success {
  background: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: var(--success);
}

.alert-info {
  background: #eff6ff;
  border: 1px solid #bfdbfe;
  color: var(--primary);
}

/* Footer */
.footer {
  background: #0f172a;
  color: #94a3b8;
  padding: 3rem 1.5rem 2rem;
  margin-top: auto;
  border-top: 1px solid #1e293b;
}

.footer-container {
  max-width: 1240px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 2fr 1fr 1.5fr;
  gap: 2.5rem;
}

.footer-col h3 {
  color: #ffffff;
  margin-bottom: 0.75rem;
  font-size: 1.25rem;
}

.footer-col h4 {
  color: #e2e8f0;
  margin-bottom: 0.75rem;
  font-size: 1rem;
}

.footer-col p {
  font-size: 0.88rem;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.footer-col a {
  display: block;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.88rem;
  margin-bottom: 0.5rem;
  transition: color 0.15s ease;
}

.footer-col a:hover {
  color: #ffffff;
}

.copyright {
  margin-top: 1rem;
  font-size: 0.8rem;
  color: #64748b;
}

@media (max-width: 860px) {
  .nav-container {
    flex-direction: column;
    align-items: flex-start;
  }
  .footer-container {
    grid-template-columns: 1fr;
  }
}
</style>
