<template>
  <div class="add-equipment-page">
    <div class="page-container">
      <div class="header">
        <router-link to="/my-equipment" class="back-link">← Back to My Listings</router-link>
        <h1>List Your Equipment</h1>
        <p>Make your unused cameras, tools, projectors, or tech gear earn money for you.</p>
      </div>

      <div v-if="error" class="alert alert-danger">
        ⚠️ {{ error }}
      </div>

      <div class="form-card">
        <form @submit.prevent="handleSubmit">
          <div class="form-group">
            <label>Equipment Name / Title *</label>
            <input 
              v-model="form.name" 
              type="text" 
              placeholder="e.g. Sony Alpha A7 III Full Frame Camera" 
              required 
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Category *</label>
              <select v-model="form.category_id" required>
                <option value="" disabled>Select a category</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                  {{ cat.name }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Condition *</label>
              <select v-model="form.condition" required>
                <option value="New">New (Unopened / Mint)</option>
                <option value="Like New">Like New (Barely used)</option>
                <option value="Excellent">Excellent (Minor signs of use)</option>
                <option value="Good">Good (Normal wear, fully functional)</option>
                <option value="Fair">Fair (Heavy wear, functional)</option>
              </select>
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>Rental Price Per Day (₹) *</label>
              <input 
                v-model.number="form.price_per_day" 
                type="number" 
                min="1" 
                step="1" 
                placeholder="500" 
                required 
              />
            </div>

            <div class="form-group">
              <label>Pickup Location / City *</label>
              <input 
                v-model="form.location" 
                type="text" 
                placeholder="e.g. Sector 14, Chandigarh or North Campus" 
                required 
              />
            </div>
          </div>

          <div class="form-group">
            <label>Detailed Description & What's Included *</label>
            <textarea 
              v-model="form.description" 
              rows="5" 
              placeholder="Include specs, accessories included (lenses, cables, case, batteries), and any specific pickup instructions..." 
              required
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="button" @click="$router.push('/my-equipment')" class="btn-secondary">Cancel</button>
            <button type="submit" class="btn-primary" :disabled="submitting">
              {{ submitting ? 'Publishing Listing...' : 'Publish Listing' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import client from '../api/client'

const router = useRouter()
const categories = ref([])
const error = ref('')
const submitting = ref(false)

const form = reactive({
  name: '',
  category_id: '',
  condition: 'Like New',
  price_per_day: '',
  location: '',
  description: ''
})

onMounted(async () => {
  try {
    const res = await client.get('/categories')
    categories.value = res.data
    if (categories.value.length > 0) {
      form.category_id = categories.value[0].id
    }
  } catch (err) {
    console.error('Failed to load categories', err)
  }
})

async function handleSubmit() {
  error.value = ''
  submitting.value = true

  try {
    const res = await client.post('/equipment', {
      name: form.name.trim(),
      category_id: form.category_id,
      condition: form.condition,
      price_per_day: Number(form.price_per_day),
      location: form.location.trim(),
      description: form.description.trim()
    })

    const newId = res.data?.equipment?.id
    if (newId) {
      router.push(`/equipment/${newId}`)
    } else {
      router.push('/my-equipment')
    }
  } catch (err) {
    error.value = err.response?.data?.error || 'Failed to list equipment. Please verify your inputs.'
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.add-equipment-page {
  max-width: 760px;
  margin: 0 auto;
}

.header {
  margin-bottom: 2rem;
}

.back-link {
  display: inline-block;
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.header h1 {
  font-size: 2.1rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0.25rem;
}

.header p {
  color: var(--text-muted);
}

.form-card {
  background: white;
  border-radius: 14px;
  border: 1px solid var(--border);
  padding: 2.25rem 2rem;
  box-shadow: var(--shadow);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-primary {
  padding: 0.75rem 1.75rem;
  font-size: 1rem;
  font-weight: 700;
}

@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
