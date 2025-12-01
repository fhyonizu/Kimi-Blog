<template>
  <div class="container mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-6 relative">
    <!-- 左侧 -->
    <div class="lg:col-span-3 space-y-6">
      <div class="glass-card p-4">
        <h3 class="font-bold text-slate-700 mb-3">🔍 文章搜索</h3>
        <input v-model="searchQuery" @keyup.enter="doSearch" placeholder="输入关键词回车..." class="w-full p-2 rounded-lg bg-white/50 border border-transparent focus:bg-white focus:ring-2 focus:ring-blue-300 outline-none transition" />
      </div>
      <div class="glass-card p-4">
        <h3 class="font-bold text-slate-700 mb-3 border-b border-gray-200 pb-2">📂 文章分类</h3>
        <ul class="space-y-2">
            <li @click="filterCategory('')" class="cursor-pointer p-2 rounded hover:bg-white/50 transition flex justify-between" :class="{'bg-blue-100 text-blue-600': currentCategory === ''}">
                <span>全部文章</span>
            </li>
            <li v-for="c in categories" :key="c.name" @click="filterCategory(c.name)" class="cursor-pointer p-2 rounded hover:bg-white/50 transition flex justify-between" :class="{'bg-blue-100 text-blue-600': currentCategory === c.name}">
                <span>{{ c.name }}</span><span class="bg-white px-2 rounded-full text-xs py-0.5 text-gray-500">{{ c.count }}</span>
            </li>
        </ul>
      </div>
    </div>

    <!-- 中间：文章列表 -->
    <div class="lg:col-span-6 space-y-6">
      <!-- 这里的 articles?.length 是安全写法 -->
      <div v-if="(!articles || articles.length === 0) && !loading" class="text-center text-gray-500 mt-10 glass-card p-10">
        <div class="text-4xl mb-2">🍃</div>没有找到相关文章
      </div>

      <TiltCard v-for="article in articles" :key="article.id" class="cursor-pointer group" @click="$router.push(`/article/${article.id}`)">
        <h2 class="text-2xl font-bold mb-2 text-slate-800 group-hover:text-blue-600 transition-colors">{{ article.title }}</h2>
        <div class="flex items-center text-sm text-gray-400 mb-2 gap-3">
          <span class="bg-blue-50 text-blue-600 px-2 py-1 rounded">{{ article.category }}</span>
          <span>📅 {{ article.date }}</span>
          <span>🔥 {{ article.views }} 阅读</span>
        </div>
        <p class="text-slate-600 line-clamp-3 mb-3">{{ article.summary }}</p>
        <div class="flex gap-2">
            <span v-for="t in article.tags" :key="t" class="text-xs text-gray-400">#{{t}}</span>
        </div>
      </TiltCard>

      <div ref="loadTrigger" class="h-10 flex justify-center items-center">
          <span v-if="loadingMore" class="animate-bounce text-slate-400">加载更多...</span>
          <span v-if="!hasNext && articles && articles.length > 0" class="text-slate-400 text-sm">--- 我是有底线的 ---</span>
      </div>
    </div>

    <!-- 右侧 -->
    <div class="lg:col-span-3 space-y-6">
      <TiltCard class="text-center">
        <div class="w-24 h-24 bg-gray-200 rounded-full mx-auto mb-4 border-4 border-white shadow-md overflow-hidden hover:scale-105 transition duration-500">
             <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" alt="avatar" class="w-full h-full object-cover" />
        </div>
        <h3 class="text-xl font-bold text-slate-800">基米 Kimi</h3>
        <p class="text-sm text-slate-500 mt-2">Web 全栈开发者</p>
      </TiltCard>
      <TiltCard>
        <h4 class="font-bold border-b border-gray-200 pb-2 mb-2 text-slate-700">🏷️ 热门标签</h4>
        <div class="flex flex-wrap gap-2">
            <span v-for="tag in tags" :key="tag" class="text-xs bg-white border border-gray-100 px-2 py-1 rounded text-slate-600 hover:bg-blue-500 hover:text-white transition cursor-pointer" @click="searchQuery = tag; doSearch()">{{ tag }}</span>
        </div>
      </TiltCard>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import TiltCard from '../components/TiltCard.vue';
import axios from 'axios';

// 初始化为空数组，防止 undefined 报错
const articles = ref([]);
const categories = ref([]);
const tags = ref([]);
const API_URL = '/api';

const searchQuery = ref('');
const currentCategory = ref('');
const page = ref(1);
const hasNext = ref(true);
const loading = ref(false);
const loadingMore = ref(false);
const loadTrigger = ref(null);

const fetchMeta = async () => {
    try {
        const res = await axios.get(`${API_URL}/site-info`);
        categories.value = res.data.categories || [];
        tags.value = res.data.tags || [];
    } catch(e) { console.error(e); }
}

const fetchArticles = async (isLoadMore = false) => {
    if (loading.value || (isLoadMore && !hasNext.value)) return;
    
    if (isLoadMore) loadingMore.value = true;
    else loading.value = true;

    try {
        const res = await axios.get(`${API_URL}/articles`, {
            params: {
                page: page.value,
                per_page: 5,
                q: searchQuery.value,
                category: currentCategory.value
            }
        });

        // 防御性写法：如果后端返回 null，这里用 [] 兜底
        const newArticles = res.data.articles || [];

        if (isLoadMore) {
            articles.value.push(...newArticles);
        } else {
            articles.value = newArticles;
        }

        hasNext.value = res.data.has_next;
        page.value++; 

    } catch(e) { 
        console.error("加载失败", e); 
        // 报错时也要保证 articles 是数组
        if(!isLoadMore) articles.value = [];
    } finally {
        loading.value = false;
        loadingMore.value = false;
    }
};

const doSearch = () => {
    page.value = 1;
    hasNext.value = true;
    currentCategory.value = '';
    fetchArticles(false);
};

const filterCategory = (cat) => {
    currentCategory.value = cat;
    searchQuery.value = '';
    page.value = 1;
    hasNext.value = true;
    fetchArticles(false);
};

let observer = null;
onMounted(() => {
    fetchMeta();
    fetchArticles();
    observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting && hasNext.value && !loading.value) {
            fetchArticles(true);
        }
    });
    if (loadTrigger.value) observer.observe(loadTrigger.value);
});

onUnmounted(() => {
    if (observer) observer.disconnect();
});
</script>