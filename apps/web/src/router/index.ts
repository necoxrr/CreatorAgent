import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
    { path: '/trends', name: 'trends', component: () => import('@/views/TrendsView.vue') },
    { path: '/topics', name: 'topics', component: () => import('@/views/TopicsView.vue') },
    { path: '/editor', name: 'editor', component: () => import('@/views/EditorView.vue') },
    { path: '/dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
    { path: '/agent', name: 'agent', component: () => import('@/views/AgentView.vue') }
  ]
})

export default router