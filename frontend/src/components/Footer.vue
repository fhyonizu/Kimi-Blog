<template>
  <footer class="mt-12 py-8 bg-white/40 backdrop-blur-md border-t border-white/40 text-center text-slate-600 text-sm">
    <div class="container mx-auto">
      <p class="mb-2">© 2025 Kimi Blog. All Rights Reserved.</p>
      <div class="flex justify-center gap-6 font-mono text-xs">
        <span>👀 总访问量: {{ visits }}</span>
        <span>⏱️ 运行时间: {{ runTime }}</span>
      </div>
    </div>
  </footer>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import axios from 'axios';

const visits = ref(0);
const runTime = ref('');
const API_URL = '/api';

// 设置网站建立时间 (例如: 2024-01-01)
const START_DATE = new Date('2025-12-01T00:00:00');

const calcTime = () => {
  const now = new Date();
  const diff = now - START_DATE;
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((diff % (1000 * 60)) / 1000);
  runTime.value = `${days}天 `;
};

let timer = null;

onMounted(async () => {
  timer = setInterval(calcTime, 1000);
  calcTime();
  try {
    // 获取后端统计数据
    const res = await axios.get(`${API_URL}/site-info`);
    visits.value = res.data.visits;
  } catch (e) {}
});

onUnmounted(() => clearInterval(timer));
</script>