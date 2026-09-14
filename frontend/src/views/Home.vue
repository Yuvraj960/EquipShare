<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <span class="pill-badge">✨ Peer-to-Peer Community Sharing</span>
        <h1 class="hero-title">Rent High-End Equipment From People Around You</h1>
        <p class="hero-subtitle">
          Why buy expensive cameras, projectors, laptops, or power tools for occasional use? 
          Rent what you need, or list your idle gear to earn extra income.
        </p>

        <div class="search-box">
          <input 
            v-model="searchQuery" 
            @keyup.enter="handleSearch"
            type="text" 
            placeholder="Search cameras, projectors, laptops, power tools, locations..." 
          />
          <button @click="handleSearch" class="btn-search">Search Gear</button>
        </div>

        <!-- Quick Category Chips -->
        <div class="category-chips" v-if="categories.length > 0">
          <span class="chips-label">Popular Categories:</span>
          <router-link 
            v-for="cat in categories.slice(0, 6)" 
            :key="cat.id" 
            :to="'/equipment?category=' + cat.id"
            class="chip"
          >
            {{ cat.name }} ({{ cat.equipment_count }})
          </router-link>
        </div>
      </div>
    </section>

    <!-- Workflow Steps -->
    <section class="workflow-section">
      <h2 class="section-title">How EquipShare Works</h2>
      <p class="section-subtitle">A seamless lifecycle designed for transparency and trust.</p>

      <div class="workflow-grid">
        <div class="step-card">
          <div class="step-num">1</div>
          <div class="step-icon">🔍</div>
          <h3>Find or List</h3>
          <p>Browse verified listings with transparent daily rates, or list your owned gear in under two minutes.</p>
        </div>

        <div class="step-card">
          <div class="step-num">2</div>
          <div class="step-icon">📅</div>
          <h3>Request & Approve</h3>
          <p>Choose your rental dates. The owner reviews the request and locks in the reservation.</p>
        </div>

        <div class="step-card">
          <div class="step-num">3</div>
          <div class="step-icon">🤝</div>
          <h3>Rent & Return</h3>
          <p>Pick up or receive the gear. Return on the agreed date with automated reminder notifications.</p>
        </div>

        <div class="step-card">
          <div class="step-num">4</div>
          <div class="step-icon">⭐</div>
          <h3>Review & Earn Trust</h3>
          <p>Rate the equipment condition and renter/owner reliability to maintain high community trust.</p>
        </div>
      </div>
    </section>

    <!-- Featured Available Gear -->
    <section class="featured-section">
      <div class="section-header">
        <div>
          <h2 class="section-title">Available Equipment Near You</h2>
          <p class="section-subtitle">Ready for instant reservation today</p>
        </div>
        <router-link to="/equipment" class="view-all-link">View All Listings →</router-link>
      </div>

      <div v-if="loading" class="loading-state">Loading available equipment...</div>

      <div v-else-if="featured.length === 0" class="empty-state">
        No equipment currently available. Be the first to list!
      </div>

      <div v-else class="equipment-grid">
        <div v-for="item in featured" :key="item.id" class="equip-card">
          <div class="card-header-badge">
            <span class="badge-cat">{{ item.category_name }}</span>
            <span class="badge-condition">{{ item.condition }}</span>
          </div>

          <h3 class="equip-name">
            <router-link :to="'/equipment/' + item.id">{{ item.name }}</router-link>
          </h3>

          <p class="equip-desc">{{ truncate(item.description, 90) }}</p>

          <div class="equip-meta">
            <span class="meta-location">📍 {{ item.location || 'Local community' }}</span>
            <span v-if="item.avg_rating > 0" class="meta-rating">⭐ {{ item.avg_rating }} ({{ item.review_count }})</span>
            <span v-else class="meta-rating new-badge">New listing</span>
          </div>

          <div class="card-footer">
            <div class="equip-price">
              <span class="price-val">₹{{ item.price_per_day }}</span>
              <span class="price-unit">/ day</span>
            </div>
            <router-link :to="'/equipment/' + item.id" class="btn-rent">Reserve</router-link>
          </div>
        </div>
      </div>
    </section>

    <!-- Call to action -->
    <section class="cta-banner">
      <div class="cta-content">
        <h2>Got gear gathering dust at home or the lab?</h2>
        <p>Turn your idle cameras, instruments, and power tools into steady income with our trusted peer network.</p>
      </div>
      <router-link to="/add-equipment" class="btn-cta">+ List Equipment Now</router-link>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import client from '../api/client'

const router = useRouter()
const searchQuery = ref('')
const categories = ref([])
const featured = ref([])
const loading = ref(true)

function handleSearch() {
  if (searchQuery.value.trim()) {
    router.push({ path: '/equipment', query: { search: searchQuery.value.trim() } })
  } else {
    router.push('/equipment')
  }
}

function truncate(text, length) {
  if (!text) return ''
  return text.length > length ? text.substring(0, length) + '...' : text
}

onMounted(async () => {
  try {
    const [catRes, equipRes] = await Promise.all([
      client.get('/categories'),
      client.get('/equipment?limit=6')
    ])
    categories.value = catRes.data
    featured.value = equipRes.data.slice(0, 6)
  } catch (err) {
    console.error('Failed to load home data', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.hero-section {
  background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #2563eb 100%);
  color: white;
  border-radius: 16px;
  padding: 3.5rem 2.5rem;
  margin-bottom: 3.5rem;
  box-shadow: 0 10px 25px -5px rgba(30, 58, 138, 0.25);
}

.hero-content {
  max-width: 780px;
}

.pill-badge {
  display: inline-block;
  background: rgba(255, 255, 255, 0.18);
  backdrop-filter: blur(4px);
  padding: 0.35rem 0.85rem;
  border-radius: 9999px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-bottom: 1.25rem;
}

.hero-title {
  font-size: 2.75rem;
  line-height: 1.2;
  font-weight: 800;
  margin-bottom: 1rem;
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: 1.1rem;
  opacity: 0.92;
  margin-bottom: 2rem;
  line-height: 1.6;
}

.search-box {
  display: flex;
  gap: 0.5rem;
  background: white;
  padding: 0.4rem;
  border-radius: 12px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  margin-bottom: 1.5rem;
}

.search-box input {
  flex: 1;
  border: none;
  outline: none;
  box-shadow: none;
  font-size: 1rem;
  padding: 0.75rem 1rem;
  color: #0f172a;
}

.btn-search {
  background: var(--primary);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-weight: 700;
  font-size: 0.95rem;
  transition: background 0.15s ease;
  white-space: nowrap;
}

.btn-search:hover {
  background: var(--primary-hover);
}

.category-chips {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  font-size: 0.85rem;
}

.chips-label {
  opacity: 0.85;
  font-weight: 500;
}

.chip {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  text-decoration: none;
  padding: 0.25rem 0.65rem;
  border-radius: 9999px;
  transition: all 0.15s ease;
}

.chip:hover {
  background: white;
  color: var(--primary);
}

/* Workflow */
.workflow-section {
  margin-bottom: 4rem;
  text-align: center;
}

.section-title {
  font-size: 1.85rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0.4rem;
}

.section-subtitle {
  color: var(--text-muted);
  font-size: 1rem;
  margin-bottom: 2.25rem;
}

.workflow-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  text-align: left;
}

.step-card {
  background: white;
  border-radius: 12px;
  border: 1px solid var(--border);
  padding: 1.75rem 1.5rem;
  position: relative;
  box-shadow: var(--shadow);
  transition: transform 0.15s ease;
}

.step-card:hover {
  transform: translateY(-3px);
}

.step-num {
  position: absolute;
  top: 1rem;
  right: 1.25rem;
  font-size: 1.75rem;
  font-weight: 900;
  color: #e2e8f0;
}

.step-icon {
  font-size: 2.25rem;
  margin-bottom: 1rem;
}

.step-card h3 {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: #1e293b;
}

.step-card p {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.5;
}

/* Featured section */
.featured-section {
  margin-bottom: 4rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 2rem;
}

.view-all-link {
  color: var(--primary);
  font-weight: 600;
  text-decoration: none;
  font-size: 0.95rem;
}

.view-all-link:hover {
  text-decoration: underline;
}

.equipment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.equip-card {
  background: white;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: var(--shadow);
  display: flex;
  flex-direction: column;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.equip-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.card-header-badge {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.badge-cat {
  background: var(--primary-light);
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

.badge-condition {
  background: #f1f5f9;
  color: var(--secondary);
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.5rem;
  border-radius: 6px;
}

.equip-name {
  font-size: 1.15rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.equip-name a {
  color: #1e293b;
  text-decoration: none;
}

.equip-name a:hover {
  color: var(--primary);
}

.equip-desc {
  color: var(--text-muted);
  font-size: 0.88rem;
  margin-bottom: 1rem;
  flex: 1;
}

.equip-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--text-muted);
  padding: 0.75rem 0;
  border-top: 1px solid #f1f5f9;
  border-bottom: 1px solid #f1f5f9;
  margin-bottom: 1rem;
}

.meta-rating {
  font-weight: 600;
  color: #b45309;
}

.new-badge {
  color: var(--success);
  font-weight: 600;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.equip-price {
  display: flex;
  align-items: baseline;
  gap: 0.2rem;
}

.price-val {
  font-size: 1.35rem;
  font-weight: 800;
  color: #0f172a;
}

.price-unit {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.btn-rent {
  background: var(--primary);
  color: white;
  text-decoration: none;
  padding: 0.5rem 1.2rem;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.88rem;
  transition: background 0.15s ease;
}

.btn-rent:hover {
  background: var(--primary-hover);
}

/* CTA */
.cta-banner {
  background: #0f172a;
  color: white;
  border-radius: 16px;
  padding: 3rem 2.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 2rem;
  flex-wrap: wrap;
}

.cta-content h2 {
  font-size: 1.6rem;
  font-weight: 800;
  margin-bottom: 0.5rem;
}

.cta-content p {
  color: #94a3b8;
  font-size: 0.95rem;
}

.btn-cta {
  background: white;
  color: #0f172a;
  text-decoration: none;
  padding: 0.85rem 1.75rem;
  border-radius: 10px;
  font-weight: 700;
  font-size: 1rem;
  transition: all 0.15s ease;
}

.btn-cta:hover {
  background: #f1f5f9;
  transform: translateY(-2px);
}

@media (max-width: 640px) {
  .hero-title {
    font-size: 2rem;
  }
  .search-box {
    flex-direction: column;
  }
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>
