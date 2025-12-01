<template>
  <!-- 1. 这里删掉了 <CursorEffect /> -->
  <Loading :loading="loading" />
  
  <div v-show="!loading" class="fade-in flex flex-col min-h-screen">
     <nav class="fixed top-0 w-full z-40 bg-white/30 backdrop-blur-md border-b border-white/20 p-4 px-10 flex justify-between items-center">
        <router-link to="/" class="font-bold text-xl text-slate-800 tracking-wider hover:opacity-70 transition">
          KIMI BLOG
        </router-link>
        <div class="flex gap-4 text-sm font-medium text-slate-600">
          <a href="#" class="hover:text-black transition">#</a>
          <a href="#" class="hover:text-black transition">#</a>
        </div>
     </nav>
     
     <div class="pt-24 flex-grow">
        <router-view></router-view>
     </div>
     
     <Footer />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
// 2. 这里删掉了 import CursorEffect ...
import Loading from './components/Loading.vue';
import Footer from './components/Footer.vue';

const loading = ref(true);

onMounted(() => {
  setTimeout(() => {
    loading.value = false;
  }, 1500);
});
</script>

<style>
.fade-in {
  animation: fadeIn 1s ease-in;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>