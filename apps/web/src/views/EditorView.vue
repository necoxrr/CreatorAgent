<template>
  <div class="container mx-auto p-6">
    <h1 class="text-3xl font-bold mb-6">✍️ 文案创作</h1>
    <div class="flex gap-6 h-[calc(100vh-120px)]">
      <div class="flex-1 border rounded-lg p-4">
        <textarea class="w-full h-full resize-none outline-none" placeholder="在此编辑你的文案..." />
      </div>
      <div class="w-80 border rounded-lg p-4 space-y-4">
        <h3 class="font-semibold">AI 助手</h3>
        <button class="w-full px-4 py-2 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition">生成大纲</button>
        <button class="w-full px-4 py-2 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition">AI 续写</button>
        <button class="w-full px-4 py-2 bg-primary/10 text-primary rounded-lg hover:bg-primary/20 transition">风格切换</button>
        <button class="w-full px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition">生成标题</button>
      </div>
    </div>
  </div>
</template>