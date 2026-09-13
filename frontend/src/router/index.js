import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import { useAuthStore } from '../store/auth'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/login', name: 'Login', component: () => import('../views/Login.vue'), meta: { guestOnly: true } },
  { path: '/register', name: 'Register', component: () => import('../views/Register.vue'), meta: { guestOnly: true } },
  { path: '/equipment', name: 'EquipmentList', component: () => import('../views/EquipmentList.vue') },
  { path: '/equipment/:id', name: 'EquipmentDetails', component: () => import('../views/EquipmentDetails.vue') },
  { path: '/add-equipment', name: 'AddEquipment', component: () => import('../views/AddEquipment.vue'), meta: { requiresAuth: true } },
  { path: '/my-equipment', name: 'MyEquipment', component: () => import('../views/MyEquipment.vue'), meta: { requiresAuth: true } },
  { path: '/rental-requests', name: 'RentalRequests', component: () => import('../views/RentalRequests.vue'), meta: { requiresAuth: true } },
  { path: '/my-rentals', name: 'MyRentals', component: () => import('../views/MyRentals.vue'), meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: () => import('../views/Profile.vue'), meta: { requiresAuth: true } },
  { path: '/notifications', name: 'Notifications', component: () => import('../views/Notifications.vue'), meta: { requiresAuth: true } },
  { path: '/admin', name: 'AdminDashboard', component: () => import('../views/AdminDashboard.vue'), meta: { requiresAuth: true, requiresAdmin: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }

  if (to.meta.guestOnly && authStore.isAuthenticated) {
    return next('/')
  }

  if (to.meta.requiresAdmin) {
    if (!authStore.user) {
      try {
        await authStore.fetchMe()
      } catch (e) {
        return next('/')
      }
    }
    if (!authStore.isAdmin) {
      return next('/')
    }
  }

  next()
})

export default router
