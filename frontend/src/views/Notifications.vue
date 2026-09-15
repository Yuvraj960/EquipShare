<template>
  <div class="notifications-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Notifications</h1>
        <p class="page-subtitle">Alerts regarding your rental requests, approvals, returns, and reviews</p>
      </div>

      <button 
        v-if="unreadCount > 0" 
        @click="markAllAsRead" 
        class="btn-secondary"
      >
        ✓ Mark All as Read ({{ unreadCount }})
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="state-card">
      <p>Loading your notifications...</p>
    </div>

    <!-- Empty -->
    <div v-else-if="notifications.length === 0" class="empty-card">
      <span class="empty-icon">🔔</span>
      <h3>No notifications yet</h3>
      <p>You're all caught up! Updates regarding booking requests, reminders, and reviews will appear here.</p>
    </div>

    <!-- Notifications List -->
    <div v-else class="notifications-list">
      <div 
        v-for="n in notifications" 
        :key="n.id" 
        :class="['notif-item', { unread: !n.read }]"
      >
        <div class="notif-icon">
          <span v-if="n.message.includes('APPROVED')">🎉</span>
          <span v-else-if="n.message.includes('request')">📬</span>
          <span v-else-if="n.message.includes('returned')">🤝</span>
          <span v-else-if="n.message.includes('review')">⭐</span>
          <span v-else-if="n.message.includes('Reminder')">⏰</span>
          <span v-else>ℹ️</span>
        </div>

        <div class="notif-content">
          <p class="notif-msg">{{ n.message }}</p>
          <span class="notif-time">{{ formatDate(n.created_at) }}</span>
        </div>

        <div class="notif-actions">
          <button 
            v-if="!n.read" 
            @click="markRead(n.id)" 
            class="btn-icon" 
            title="Mark as read"
          >
            ✓
          </button>
          <button 
            @click="deleteNotif(n.id)" 
            class="btn-icon delete" 
            title="Delete notification"
          >
            ✕
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import client from '../api/client'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()
const notifications = ref([])
const loading = ref(true)

const unreadCount = computed(() => {
  return notifications.value.filter(n => !n.read).length
})

function formatDate(iso) {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) + ' at ' + d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

async function fetchNotifications() {
  loading.value = true
  try {
    const res = await client.get('/notifications')
    notifications.value = res.data.notifications || []
    auth.unreadCount = res.data.unread_count || 0
  } catch (err) {
    console.error('Failed to load notifications', err)
  } finally {
    loading.value = false
  }
}

async function markRead(id) {
  try {
    await client.put(`/notifications/${id}/read`)
    const found = notifications.value.find(n => n.id === id)
    if (found) found.read = true
    auth.fetchUnreadCount()
  } catch (err) {
    console.error(err)
  }
}

async function markAllAsRead() {
  try {
    await client.put('/notifications/read-all')
    notifications.value.forEach(n => { n.read = true })
    auth.unreadCount = 0
  } catch (err) {
    console.error(err)
  }
}

async function deleteNotif(id) {
  try {
    await client.delete(`/notifications/${id}`)
    notifications.value = notifications.value.filter(n => n.id !== id)
    auth.fetchUnreadCount()
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  fetchNotifications()
})
</script>

<style scoped>
.notifications-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 2.1rem;
  font-weight: 800;
  color: #0f172a;
}

.page-subtitle {
  color: var(--text-muted);
}

.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.notif-item {
  background: white;
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 1.25rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  box-shadow: var(--shadow);
  transition: all 0.15s ease;
}

.notif-item.unread {
  border-left: 4px solid var(--primary);
  background: #f8fbff;
}

.notif-icon {
  font-size: 1.75rem;
}

.notif-content {
  flex: 1;
}

.notif-msg {
  font-size: 0.98rem;
  color: #1e293b;
  margin-bottom: 0.25rem;
  line-height: 1.4;
}

.notif-time {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.notif-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  background: #f1f5f9;
  border: none;
  width: 34px;
  height: 34px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: var(--secondary);
  font-weight: 700;
  font-size: 0.9rem;
  transition: all 0.15s ease;
}

.btn-icon:hover {
  background: #e2e8f0;
  color: var(--text-main);
}

.btn-icon.delete:hover {
  background: #fee2e2;
  color: var(--danger);
}

.state-card, .empty-card {
  background: white;
  border-radius: 14px;
  border: 1px solid var(--border);
  padding: 3.5rem 2rem;
  text-align: center;
}

.empty-icon {
  font-size: 3rem;
  display: block;
  margin-bottom: 1rem;
}

.empty-card h3 {
  font-size: 1.35rem;
  margin-bottom: 0.5rem;
}

.empty-card p {
  color: var(--text-muted);
}
</style>
