<template>
  <div class="rental-requests-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Rental Requests</h1>
        <p class="page-subtitle">Review incoming booking inquiries for your gear and track requests you've submitted</p>
      </div>
    </div>

    <!-- Feedback alerts -->
    <div v-if="successMsg" class="alert alert-success">
      ✅ {{ successMsg }}
    </div>
    <div v-if="errorMsg" class="alert alert-danger">
      ⚠️ {{ errorMsg }}
    </div>

    <!-- Tabs Navigation -->
    <div class="tabs-nav">
      <button 
        :class="['tab-btn', { active: activeTab === 'received' }]" 
        @click="activeTab = 'received'"
      >
        📥 Received Requests ({{ receivedRequests.length }})
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'sent' }]" 
        @click="activeTab = 'sent'"
      >
        📤 Sent Inquiries ({{ sentRequests.length }})
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="state-card">
      <p>Loading requests...</p>
    </div>

    <!-- TAB 1: Received Requests -->
    <div v-else-if="activeTab === 'received'">
      <div v-if="receivedRequests.length === 0" class="empty-card">
        <span class="empty-icon">📬</span>
        <h3>No received requests yet</h3>
        <p>When other members want to rent your equipment, their booking requests will appear here for your review.</p>
        <router-link to="/equipment" class="btn-secondary">Browse Equipment</router-link>
      </div>

      <div v-else class="requests-list">
        <div v-for="req in receivedRequests" :key="req.id" class="request-card">
          <div class="req-header">
            <div>
              <span class="req-id">Request #{{ req.id }}</span>
              <h3 class="req-item-title">{{ req.equipment_name }}</h3>
            </div>
            <span :class="['status-pill', req.status.toLowerCase()]">{{ req.status }}</span>
          </div>

          <div class="req-details-grid">
            <div class="detail-block">
              <span class="detail-label">Renter</span>
              <span class="detail-val">👤 {{ req.renter_username }}</span>
            </div>
            <div class="detail-block">
              <span class="detail-label">Rental Duration</span>
              <span class="detail-val">📅 {{ req.start_date }} → {{ req.end_date }} ({{ req.days }} day{{ req.days > 1 ? 's' : '' }})</span>
            </div>
            <div class="detail-block">
              <span class="detail-label">Total Amount</span>
              <span class="detail-val amount">₹{{ req.total_estimate }}</span>
            </div>
          </div>

          <div v-if="req.message" class="req-message">
            <strong>Note from renter:</strong>
            <p>"{{ req.message }}"</p>
          </div>

          <div class="req-footer">
            <span class="req-date">Requested on {{ formatDate(req.created_at) }}</span>

            <div v-if="req.status === 'PENDING'" class="actions">
              <button @click="rejectRequest(req.id)" class="btn-reject" :disabled="processingId === req.id">
                Decline
              </button>
              <button @click="approveRequest(req.id)" class="btn-approve" :disabled="processingId === req.id">
                Approve & Reserve
              </button>
            </div>

            <div v-else-if="req.status === 'APPROVED'" class="actions">
              <router-link to="/my-rentals" class="btn-primary btn-sm">View in Active Rentals →</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: Sent Requests -->
    <div v-else-if="activeTab === 'sent'">
      <div v-if="sentRequests.length === 0" class="empty-card">
        <span class="empty-icon">📤</span>
        <h3>You haven't requested any equipment</h3>
        <p>Explore equipment in your area and reserve items for your next shoot, build, or presentation.</p>
        <router-link to="/equipment" class="btn-primary">Browse Gear</router-link>
      </div>

      <div v-else class="requests-list">
        <div v-for="req in sentRequests" :key="req.id" class="request-card">
          <div class="req-header">
            <div>
              <span class="req-id">Request #{{ req.id }}</span>
              <h3 class="req-item-title">{{ req.equipment_name }}</h3>
            </div>
            <span :class="['status-pill', req.status.toLowerCase()]">{{ req.status }}</span>
          </div>

          <div class="req-details-grid">
            <div class="detail-block">
              <span class="detail-label">Owner</span>
              <span class="detail-val">👤 {{ req.owner_username }}</span>
            </div>
            <div class="detail-block">
              <span class="detail-label">Requested Dates</span>
              <span class="detail-val">📅 {{ req.start_date }} → {{ req.end_date }} ({{ req.days }} days)</span>
            </div>
            <div class="detail-block">
              <span class="detail-label">Estimated Total</span>
              <span class="detail-val amount">₹{{ req.total_estimate }}</span>
            </div>
          </div>

          <div v-if="req.message" class="req-message">
            <strong>Your note:</strong>
            <p>"{{ req.message }}"</p>
          </div>

          <div class="req-footer">
            <span class="req-date">Submitted on {{ formatDate(req.created_at) }}</span>

            <div v-if="req.status === 'PENDING'" class="actions">
              <button @click="cancelRequest(req.id)" class="btn-danger-outline btn-sm">
                Cancel Request
              </button>
            </div>

            <div v-else-if="req.status === 'APPROVED'" class="actions">
              <router-link to="/my-rentals" class="btn-primary btn-sm">View in My Rentals →</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '../api/client'

const activeTab = ref('received')
const receivedRequests = ref([])
const sentRequests = ref([])
const loading = ref(true)
const processingId = ref(null)
const successMsg = ref('')
const errorMsg = ref('')

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

async function loadData() {
  loading.value = true
  try {
    const [recRes, sentRes] = await Promise.all([
      client.get('/rentals/received'),
      client.get('/rentals/my-requests')
    ])
    receivedRequests.value = recRes.data
    sentRequests.value = sentRes.data
  } catch (err) {
    errorMsg.value = 'Failed to load rental requests.'
  } finally {
    loading.value = false
  }
}

async function approveRequest(id) {
  processingId.value = id
  errorMsg.value = ''
  try {
    await client.put(`/rentals/${id}/approve`)
    successMsg.value = `Request #${id} approved! The equipment has been marked as rented.`
    await loadData()
    setTimeout(() => { successMsg.value = '' }, 3500)
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to approve request'
  } finally {
    processingId.value = null
  }
}

async function rejectRequest(id) {
  processingId.value = id
  errorMsg.value = ''
  try {
    await client.put(`/rentals/${id}/reject`)
    successMsg.value = `Request #${id} rejected.`
    await loadData()
    setTimeout(() => { successMsg.value = '' }, 3500)
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to reject request'
  } finally {
    processingId.value = null
  }
}

async function cancelRequest(id) {
  if (!confirm('Are you sure you want to cancel this pending request?')) return
  try {
    await client.put(`/rentals/requests/${id}/cancel`)
    successMsg.value = 'Rental request cancelled.'
    await loadData()
    setTimeout(() => { successMsg.value = '' }, 3000)
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to cancel request'
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
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

.tabs-nav {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 2rem;
  border-bottom: 2px solid var(--border);
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

.requests-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.request-card {
  background: white;
  border-radius: 14px;
  border: 1px solid var(--border);
  padding: 1.75rem;
  box-shadow: var(--shadow);
}

.req-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.req-id {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

.req-item-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #0f172a;
}

.status-pill {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
  text-transform: uppercase;
}

.status-pill.pending {
  background: #eff6ff;
  color: #1d4ed8;
}

.status-pill.approved {
  background: #f0fdf4;
  color: var(--success);
}

.status-pill.rejected, .status-pill.cancelled, .status-pill.expired {
  background: #fef2f2;
  color: var(--danger);
}

.req-details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.25rem;
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
}

.detail-block {
  display: flex;
  flex-direction: column;
}

.detail-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--text-muted);
  margin-bottom: 0.2rem;
}

.detail-val {
  font-size: 0.95rem;
  color: #1e293b;
  font-weight: 500;
}

.detail-val.amount {
  font-size: 1.15rem;
  font-weight: 800;
  color: #0f172a;
}

.req-message {
  background: #ffffff;
  border-left: 3px solid var(--primary);
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  color: #334155;
  margin-bottom: 1.25rem;
}

.req-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border);
  padding-top: 1rem;
}

.req-date {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.actions {
  display: flex;
  gap: 0.75rem;
}

.btn-approve {
  background: var(--success);
  color: white;
  border: none;
  padding: 0.5rem 1.15rem;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.15s ease;
}

.btn-approve:hover:not(:disabled) {
  background: #15803d;
}

.btn-reject {
  background: transparent;
  color: var(--danger);
  border: 1px solid #fca5a5;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
}

.btn-reject:hover:not(:disabled) {
  background: #fef2f2;
}

.btn-sm {
  padding: 0.45rem 0.9rem;
  font-size: 0.85rem;
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
</style>
