<template>
  <div class="my-equipment-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">My Equipment Listings</h1>
        <p class="page-subtitle">Manage your inventory, rental rates, availability, and pending requests</p>
      </div>
      <router-link to="/add-equipment" class="btn-primary">+ Add New Equipment</router-link>
    </div>

    <div v-if="successMsg" class="alert alert-success">
      ✅ {{ successMsg }}
    </div>
    <div v-if="errorMsg" class="alert alert-danger">
      ⚠️ {{ errorMsg }}
    </div>

    <!-- Loading -->
    <div v-if="loading" class="state-card">
      <p>Loading your listings...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="items.length === 0" class="empty-card">
      <span class="empty-icon">📷</span>
      <h3>You haven't listed any equipment yet</h3>
      <p>Got cameras, audio equipment, laptops, or tools? Share them with members and earn rental income.</p>
      <router-link to="/add-equipment" class="btn-primary">+ List Your First Item</router-link>
    </div>

    <!-- Equipment List -->
    <div v-else class="listings-grid">
      <div v-for="item in items" :key="item.id" class="item-card">
        <div class="item-top">
          <div class="item-info">
            <span class="cat-pill">{{ item.category_name }}</span>
            <span :class="['status-pill', item.availability_status]">
              {{ item.availability_status }}
            </span>
          </div>
          <div class="item-pricing">
            <span class="price-amount">₹{{ item.price_per_day }}</span>
            <span class="price-period">/ day</span>
          </div>
        </div>

        <h3 class="item-title">
          <router-link :to="'/equipment/' + item.id">{{ item.name }}</router-link>
        </h3>

        <p class="item-desc">{{ item.description }}</p>

        <div class="item-stats">
          <div class="stat-pill" v-if="item.pending_requests_count > 0">
            <router-link to="/rental-requests" class="highlight-link">
              🔔 {{ item.pending_requests_count }} Pending Request{{ item.pending_requests_count > 1 ? 's' : '' }}
            </router-link>
          </div>
          <div class="stat-pill" v-else>0 Pending Requests</div>

          <div class="stat-pill" v-if="item.active_rentals_count > 0">
            <router-link to="/my-rentals" class="highlight-link">
              🤝 {{ item.active_rentals_count }} Active Rental
            </router-link>
          </div>
          <div class="stat-pill" v-else>0 Active Rentals</div>
        </div>

        <div class="item-footer">
          <span class="location-text">📍 {{ item.location || 'Local' }}</span>
          <div class="actions">
            <button @click="openEditModal(item)" class="btn-secondary btn-sm">Edit</button>
            <button @click="confirmDelete(item)" class="btn-danger-outline btn-sm">Delete</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="showEditModal" class="modal-backdrop" @click.self="showEditModal = false">
      <div class="modal-card">
        <h3>Edit Equipment Listing</h3>
        <p class="modal-sub">Update details for <strong>{{ editingItem.name }}</strong></p>

        <form @submit.prevent="saveEdit">
          <div class="form-group">
            <label>Title / Name</label>
            <input v-model="editForm.name" type="text" required />
          </div>

          <div class="modal-grid">
            <div class="form-group">
              <label>Daily Price (₹)</label>
              <input v-model.number="editForm.price_per_day" type="number" min="1" required />
            </div>

            <div class="form-group">
              <label>Availability Status</label>
              <select v-model="editForm.availability_status" required>
                <option value="available">Available</option>
                <option value="unavailable">Unavailable (Temporarily hidden)</option>
                <option value="rented">Rented</option>
                <option value="maintenance">Maintenance</option>
              </select>
            </div>
          </div>

          <div class="modal-grid">
            <div class="form-group">
              <label>Condition</label>
              <select v-model="editForm.condition" required>
                <option value="New">New</option>
                <option value="Like New">Like New</option>
                <option value="Excellent">Excellent</option>
                <option value="Good">Good</option>
                <option value="Fair">Fair</option>
              </select>
            </div>

            <div class="form-group">
              <label>Location</label>
              <input v-model="editForm.location" type="text" required />
            </div>
          </div>

          <div class="form-group">
            <label>Description</label>
            <textarea v-model="editForm.description" rows="4"></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showEditModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Saving Changes...' : 'Save Changes' }}
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

const items = ref([])
const loading = ref(true)
const successMsg = ref('')
const errorMsg = ref('')

const showEditModal = ref(false)
const editingItem = ref(null)
const saving = ref(false)
const editForm = reactive({
  id: null,
  name: '',
  price_per_day: '',
  availability_status: 'available',
  condition: 'Good',
  location: '',
  description: ''
})

async function fetchMyEquipment() {
  loading.value = true
  try {
    const res = await client.get('/equipment/my')
    items.value = res.data
  } catch (err) {
    errorMsg.value = 'Failed to load your equipment.'
  } finally {
    loading.value = false
  }
}

function openEditModal(item) {
  editingItem.value = item
  editForm.id = item.id
  editForm.name = item.name
  editForm.price_per_day = item.price_per_day
  editForm.availability_status = item.availability_status
  editForm.condition = item.condition
  editForm.location = item.location
  editForm.description = item.description
  showEditModal.value = true
}

async function saveEdit() {
  saving.value = true
  try {
    await client.put(`/equipment/${editForm.id}`, {
      name: editForm.name,
      price_per_day: editForm.price_per_day,
      availability_status: editForm.availability_status,
      condition: editForm.condition,
      location: editForm.location,
      description: editForm.description
    })
    successMsg.value = `Updated "${editForm.name}" successfully!`
    showEditModal.value = false
    await fetchMyEquipment()
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to update equipment.')
  } finally {
    saving.value = false
  }
}

async function confirmDelete(item) {
  if (confirm(`Are you sure you want to delete "${item.name}"?`)) {
    try {
      await client.delete(`/equipment/${item.id}`)
      successMsg.value = `Deleted "${item.name}".`
      await fetchMyEquipment()
      setTimeout(() => { successMsg.value = '' }, 3000)
    } catch (err) {
      errorMsg.value = err.response?.data?.error || 'Could not delete item.'
      setTimeout(() => { errorMsg.value = '' }, 3000)
    }
  }
}

onMounted(() => {
  fetchMyEquipment()
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

.listings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.75rem;
}

.item-card {
  background: white;
  border-radius: 14px;
  border: 1px solid var(--border);
  padding: 1.75rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
}

.item-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.item-info {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.cat-pill {
  background: var(--primary-light);
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
}

.status-pill {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  text-transform: capitalize;
}

.status-pill.available {
  background: #f0fdf4;
  color: var(--success);
}

.status-pill.rented {
  background: #fffbeb;
  color: var(--warning);
}

.status-pill.unavailable {
  background: #f1f5f9;
  color: var(--secondary);
}

.item-pricing {
  text-align: right;
}

.price-amount {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
}

.price-period {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.item-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.item-title a {
  color: #0f172a;
  text-decoration: none;
}

.item-title a:hover {
  color: var(--primary);
}

.item-desc {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 1.25rem;
  flex: 1;
}

.item-stats {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.stat-pill {
  background: #f8fafc;
  border: 1px solid var(--border);
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.highlight-link {
  color: var(--primary);
  font-weight: 700;
  text-decoration: none;
}

.item-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  border-top: 1px solid var(--border);
}

.location-text {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.4rem 0.85rem;
  font-size: 0.85rem;
  border-radius: 6px;
}

.btn-danger-outline {
  background: transparent;
  border: 1px solid #fca5a5;
  color: var(--danger);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-danger-outline:hover {
  background: #fef2f2;
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
  margin-bottom: 1.5rem;
}

/* Modal */
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
  max-width: 540px;
  padding: 2rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
}

.modal-sub {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: 1.25rem;
}

.modal-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}
</style>
