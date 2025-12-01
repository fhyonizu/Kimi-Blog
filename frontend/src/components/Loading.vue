<template>
  <div v-if="loading" class="fixed inset-0 z-[100] bg-white flex items-center justify-center transition-opacity duration-500" :class="{'opacity-0 pointer-events-none': !loading}">
    <div class="flex flex-col items-center">
      <div class="animate-bounce text-5xl mb-4">🐰</div>
      <div class="text-xl font-bold text-slate-500 animate-pulse tracking-widest">加载中...</div>
    </div>
  </div>
</template>
<script setup>
defineProps(['loading'])
</script>