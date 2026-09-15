<template>
  <div class="equipment-details-page">
    <div class="breadcrumb">
      <router-link to="/equipment">← Back to Catalog</router-link>
    </div>

    <div v-if="loading" class="state-card">
      <p>Loading equipment specifications...</p>
    </div>

    <div v-else-if="!equip" class="state-card error">
      <h3>Equipment not found</h3>
      <p>This listing may have been removed or does not exist.</p>
      <router-link to="/equipment" class="btn-primary">Browse Other Gear</router-link>
    </div>

    <div v-else class="details-layout">
      <!-- Main Info Column -->
      <div class="details-main">
        <div class="item-header-card">
          <div class="header-badges">
            <span class="badge-cat">{{ equip.category_name }}</span>
            <span class="badge-condition">Condition: {{ equip.condition }}</span>
            <span :class="['badge-status', equip.availability_status]">
              {{ equip.availability_status === 'available' ? 'Available for Rent' : 'Currently Rented' }}
            </span>
          </div>

          <h1 class="item-title">{{ equip.name }}</h1>

          <div class="item-meta-bar">
            <span>📍 {{ equip.location || 'Location upon request' }}</span>
            <span>👤 Listed by <strong>{{ equip.owner_username }}</strong></span>
            <span v-if="equip.avg_rating > 0">⭐ {{ equip.avg_rating }} / 5.0 ({{ equip.review_count }} reviews)</span>
          </div>

          <div class="item-description-section">
            <h3>Description & Included Accessories</h3>
            <p class="description-text">{{ equip.description || 'No detailed description provided by owner.' }}</p>
          </div>

          <div class="report-action">
            <button @click="showReportModal = true" class="btn-report">🚩 Report listing</button>
          </div>
        </div>

        <!-- Reviews Section -->
        <div class="reviews-card">
          <div class="reviews-header">
            <h3>Community Reviews</h3>
            <span v-if="equip.reviews && equip.reviews.length > 0" class="reviews-summary">
              ⭐ {{ equip.avg_rating }} average rating ({{ equip.reviews.length }} reviews)
            </span>
          </div>

          <div v-if="!equip.reviews || equip.reviews.length === 0" class="no-reviews">
            <p>No reviews yet for this equipment. Be the first to rent and leave feedback!</p>
          </div>

          <div v-else class="reviews-list">
            <div v-for="rev in equip.reviews" :key="rev.id" class="review-item">
              <div class="review-top">
                <div class="reviewer-info">
                  <span class="reviewer-name">{{ rev.reviewer_username }}</span>
                  <span class="review-date">{{ formatDate(rev.created_at) }}</span>
                </div>
                <div class="stars">{{ '★'.repeat(rev.rating) }}{{ '☆'.repeat(5 - rev.rating) }}</div>
              </div>
              <p class="review-comment">{{ rev.comment }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Booking / Action Sidebar -->
      <div class="details-sidebar">
        <div class="booking-card">
          <div class="pricing-header">
            <div class="price-box">
              <span class="price-num">₹{{ equip.price_per_day }}</span>
              <span class="price-sub">/ day</span>
            </div>
            <span :class="['avail-tag', equip.availability_status]">
              {{ equip.availability_status }}
            </span>
          </div>

          <!-- Owner View -->
          <div v-if="isOwner" class="owner-notice">
            <span class="icon">ℹ️</span>
            <div>
              <strong>You are the owner</strong>
              <p>Manage reservations and requests for this gear in your dashboard.</p>
              <router-link to="/my-equipment" class="btn-secondary btn-block">Manage Listing</router-link>
            </div>
          </div>

          <!-- Guest View -->
          <div v-else-if="!auth.isAuthenticated" class="guest-notice">
            <p>Log in or create a free account to request this equipment.</p>
            <router-link :to="'/login?redirect=' + route.fullPath" class="btn-primary btn-block">
              Log In to Rent
            </router-link>
          </div>

          <!-- Booking Form for Logged-in Renters -->
          <form v-else @submit.prevent="submitRentalRequest" class="booking-form">
            <div v-if="requestSuccess" class="alert alert-success">
              ✅ Request sent! Owner will be notified to confirm your rental.
            </div>
            <div v-if="requestError" class="alert alert-danger">
              ⚠️ {{ requestError }}
            </div>

            <div class="date-row">
              <div class="form-group">
                <label>Start Date</label>
                <input 
                  v-model="startDate" 
                  :min="minStartDate" 
                  type="date" 
                  required 
                  @change="validateDates"
                />
              </div>

              <div class="form-group">
                <label>End Date</label>
                <input 
                  v-model="endDate" 
                  :min="startDate || minStartDate" 
                  type="date" 
                  required 
                  @change="validateDates"
                />
              </div>
            </div>

            <div class="form-group">
              <label>Message to Owner (Optional)</label>
              <textarea 
                v-model="message" 
                rows="3" 
                placeholder="Share how you plan to use it or ask pickup questions..."
              ></textarea>
            </div>

            <!-- Cost Calculation Preview -->
            <div class="cost-breakdown">
              <div class="cost-row">
                <span>Duration</span>
                <span><strong>{{ rentalDays }} day{{ rentalDays > 1 ? 's' : '' }}</strong></span>
              </div>
              <div class="cost-row">
                <span>Daily rate</span>
                <span>₹{{ equip.price_per_day }}</span>
              </div>
              <div class="cost-row total-row">
                <span>Total Estimated Cost</span>
                <span class="total-amount">₹{{ totalEstimate }}</span>
              </div>
            </div>

            <button 
              type="submit" 
              class="btn-primary btn-block btn-submit-request"
              :disabled="submitting || equip.availability_status !== 'available'"
            >
              {{ submitting ? 'Sending Request...' : (equip.availability_status === 'available' ? 'Request to Rent' : 'Item Currently Unavailable') }}
            </button>
            <p class="terms-note">No payment is charged until the owner approves your dates.</p>
          </form>
        </div>
      </div>
    </div>

    <!-- Report Modal -->
    <div v-if="showReportModal" class="modal-backdrop" @click.self="showReportModal = false">
      <div class="modal-card">
        <h3>Report this Listing</h3>
        <p class="modal-sub">Tell our administrators why this listing requires moderation.</p>

        <div v-if="reportSuccess" class="alert alert-success">
          Report submitted. Thank you for keeping EquipShare safe!
        </div>

        <form v-else @submit.prevent="submitReport">
          <div class="form-group">
            <label>Reason for report</label>
            <textarea 
              v-model="reportReason" 
              rows="4" 
              placeholder="e.g. Inappropriate item, misleading condition, suspected fraud, spam..."
              required
            ></textarea>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showReportModal = false" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-danger" :disabled="submittingReport">Submit Report</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '../api/client'
import { useAuthStore } from '../store/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const equip = ref(null)
const loading = ref(true)

// Rental form state
const todayStr = new Date().toISOString().split('T')[0]
const tomorrowDate = new Date(Date.now() + 86400000)
const tomorrowStr = tomorrowDate.toISOString().split('T')[0]
const afterTomorrowDate = new Date(Date.now() + 86400000 * 3)
const afterTomorrowStr = afterTomorrowDate.toISOString().split('T')[0]

const minStartDate = ref(todayStr)
const startDate = ref(tomorrowStr)
const endDate = ref(afterTomorrowStr)
const message = ref('')
const submitting = ref(false)
const requestSuccess = ref(false)
const requestError = ref('')

// Report state
const showReportModal = ref(false)
const reportReason = ref('')
const submittingReport = ref(false)
const reportSuccess = ref(false)

const isOwner = computed(() => {
  return auth.isAuthenticated && equip.value && auth.user && auth.user.id === equip.value.owner_id
})

const rentalDays = computed(() => {
  if (!startDate.value || !endDate.value) return 1
  const s = new Date(startDate.value)
  const e = new Date(endDate.value)
  const diffDays = Math.round((e - s) / (1000 * 60 * 60 * 24))
  return Math.max(1, diffDays > 0 ? diffDays : 1)
})

const totalEstimate = computed(() => {
  if (!equip.value) return 0
  return rentalDays.value * equip.value.price_per_day
})

function validateDates() {
  if (startDate.value && endDate.value && startDate.value > endDate.value) {
    endDate.value = startDate.value
  }
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

async function fetchEquip() {
  loading.value = true
  try {
    const res = await client.get('/equipment/' + route.params.id)
    equip.value = res.data
  } catch (err) {
    console.error('Failed to load item', err)
  } finally {
    loading.value = false
  }
}

async function submitRentalRequest() {
  requestError.value = ''
  requestSuccess.value = false
  submitting.value = true

  try {
    await client.post('/rentals/request', {
      equipment_id: equip.value.id,
      start_date: startDate.value,
      end_date: endDate.value,
      message: message.value
    })
    requestSuccess.value = true
    message.value = ''
    setTimeout(() => {
      router.push('/rental-requests')
    }, 1500)
  } catch (err) {
    requestError.value = err.response?.data?.error || 'Could not submit request'
  } finally {
    submitting.value = false
  }
}

async function submitReport() {
  if (!reportReason.value.trim()) return
  submittingReport.value = true
  try {
    await client.post('/reports', {
      equipment_id: equip.value.id,
      reported_user_id: equip.value.owner_id,
      reason: reportReason.value
    })
    reportSuccess.value = true
    setTimeout(() => {
      showReportModal.value = false
      reportSuccess.value = false
      reportReason.value = ''
    }, 1800)
  } catch (err) {
    alert('Failed to submit report. Please make sure you are logged in.')
  } finally {
    submittingReport.value = false
  }
}

onMounted(() => {
  fetchEquip()
})
</script>

<style scoped>
.breadcrumb {
  margin-bottom: 1.5rem;
}

.breadcrumb a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.95rem;
}

.details-layout {
  display: grid;
  grid-template-columns: 2fr 1.2fr;
  gap: 2rem;
  align-items: flex-start;
}

.item-header-card, .reviews-card, .booking-card {
  background: white;
  border-radius: 14px;
  border: 1px solid var(--border);
  padding: 2rem;
  box-shadow: var(--shadow);
  margin-bottom: 2rem;
}

.header-badges {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.badge-cat {
  background: var(--primary-light);
  color: var(--primary);
  font-weight: 700;
  font-size: 0.8rem;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
}

.badge-condition {
  background: #f1f5f9;
  color: var(--secondary);
  font-weight: 600;
  font-size: 0.8rem;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
}

.badge-status {
  font-weight: 700;
  font-size: 0.8rem;
  padding: 0.25rem 0.65rem;
  border-radius: 6px;
}

.badge-status.available {
  background: #f0fdf4;
  color: var(--success);
}

.badge-status.rented {
  background: #fffbeb;
  color: var(--warning);
}

.item-title {
  font-size: 2.25rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
  margin-bottom: 0.75rem;
}

.item-meta-bar {
  display: flex;
  gap: 1.5rem;
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-bottom: 2rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border);
  flex-wrap: wrap;
}

.item-description-section h3 {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 0.75rem;
  color: #1e293b;
}

.description-text {
  font-size: 1rem;
  line-height: 1.7;
  color: #334155;
  white-space: pre-line;
}

.report-action {
  margin-top: 2rem;
  text-align: right;
}

.btn-report {
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-size: 0.82rem;
  cursor: pointer;
}

.btn-report:hover {
  color: var(--danger);
  text-decoration: underline;
}

/* Reviews */
.reviews-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}

.reviews-summary {
  font-weight: 700;
  color: #b45309;
  font-size: 0.9rem;
}

.no-reviews {
  color: var(--text-muted);
  font-size: 0.95rem;
  padding: 1rem 0;
}

.review-item {
  padding: 1.25rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.review-item:last-child {
  border-bottom: none;
}

.review-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.reviewer-name {
  font-weight: 700;
  color: #0f172a;
}

.review-date {
  color: var(--text-muted);
  font-size: 0.8rem;
  margin-left: 0.75rem;
}

.stars {
  color: #f59e0b;
  font-size: 1.1rem;
  letter-spacing: 0.1em;
}

.review-comment {
  color: #334155;
  font-size: 0.95rem;
}

/* Booking Card */
.pricing-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--border);
}

.price-num {
  font-size: 2rem;
  font-weight: 800;
  color: #0f172a;
}

.price-sub {
  color: var(--text-muted);
  font-size: 0.9rem;
  margin-left: 0.25rem;
}

.avail-tag {
  text-transform: uppercase;
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
}

.avail-tag.available {
  background: #f0fdf4;
  color: var(--success);
}

.avail-tag.rented {
  background: #fffbeb;
  color: var(--warning);
}

.owner-notice, .guest-notice {
  background: #f8fafc;
  border-radius: 10px;
  padding: 1.25rem;
  text-align: center;
}

.owner-notice {
  display: flex;
  gap: 0.75rem;
  text-align: left;
}

.btn-block {
  display: block;
  width: 100%;
  text-align: center;
  margin-top: 1rem;
}

.date-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.cost-breakdown {
  background: #f8fafc;
  border-radius: 8px;
  padding: 1rem;
  margin: 1.25rem 0;
  border: 1px solid var(--border);
}

.cost-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  color: var(--secondary);
}

.total-row {
  border-top: 1px solid var(--border);
  padding-top: 0.5rem;
  margin-top: 0.5rem;
  margin-bottom: 0;
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
}

.total-amount {
  color: var(--primary);
  font-size: 1.25rem;
}

.btn-submit-request {
  padding: 0.85rem;
  font-size: 1.05rem;
  font-weight: 700;
}

.btn-submit-request:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.terms-note {
  font-size: 0.78rem;
  color: var(--text-muted);
  text-align: center;
  margin-top: 0.75rem;
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

.btn-danger {
  background: var(--danger);
  color: white;
  border: none;
  padding: 0.6rem 1.25rem;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

@media (max-width: 860px) {
  .details-layout {
    grid-template-columns: 1fr;
  }
}
</style>
