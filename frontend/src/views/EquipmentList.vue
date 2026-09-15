<template>
  <div class="equipment-list-page">
    <div class="page-header">
      <div>
        <h1 class="page-title">Explore Equipment</h1>
        <p class="page-subtitle">Find and rent verified gear from members in your community</p>
      </div>
      <router-link to="/add-equipment" class="btn-primary">+ List Your Equipment</router-link>
    </div>

    <!-- Filters Bar -->
    <div class="filters-card">
      <div class="filter-row primary-search">
        <div class="search-input-wrapper">
          <span class="search-icon">🔍</span>
          <input 
            v-model="filters.search" 
            @input="debounceFetch" 
            type="text" 
            placeholder="Search by name, description, or city (e.g. Canon, Projector, Chandigarh)..." 
          />
          <button v-if="filters.search" @click="clearSearch" class="btn-clear-search">✕</button>
        </div>
      </div>

      <div class="filter-row filter-controls">
        <div class="filter-item">
          <label>Category</label>
          <select v-model="filters.category_id" @change="fetchEquipment">
            <option value="">All Categories</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }} ({{ cat.total_equipment_count }})
            </option>
          </select>
        </div>

        <div class="filter-item">
          <label>Condition</label>
          <select v-model="filters.condition" @change="fetchEquipment">
            <option value="">Any Condition</option>
            <option value="New">New</option>
            <option value="Like New">Like New</option>
            <option value="Excellent">Excellent</option>
            <option value="Good">Good</option>
            <option value="Fair">Fair</option>
          </select>
        </div>

        <div class="filter-item">
          <label>Availability</label>
          <select v-model="filters.status" @change="fetchEquipment">
            <option value="available">Available Now</option>
            <option value="all">All (Including Rented)</option>
            <option value="rented">Currently Rented</option>
          </select>
        </div>

        <div class="filter-item">
          <label>Sort By</label>
          <select v-model="filters.sort" @change="fetchEquipment">
            <option value="newest">Newest First</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
            <option value="name">Name (A-Z)</option>
          </select>
        </div>

        <div class="filter-item btn-reset-wrapper">
          <button @click="resetFilters" class="btn-reset">Reset Filters</button>
        </div>
      </div>
    </div>

    <!-- Listings Count -->
    <div class="results-bar">
      <span class="results-count">Showing <strong>{{ equipmentList.length }}</strong> listings</span>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="state-container">
      <p>Loading equipment catalog...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="equipmentList.length === 0" class="empty-container">
      <span class="empty-icon">📦</span>
      <h3>No equipment found</h3>
      <p>Try clearing some filters or searching for something else.</p>
      <button @click="resetFilters" class="btn-secondary">Clear All Filters</button>
    </div>

    <!-- Equipment Cards Grid -->
    <div v-else class="equipment-grid">
      <div v-for="item in equipmentList" :key="item.id" class="equip-card">
        <div class="card-badges">
          <span class="cat-pill">{{ item.category_name }}</span>
          <span :class="['status-pill', item.availability_status]">
            {{ item.availability_status === 'available' ? 'Available' : 'Rented' }}
          </span>
        </div>

        <h3 class="card-title">
          <router-link :to="'/equipment/' + item.id">{{ item.name }}</router-link>
        </h3>

        <div class="card-condition-row">
          <span class="condition-tag">Condition: <strong>{{ item.condition }}</strong></span>
          <span v-if="item.avg_rating > 0" class="rating-tag">⭐ {{ item.avg_rating }} ({{ item.review_count }})</span>
          <span v-else class="rating-tag muted">No reviews yet</span>
        </div>

        <p class="card-desc">{{ truncate(item.description, 110) }}</p>

        <div class="card-location">
          <span>📍 {{ item.location || 'Local' }}</span>
          <span class="owner-name">Owner: {{ item.owner_username }}</span>
        </div>

        <div class="card-bottom">
          <div class="card-pricing">
            <span class="price-val">₹{{ item.price_per_day }}</span>
            <span class="price-period">/ day</span>
          </div>
          <router-link :to="'/equipment/' + item.id" class="btn-view">
            View & Reserve →
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import client from '../api/client'

const route = useRoute()
const equipmentList = ref([])
const categories = ref([])
const loading = ref(true)

const filters = reactive({
  search: route.query.search || '',
  category_id: route.query.category || '',
  condition: '',
  status: 'available',
  sort: 'newest'
})

let debounceTimer = null
function debounceFetch() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    fetchEquipment()
  }, 350)
}

function clearSearch() {
  filters.search = ''
  fetchEquipment()
}

function resetFilters() {
  filters.search = ''
  filters.category_id = ''
  filters.condition = ''
  filters.status = 'available'
  filters.sort = 'newest'
  fetchEquipment()
}

function truncate(text, length) {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

async function fetchEquipment() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filters.search) params.append('search', filters.search)
    if (filters.category_id) params.append('category_id', filters.category_id)
    if (filters.condition) params.append('condition', filters.condition)
    if (filters.status) params.append('status', filters.status)
    if (filters.sort) params.append('sort', filters.sort)

    const res = await client.get(`/equipment?${params.toString()}`)
    equipmentList.value = res.data
  } catch (e) {
    console.error('Error fetching equipment', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const catRes = await client.get('/categories')
    categories.value = catRes.data
  } catch (e) {
    console.error('Failed to load categories', e)
  }
  await fetchEquipment()
})

watch(() => route.query, (newQuery) => {
  if (newQuery.search !== undefined) filters.search = newQuery.search
  if (newQuery.category !== undefined) filters.category_id = newQuery.category
  fetchEquipment()
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
  font-size: 1rem;
}

.filters-card {
  background: white;
  border-radius: 14px;
  border: 1px solid var(--border);
  padding: 1.5rem;
  margin-bottom: 1.75rem;
  box-shadow: var(--shadow);
}

.primary-search {
  margin-bottom: 1.25rem;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-icon {
  position: absolute;
  left: 1rem;
  font-size: 1.1rem;
  color: var(--text-muted);
}

.search-input-wrapper input {
  padding-left: 2.75rem;
  padding-right: 2.5rem;
  font-size: 1rem;
  height: 48px;
  border-radius: 10px;
}

.btn-clear-search {
  position: absolute;
  right: 1rem;
  background: transparent;
  border: none;
  font-size: 1rem;
  color: var(--text-muted);
  cursor: pointer;
  width: auto;
  margin: 0;
  padding: 0;
}

.filter-controls {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  align-items: flex-end;
}

.filter-item label {
  display: block;
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  margin-bottom: 0.35rem;
}

.filter-item select {
  height: 42px;
  border-radius: 8px;
  background-color: #f8fafc;
}

.btn-reset-wrapper {
  display: flex;
}

.btn-reset {
  height: 42px;
  background: #f1f5f9;
  color: var(--secondary);
  border: 1px solid var(--border);
  font-weight: 600;
  font-size: 0.88rem;
  border-radius: 8px;
  transition: all 0.15s ease;
}

.btn-reset:hover {
  background: #e2e8f0;
  color: var(--text-main);
}

.results-bar {
  margin-bottom: 1.5rem;
  color: var(--text-muted);
  font-size: 0.95rem;
}

.equipment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.75rem;
}

.equip-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 1.5rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.equip-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 20px -3px rgba(0, 0, 0, 0.09);
}

.card-badges {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.85rem;
}

.cat-pill {
  background: var(--primary-light);
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
}

.status-pill {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 6px;
}

.status-pill.available {
  background: #f0fdf4;
  color: var(--success);
}

.status-pill.rented {
  background: #fffbeb;
  color: var(--warning);
}

.card-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}

.card-title a {
  color: #0f172a;
  text-decoration: none;
}

.card-title a:hover {
  color: var(--primary);
}

.card-condition-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
  margin-bottom: 0.75rem;
}

.condition-tag {
  color: var(--text-muted);
}

.condition-tag strong {
  color: #334155;
}

.rating-tag {
  font-weight: 700;
  color: #b45309;
}

.rating-tag.muted {
  color: #94a3b8;
  font-weight: 400;
}

.card-desc {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 1.25rem;
  flex: 1;
}

.card-location {
  display: flex;
  justify-content: space-between;
  font-size: 0.82rem;
  color: var(--text-muted);
  padding: 0.6rem 0;
  border-top: 1px solid #f1f5f9;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 1.25rem;
}

.card-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-pricing {
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
}

.price-val {
  font-size: 1.45rem;
  font-weight: 800;
  color: #0f172a;
}

.price-period {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.btn-view {
  background: var(--primary);
  color: white;
  text-decoration: none;
  padding: 0.55rem 1.15rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.88rem;
  transition: background 0.15s ease;
}

.btn-view:hover {
  background: var(--primary-hover);
}

.state-container, .empty-container {
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

.empty-container h3 {
  font-size: 1.35rem;
  margin-bottom: 0.5rem;
}

.empty-container p {
  color: var(--text-muted);
  margin-bottom: 1.5rem;
}
</style>
