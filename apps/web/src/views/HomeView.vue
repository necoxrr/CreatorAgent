<template>
  <main class="min-h-screen bg-gradient-to-br from-primary/5 to-accent/5">
    <div class="container mx-auto px-6 py-20 text-center">
      <h1 class="text-5xl font-bold mb-4 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
        CreatorAgent
      </h1>
      <p class="text-xl text-gray-600 mb-12">AI驱动的创作者智能体工作台</p>
      <div class="flex justify-center gap-4">
        <router-link to="/trends" class="px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition">
          🔥 热点发现
        </router-link>
        <router-link to="/topics" class="px-6 py-3 bg-secondary text-white rounded-lg hover:bg-secondary/90 transition">
          📋 选题推荐
        </router-link>
        <router-link to="/editor" class="px-6 py-3 bg-accent text-white rounded-lg hover:bg-accent/90 transition">
          ✍️ 文案创作
        </router-link>
        <router-link to="/dashboard" class="px-6 py-3 border border-primary text-primary rounded-lg hover:bg-primary/10 transition">
          📊 数据仪表盘
        </router-link>
      </div>
    </div>
  </main>
</template>