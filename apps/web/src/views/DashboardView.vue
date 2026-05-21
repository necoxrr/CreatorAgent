<template>
  <div class="container mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6">📊 数据仪表盘</h1>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="p-6 border rounded-lg text-center">
        <p class="text-3xl font-bold text-primary">0</p>
        <p class="text-gray-500">本月产出</p>
      </div>
      <div class="p-6 border rounded-lg text-center">
        <p class="text-3xl font-bold text-accent">0</p>
        <p class="text-gray-500">平均互动</p>
      </div>
      <div class="p-6 border rounded-lg text-center">
        <p class="text-3xl font-bold text-green-500">0%</p>
        <p class="text-gray-500">热点命中</p>
      </div>
    </div>
    <div class="border rounded-lg p-6 h-80 flex items-center justify-center text-gray-400">
      图表区域 — 待 Week4 接入 ECharts
    </div>
  </div>
</template>