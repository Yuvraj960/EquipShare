<template>
  <div class="admin-dashboard-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">🛡️ Admin Dashboard</h1>
        <p class="page-subtitle">System-wide monitoring, category management, user moderation, and scheduled maintenance</p>
      </div>
      <button @click="triggerScheduledTasks" class="btn-maintenance" :disabled="runningTasks">
        {{ runningTasks ? 'Running Tasks...' : '⚡ Run Maintenance Tasks' }}
      </button>
    </div>

    <!-- Feedback alerts -->
    <div v-if="successMsg" class="alert alert-success">
      ✅ {{ successMsg }}
    </div>
    <div v-if="errorMsg" class="alert alert-danger">
      ⚠️ {{ errorMsg }}
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid" v-if="stats">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-data">
          <span class="stat-value">{{ stats.total_users }}</span>
          <span class="stat-name">Registered Users</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">📷</div>
        <div class="stat-data">
          <span class="stat-value">{{ stats.total_equipment }}</span>
          <span class="stat-name">Listed Equipment ({{ stats.available_equipment }} available)</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">🤝</div>
        <div class="stat-data">
          <span class="stat-value">{{ stats.active_rentals }}</span>
          <span class="stat-name">Active Rentals ({{ stats.completed_rentals }} completed)</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">💰</div>
        <div class="stat-data">
          <span class="stat-value">₹{{ stats.total_revenue }}</span>
          <span class="stat-name">Total Platform Volume</span>
        </div>
      </div>
    </div>

    <!-- Admin Tabs -->
    <div class="admin-tabs">
      <button 
        :class="['tab-btn', { active: currentTab === 'categories' }]"
        @click="currentTab = 'categories'"
      >
        📂 Categories ({{ categories.length }})
      </button>

      <button 
        :class="['tab-btn', { active: currentTab === 'users' }]"
        @click="currentTab = 'users'"
      >
        👥 Users ({{ users.length }})
      </button>

      <button 
        :class="['tab-btn', { active: currentTab === 'equipment' }]"
        @click="currentTab = 'equipment'"
      >
        📦 All Equipment ({{ allEquipment.length }})
      </button>

      <button 
        :class="['tab-btn', { active: currentTab === 'reports' }]"
        @click="currentTab = 'reports'"
      >
        🚩 Reports ({{ reports.length }})
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="state-card">
      <p>Loading administration data...</p>
    </div>

    <!-- TAB 1: Categories -->
    <div v-else-if="currentTab === 'categories'" class="tab-pane">
      <div class="pane-header">
        <h3>Equipment Categories</h3>
        <button @click="showAddCatModal = true" class="btn-primary btn-sm">+ Add New Category</button>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Category Name</th>
              <th>Description</th>
              <th>Available Gear</th>
              <th>Total Gear</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in categories" :key="c.id">
              <td>#{{ c.id }}</td>
              <td><strong>{{ c.name }}</strong></td>
              <td>{{ c.description }}</td>
              <td><span class="badge-count">{{ c.equipment_count }}</span></td>
              <td>{{ c.total_equipment_count }}</td>
              <td>
                <button @click="deleteCategory(c)" class="btn-danger-outline btn-sm">Delete</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 2: Users -->
    <div v-else-if="currentTab === 'users'" class="tab-pane">
      <div class="pane-header">
        <h3>User Accounts & Access</h3>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Username</th>
              <th>Email</th>
              <th>Roles</th>
              <th>Listings</th>
              <th>Rentals</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in users" :key="u.id">
              <td>#{{ u.id }}</td>
              <td><strong>{{ u.username }}</strong></td>
              <td>{{ u.email }}</td>
              <td>
                <span v-for="r in u.roles" :key="r" class="role-pill">{{ r }}</span>
              </td>
              <td>{{ u.equipment_count }}</td>
              <td>{{ u.rentals_count }}</td>
              <td>
                <span :class="['status-tag', u.active ? 'active' : 'inactive']">
                  {{ u.active ? 'Active' : 'Deactivated' }}
                </span>
              </td>
              <td>
                <button 
                  v-if="u.id !== auth.user?.id" 
                  @click="toggleUserStatus(u)" 
                  :class="['btn-sm', u.active ? 'btn-danger-outline' : 'btn-approve']"
                >
                  {{ u.active ? 'Deactivate' : 'Activate' }}
                </button>
                <span v-else class="text-muted">(You)</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 3: All Equipment -->
    <div v-else-if="currentTab === 'equipment'" class="tab-pane">
      <div class="pane-header">
        <h3>Equipment Inventory Moderation</h3>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Category</th>
              <th>Owner</th>
              <th>Daily Rate</th>
              <th>Status</th>
              <th>Location</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="e in allEquipment" :key="e.id">
              <td>#{{ e.id }}</td>
              <td>
                <router-link :to="'/equipment/' + e.id" class="equip-link"><strong>{{ e.name }}</strong></router-link>
              </td>
              <td>{{ e.category_name }}</td>
              <td>👤 {{ e.owner_username }}</td>
              <td>₹{{ e.price_per_day }}</td>
              <td>
                <span :class="['status-tag', e.availability_status]">
                  {{ e.availability_status }}
                </span>
              </td>
              <td>{{ e.location }}</td>
              <td>
                <button @click="deleteEquipmentListing(e)" class="btn-danger-outline btn-sm">Remove</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- TAB 4: Reports -->
    <div v-else-if="currentTab === 'reports'" class="tab-pane">
      <div class="pane-header">
        <h3>Reported Listings & Community Flags</h3>
      </div>

      <div v-if="reports.length === 0" class="empty-card">
        <h3>No pending reports</h3>
        <p>No user or equipment reports currently on file.</p>
      </div>

      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Reporter</th>
              <th>Target</th>
              <th>Reason</th>
              <th>Status</th>
              <th>Date</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in reports" :key="r.id">
              <td>#{{ r.id }}</td>
              <td>👤 {{ r.reporter_username }}</td>
              <td>
                <span v-if="r.equipment_name">Item: <strong>{{ r.equipment_name }}</strong></span>
                <span v-else-if="r.reported_username">User: <strong>{{ r.reported_username }}</strong></span>
                <span v-else>General report</span>
              </td>
              <td class="reason-cell">{{ r.reason }}</td>
              <td>
                <span :class="['status-tag', r.status.toLowerCase()]">{{ r.status }}</span>
              </td>
              <td>{{ formatDate(r.created_at) }}</td>
              <td>
                <button 
                  v-if="r.status === 'OPEN'" 
                  @click="resolveReport(r)" 
                  class="btn-approve btn-sm"
                >
                  Resolve
                </button>
                <span v-else class="text-muted">Resolved</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add Category Modal -->
    <div v-if="showAddCatModal" class="modal-backdrop" @click.self="showAddCatModal = false">
      <div class="modal-card">
        <h3>Add Equipment Category</h3>
        <p class="modal-sub">Create a new category for community members to browse.</p>

        <form @submit.prevent="createCategory">
          <div class="form-group">
            <label>Category Name *</label>
            <input v-model="newCatName" type="text" placeholder="e.g. Drones & Aerial" required />
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea v-model="newCatDesc" rows="3" placeholder="Brief summary of items in this category..."></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showAddCatModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="addingCat">Create Category</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '../api/client'
import { useAuthStore } from '../store/auth'

const auth = useAuthStore()

const currentTab = ref('categories')
const stats = ref(null)
const categories = ref([])
const users = ref([])
const allEquipment = ref([])
const reports = ref([])
const loading = ref(true)

const successMsg = ref('')
const errorMsg = ref('')
const runningTasks = ref(false)

// Add Category
const showAddCatModal = ref(false)
const newCatName = ref('')
const newCatDesc = ref('')
const addingCat = ref(false)

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

async function loadDashboard() {
  loading.value = true
  try {
    const [sRes, cRes, uRes, eRes, rRes] = await Promise.all([
      client.get('/admin/stats'),
      client.get('/categories'),
      client.get('/admin/users'),
      client.get('/admin/equipment'),
      client.get('/admin/reports')
    ])
    stats.value = sRes.data
    categories.value = cRes.data
    users.value = uRes.data
    allEquipment.value = eRes.data
    reports.value = rRes.data
  } catch (err) {
    errorMsg.value = 'Failed to load administrator data'
  } finally {
    loading.value = false
  }
}

async function triggerScheduledTasks() {
  runningTasks.value = true
  errorMsg.value = ''
  try {
    const res = await client.post('/admin/run-scheduled-tasks')
    successMsg.value = `${res.data.message} (Expired requests: ${res.data.expired_requests_count}, Reminders sent: ${res.data.reminders_sent_count})`
    await loadDashboard()
    setTimeout(() => { successMsg.value = '' }, 4000)
  } catch (err) {
    errorMsg.value = 'Failed to execute scheduled maintenance tasks'
  } finally {
    runningTasks.value = false
  }
}

async function createCategory() {
  if (!newCatName.value.trim()) return
  addingCat.value = true
  try {
    await client.post('/categories', {
      name: newCatName.value.trim(),
      description: newCatDesc.value.trim()
    })
    successMsg.value = `Category "${newCatName.value}" created successfully!`
    showAddCatModal.value = false
    newCatName.value = ''
    newCatDesc.value = ''
    await loadDashboard()
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to create category')
  } finally {
    addingCat.value = false
  }
}

async function deleteCategory(cat) {
  if (!confirm(`Delete category "${cat.name}"? Existing equipment will become uncategorized.`)) return
  try {
    await client.delete(`/categories/${cat.id}`)
    successMsg.value = `Category "${cat.name}" deleted.`
    await loadDashboard()
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to delete category')
  }
}

async function toggleUserStatus(u) {
  const action = u.active ? 'deactivate' : 'activate'
  if (!confirm(`Are you sure you want to ${action} user "${u.username}"?`)) return
  try {
    await client.put(`/admin/users/${u.id}/toggle-status`)
    successMsg.value = `User status updated.`
    await loadDashboard()
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to toggle user status')
  }
}

async function deleteEquipmentListing(e) {
  if (!confirm(`Remove listing "${e.name}"?`)) return
  try {
    await client.delete(`/admin/equipment/${e.id}`)
    successMsg.value = `Listing "${e.name}" removed.`
    await loadDashboard()
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to remove listing')
  }
}

async function resolveReport(report) {
  try {
    await client.put(`/admin/reports/${report.id}/resolve`)
    successMsg.value = `Report #${report.id} marked as resolved.`
    await loadDashboard()
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err) {
    alert('Failed to resolve report')
  }
}

onMounted(() => {
  loadDashboard()
})
</script>

<style scoped>
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

.btn-maintenance {
  background: #f59e0b;
  color: white;
  border: none;
  font-weight: 700;
  padding: 0.65rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.btn-maintenance:hover:not(:disabled) {
  background: #d97706;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.25rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  box-shadow: var(--shadow);
}

.stat-icon {
  font-size: 2.5rem;
  background: var(--primary-light);
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.stat-data {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.85rem;
  font-weight: 800;
  color: #0f172a;
}

.stat-name {
  font-size: 0.82rem;
  color: var(--text-muted);
}

/* Tabs */
.admin-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid var(--border);
  flex-wrap: wrap;
}

.tab-btn {
  background: transparent;
  border: none;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-muted);
  padding: 0.75rem 1.25rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  transition: all 0.15s ease;
}

.tab-btn:hover {
  color: var(--primary);
}

.tab-btn.active {
  color: var(--primary);
  border-bottom-color: var(--primary);
}

.tab-pane {
  background: white;
  border-radius: 14px;
  border: 1px solid var(--border);
  padding: 2rem;
  box-shadow: var(--shadow);
}

.pane-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.pane-header h3 {
  font-size: 1.35rem;
  font-weight: 700;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.92rem;
}

.data-table th {
  background: #f8fafc;
  padding: 0.85rem 1rem;
  font-weight: 700;
  color: var(--secondary);
  border-bottom: 1px solid var(--border);
  font-size: 0.82rem;
  text-transform: uppercase;
}

.data-table td {
  padding: 0.9rem 1rem;
  border-bottom: 1px solid #f1f5f9;
  vertical-align: middle;
}

.badge-count {
  background: var(--primary-light);
  color: var(--primary);
  font-weight: 700;
  padding: 0.15rem 0.5rem;
  border-radius: 4px;
}

.role-pill {
  background: #eff6ff;
  color: #2563eb;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  margin-right: 0.25rem;
}

.status-tag {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  text-transform: capitalize;
}

.status-tag.active, .status-tag.available, .status-tag.resolved {
  background: #f0fdf4;
  color: var(--success);
}

.status-tag.inactive, .status-tag.open {
  background: #fef2f2;
  color: var(--danger);
}

.status-tag.rented {
  background: #fffbeb;
  color: var(--warning);
}

.equip-link {
  color: #0f172a;
  text-decoration: none;
}

.equip-link:hover {
  color: var(--primary);
}

.reason-cell {
  max-width: 250px;
}

.btn-approve {
  background: var(--success);
  color: white;
  border: none;
  font-weight: 600;
  cursor: pointer;
  border-radius: 6px;
}

.btn-danger-outline {
  background: transparent;
  border: 1px solid #fca5a5;
  color: var(--danger);
  font-weight: 600;
  cursor: pointer;
  border-radius: 6px;
}

.btn-sm {
  padding: 0.35rem 0.75rem;
  font-size: 0.82rem;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 1.5rem;
}

.modal-card {
  background: white;
  border-radius: 14px;
  width: 100%;
  max-width: 500px;
  padding: 2rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
}

.modal-sub {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: 1.25rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}
</style>
