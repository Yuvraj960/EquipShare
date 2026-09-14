<template>
  <div class="my-rentals-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">My Rentals</h1>
        <p class="page-subtitle">Track active equipment rentals in progress and review completed rental history</p>
      </div>
    </div>

    <!-- Alerts -->
    <div v-if="successMsg" class="alert alert-success">
      ✅ {{ successMsg }}
    </div>
    <div v-if="errorMsg" class="alert alert-danger">
      ⚠️ {{ errorMsg }}
    </div>

    <!-- Tabs Navigation -->
    <div class="tabs-nav">
      <button 
        :class="['tab-btn', { active: activeTab === 'active' }]" 
        @click="activeTab = 'active'"
      >
        ⏳ Active Rentals ({{ activeRentals.length }})
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'completed' }]" 
        @click="activeTab = 'completed'"
      >
        📦 Past & Returned ({{ completedRentals.length }})
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="state-card">
      <p>Loading your rentals...</p>
    </div>

    <!-- TAB 1: Active Rentals -->
    <div v-else-if="activeTab === 'active'">
      <div v-if="activeRentals.length === 0" class="empty-card">
        <span class="empty-icon">🤝</span>
        <h3>No active rentals currently</h3>
        <p>You don't have any ongoing rentals. Check your approved requests or discover new gear!</p>
        <router-link to="/equipment" class="btn-primary">Browse Gear</router-link>
      </div>

      <div v-else class="rentals-grid">
        <div v-for="r in activeRentals" :key="r.id" class="rental-card active-card">
          <div class="rental-top">
            <div class="role-tag-box">
              <span :class="['role-pill', r.is_renter ? 'renter' : 'owner']">
                {{ r.is_renter ? 'You are Renting' : 'You Lent Out' }}
              </span>
              <span class="rental-code">Rental #{{ r.id }}</span>
            </div>
            <span class="status-active">ACTIVE NOW</span>
          </div>

          <h3 class="equip-name">
            <router-link :to="'/equipment/' + r.equipment_id">{{ r.equipment_name }}</router-link>
          </h3>

          <div class="rental-details">
            <div class="detail-row">
              <span class="detail-k">{{ r.is_renter ? 'Owner' : 'Renter' }}:</span>
              <span class="detail-v">👤 {{ r.is_renter ? r.owner_username : r.renter_username }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-k">Rental Period:</span>
              <span class="detail-v">📅 {{ r.start_date }} → {{ r.end_date }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-k">Total Agreed Amount:</span>
              <span class="detail-v total-price">₹{{ r.total_amount }}</span>
            </div>
          </div>

          <div class="rental-card-footer">
            <span class="footer-note">Ready to return? Either owner or renter can confirm return.</span>
            <button 
              @click="markReturned(r.id)" 
              class="btn-return"
              :disabled="returningId === r.id"
            >
              {{ returningId === r.id ? 'Updating...' : 'Mark as Returned' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- TAB 2: Completed Rentals -->
    <div v-else-if="activeTab === 'completed'">
      <div v-if="completedRentals.length === 0" class="empty-card">
        <span class="empty-icon">📁</span>
        <h3>No past rentals on record</h3>
        <p>Your finished rentals will be archived here along with reviews and receipts.</p>
      </div>

      <div v-else class="rentals-grid">
        <div v-for="r in completedRentals" :key="r.id" class="rental-card completed-card">
          <div class="rental-top">
            <span :class="['role-pill', r.is_renter ? 'renter' : 'owner']">
              {{ r.is_renter ? 'Rented by You' : 'Lent by You' }}
            </span>
            <span class="status-completed">RETURNED</span>
          </div>

          <h3 class="equip-name">
            <router-link :to="'/equipment/' + r.equipment_id">{{ r.equipment_name }}</router-link>
          </h3>

          <div class="rental-details">
            <div class="detail-row">
              <span class="detail-k">{{ r.is_renter ? 'Owner' : 'Renter' }}:</span>
              <span class="detail-v">👤 {{ r.is_renter ? r.owner_username : r.renter_username }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-k">Dates:</span>
              <span class="detail-v">{{ r.start_date }} to {{ r.end_date }}</span>
            </div>
            <div class="detail-row">
              <span class="detail-k">Amount Settled:</span>
              <span class="detail-v">₹{{ r.total_amount }}</span>
            </div>
            <div class="detail-row" v-if="r.returned_at">
              <span class="detail-k">Returned Date:</span>
              <span class="detail-v">{{ formatDate(r.returned_at) }}</span>
            </div>
          </div>

          <div class="rental-card-footer">
            <template v-if="r.is_renter">
              <button 
                v-if="!r.has_reviewed" 
                @click="openReviewModal(r)" 
                class="btn-primary btn-sm"
              >
                ⭐ Write Review
              </button>
              <span v-else class="reviewed-pill">✓ Reviewed</span>
            </template>
            <template v-else>
              <span class="owner-done-pill">Item returned to inventory</span>
            </template>
          </div>
        </div>
      </div>
    </div>

    <!-- Write Review Modal -->
    <div v-if="showReviewModal" class="modal-backdrop" @click.self="showReviewModal = false">
      <div class="modal-card">
        <h3>Rate & Review</h3>
        <p class="modal-sub">How was your experience renting <strong>{{ currentReviewRental?.equipment_name }}</strong>?</p>

        <form @submit.prevent="submitReview">
          <div class="form-group">
            <label>Rating (1 to 5 Stars)</label>
            <div class="rating-stars-input">
              <span 
                v-for="star in 5" 
                :key="star" 
                :class="['star-icon', { active: star <= reviewRating }]"
                @click="reviewRating = star"
              >
                ★
              </span>
              <span class="rating-val-display">{{ reviewRating }} / 5</span>
            </div>
          </div>

          <div class="form-group">
            <label>Your Review & Feedback</label>
            <textarea 
              v-model="reviewComment" 
              rows="4" 
              placeholder="Was the equipment in great condition? Did the owner provide helpful instructions?"
              required
            ></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showReviewModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="submittingReview">
              {{ submittingReview ? 'Submitting...' : 'Post Review' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import client from '../api/client'

const activeTab = ref('active')
const allRentals = ref([])
const loading = ref(true)
const returningId = ref(null)
const successMsg = ref('')
const errorMsg = ref('')

// Review modal
const showReviewModal = ref(false)
const currentReviewRental = ref(null)
const reviewRating = ref(5)
const reviewComment = ref('')
const submittingReview = ref(false)

const activeRentals = computed(() => {
  return allRentals.value.filter(r => r.status === 'ACTIVE')
})

const completedRentals = computed(() => {
  return allRentals.value.filter(r => r.status === 'RETURNED')
})

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

async function fetchRentals() {
  loading.value = true
  try {
    const res = await client.get('/rentals/my-rentals')
    allRentals.value = res.data
  } catch (err) {
    errorMsg.value = 'Failed to load your rentals'
  } finally {
    loading.value = false
  }
}

async function markReturned(id) {
  if (!confirm('Confirm return? This will restore the equipment to available status.')) return
  returningId.value = id
  errorMsg.value = ''
  try {
    await client.put(`/rentals/${id}/return`)
    successMsg.value = `Rental #${id} marked as returned!`
    await fetchRentals()
    setTimeout(() => { successMsg.value = '' }, 3500)
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Failed to update return status.'
  } finally {
    returningId.value = null
  }
}

function openReviewModal(rental) {
  currentReviewRental.value = rental
  reviewRating.value = 5
  reviewComment.value = ''
  showReviewModal.value = true
}

async function submitReview() {
  if (!currentReviewRental.value) return
  submittingReview.value = true
  try {
    await client.post(`/equipment/${currentReviewRental.value.equipment_id}/reviews`, {
      rental_id: currentReviewRental.value.id,
      rating: reviewRating.value,
      comment: reviewComment.value
    })
    successMsg.value = 'Thank you for your review!'
    showReviewModal.value = false
    await fetchRentals()
    setTimeout(() => { successMsg.value = '' }, 3500)
  } catch (err) {
    alert(err.response?.data?.error || 'Failed to post review')
  } finally {
    submittingReview.value = false
  }
}

onMounted(() => {
  fetchRentals()
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

.rentals-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 1.75rem;
}

.rental-card {
  background: white;
  border-radius: 14px;
  border: 1px solid var(--border);
  padding: 1.75rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
}

.rental-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.role-tag-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.role-pill {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
}

.role-pill.renter {
  background: #eff6ff;
  color: #2563eb;
}

.role-pill.owner {
  background: #fdf4ff;
  color: #a21caf;
}

.rental-code {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 600;
}

.status-active {
  background: #f0fdf4;
  color: var(--success);
  font-size: 0.75rem;
  font-weight: 800;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
}

.status-completed {
  background: #f1f5f9;
  color: var(--secondary);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
}

.equip-name {
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.equip-name a {
  color: #0f172a;
  text-decoration: none;
}

.equip-name a:hover {
  color: var(--primary);
}

.rental-details {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.88rem;
}

.detail-k {
  color: var(--text-muted);
}

.detail-v {
  font-weight: 600;
  color: #1e293b;
}

.detail-v.total-price {
  font-size: 1.1rem;
  font-weight: 800;
  color: #0f172a;
}

.rental-card-footer {
  margin-top: auto;
  border-top: 1px solid var(--border);
  padding-top: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.footer-note {
  font-size: 0.75rem;
  color: var(--text-muted);
  line-height: 1.3;
}

.btn-return {
  background: var(--primary);
  color: white;
  border: none;
  padding: 0.55rem 1.15rem;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.88rem;
  cursor: pointer;
  white-space: nowrap;
  transition: background 0.15s ease;
}

.btn-return:hover:not(:disabled) {
  background: var(--primary-hover);
}

.reviewed-pill {
  font-size: 0.85rem;
  color: var(--success);
  font-weight: 700;
}

.owner-done-pill {
  font-size: 0.82rem;
  color: var(--text-muted);
}

.btn-sm {
  padding: 0.45rem 1rem;
  font-size: 0.85rem;
}

.rating-stars-input {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin-top: 0.25rem;
}

.star-icon {
  font-size: 2rem;
  color: #cbd5e1;
  cursor: pointer;
  user-select: none;
  transition: color 0.15s ease;
}

.star-icon.active {
  color: #f59e0b;
}

.rating-val-display {
  margin-left: 0.75rem;
  font-size: 1rem;
  font-weight: 700;
  color: #334155;
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
