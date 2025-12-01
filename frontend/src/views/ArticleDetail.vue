<template>
  <div class="container mx-auto px-4 py-8 max-w-4xl">
    <button @click="$router.back()" class="mb-4 text-slate-600 bg-white/50 px-4 py-2 rounded-lg hover:bg-white hover:shadow transition">← 返回列表</button>
    
    <div v-if="article" class="glass-card p-8 mb-8 animate__animated animate__fadeInUp">
      <h1 class="text-4xl font-bold mb-4 text-slate-800">{{ article.title }}</h1>
      <div class="text-sm text-slate-400 mb-6 flex gap-4">
        <span>📂 {{ article.category }}</span>
        <span>📅 {{ article.date }}</span>
      </div>
      <!-- Markdown 渲染 -->
      <div class="prose prose-slate max-w-none" v-html="renderedContent"></div>
    </div>

    <!-- 评论区 -->
    <div class="glass-card p-6">
      <h3 class="text-xl font-bold mb-4 text-slate-700">评论区 ({{ article?.comments?.length || 0 }})</h3>
      
      <!-- 留言列表 -->
      <div class="space-y-4 mb-8">
        <div v-if="!article?.comments?.length" class="text-slate-400 text-sm">还没有评论，快来抢沙发吧~</div>
        <div v-for="(comment, index) in article?.comments" :key="index" class="bg-white/40 p-3 rounded-lg border border-white/50">
          <div class="font-bold text-sm text-slate-800 flex items-center gap-2">
            <div class="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center text-xs text-blue-500">👤</div>
            {{ comment.nickname }}
          </div>
          <div class="text-slate-600 mt-1 ml-8">{{ comment.content }}</div>
        </div>
      </div>
      
      <!-- 留言表单 -->
      <div class="flex flex-col gap-3 bg-white/30 p-4 rounded-xl">
        <h4 class="font-bold text-sm text-slate-600">发表评论</h4>
        <input v-model="newComment.nickname" placeholder="请输入你的昵称" class="p-2 rounded-lg bg-white/60 border-none focus:ring-2 focus:ring-blue-200 outline-none" />
        <textarea v-model="newComment.content" placeholder="写下你的想法..." class="p-2 rounded-lg bg-white/60 border-none focus:ring-2 focus:ring-blue-200 outline-none h-20 resize-none"></textarea>
        <div class="flex justify-between items-center">
            <div class="flex gap-2">
                <button v-for="emoji in emojis" :key="emoji" @click="newComment.content += emoji" class="text-lg hover:scale-125 transition">{{emoji}}</button>
            </div>
            <button @click="submitComment" class="bg-slate-800 text-white px-6 py-2 rounded-lg hover:bg-black transition text-sm">发送评论</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const route = useRoute();
const article = ref(null);
const newComment = ref({ nickname: '', content: '' });
const emojis = ['👍', '😂', '🤔', '❤️', '🔥', '😭', '🎉'];
const API_URL = '/api';

const renderedContent = computed(() => {
    return article.value ? DOMPurify.sanitize(marked(article.value.content)) : '';
});

const loadArticle = async () => {
    try {
        const res = await axios.get(`${API_URL}/articles/${route.params.id}`);
        article.value = res.data;
    } catch(e) { console.error(e); }
}

const submitComment = async () => {
    if(!newComment.value.content || !newComment.value.nickname) return alert('昵称和内容都得写哦');
    await axios.post(`${API_URL}/articles/${route.params.id}/comments`, newComment.value);
    newComment.value = { nickname: '', content: '' };
    loadArticle(); 
}

onMounted(loadArticle);
</script>