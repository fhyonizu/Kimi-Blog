<template>
  <div class="container mx-auto px-4 min-h-[80vh] flex flex-col items-center py-10">
    
    <!-- 登录卡片 -->
    <div v-if="!token" class="w-full max-w-md animate__animated animate__fadeIn">
        <TiltCard class="p-10 text-center">
            <h2 class="text-3xl font-bold mb-2 text-slate-800">管理员登录</h2>
            <div class="space-y-4 mt-6">
              <input v-model="loginForm.username" @keyup.enter="handleLogin" class="w-full p-3 rounded-lg bg-white/50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-slate-400" placeholder="用户名">
              <input v-model="loginForm.password" type="password" @keyup.enter="handleLogin" class="w-full p-3 rounded-lg bg-white/50 border border-gray-200 focus:outline-none focus:ring-2 focus:ring-slate-400" placeholder="密码">
            </div>
            <button @click="handleLogin" class="w-full mt-8 bg-slate-800 text-white py-3 rounded-lg font-bold hover:bg-black transition-all">登 录</button>
            <p v-if="errorMsg" class="mt-4 text-red-500 text-sm">{{ errorMsg }}</p>
        </TiltCard>
    </div>

    <!-- 管理界面 -->
    <div v-else class="w-full max-w-6xl animate__animated animate__fadeIn">
        <!-- 顶部栏 -->
        <div class="flex justify-between items-center mb-8 glass-card p-4">
            <h1 class="text-2xl font-bold text-slate-800">控制台</h1>
            <div class="flex gap-4">
                <!-- 切换标签 -->
                <button @click="currentTab = 'article'" :class="{'text-blue-600 font-bold': currentTab==='article'}" class="hover:text-blue-500">文章管理</button>
                <button @click="currentTab = 'comment'" :class="{'text-blue-600 font-bold': currentTab==='comment'}" class="hover:text-blue-500">评论管理</button>
                <div class="w-[1px] bg-gray-300 mx-2"></div>
                <button @click="logout" class="text-red-500 hover:text-red-700">退出</button>
            </div>
        </div>

        <!-- TAB 1: 文章管理 -->
        <div v-if="currentTab === 'article'" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <!-- 左侧：编辑器 -->
            <div class="glass-card p-6">
                <h3 class="text-xl font-bold mb-4 text-slate-700 border-b pb-2">{{ isEditing ? '编辑文章' : '发布新文章' }}</h3>
                <div class="space-y-4">
                  <input v-model="form.title" class="w-full p-3 rounded-lg bg-gray-50/50 border-none focus:ring-2 focus:ring-slate-200" placeholder="文章标题">
                  <div class="flex gap-4">
                      <input v-model="form.category" class="w-1/2 p-3 rounded-lg bg-gray-50/50 border-none focus:ring-2 focus:ring-slate-200" placeholder="分类">
                      <input v-model="form.tags" class="w-1/2 p-3 rounded-lg bg-gray-50/50 border-none focus:ring-2 focus:ring-slate-200" placeholder="标签 (逗号分隔)">
                  </div>
                  <textarea v-model="form.content" class="w-full h-80 p-3 rounded-lg bg-gray-50/50 border-none focus:ring-2 focus:ring-slate-200 font-mono text-sm" placeholder="# Markdown..."></textarea>
                </div>
                <div class="flex gap-3 mt-6">
                    <button @click="saveArticle" class="bg-slate-800 text-white px-6 py-2 rounded-lg hover:bg-black transition">{{ isEditing ? '更新' : '发布' }}</button>
                    <button v-if="isEditing" @click="resetForm" class="bg-gray-200 text-gray-600 px-6 py-2 rounded-lg">取消</button>
                </div>
            </div>

            <!-- 右侧：文章列表 -->
            <div class="glass-card p-6">
                <h3 class="text-xl font-bold mb-4 text-slate-700 border-b pb-2">文章列表</h3>
                <div class="space-y-3 max-h-[600px] overflow-y-auto pr-2 custom-scroll">
                    <div v-for="a in articles" :key="a.id" class="flex justify-between items-center p-3 hover:bg-white/60 rounded-lg transition border border-transparent hover:border-gray-100 group">
                        <div class="truncate w-2/3">
                          <div class="font-bold text-slate-800 truncate">{{ a.title }}</div>
                          <div class="text-xs text-gray-400">{{ a.date }}</div>
                        </div>
                        <div class="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button @click="editArticle(a)" class="text-blue-600 text-sm">编辑</button>
                            <button @click="deleteArticle(a.id)" class="text-red-600 text-sm">删除</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- TAB 2: 评论管理 -->
        <div v-if="currentTab === 'comment'" class="glass-card p-6">
            <div class="flex justify-between mb-4 border-b pb-2">
                <h3 class="text-xl font-bold text-slate-700">最新评论 (前50条)</h3>
                <button @click="fetchComments" class="text-sm text-blue-500">刷新</button>
            </div>
            
            <div class="space-y-4 max-h-[70vh] overflow-y-auto custom-scroll">
                <div v-if="comments.length === 0" class="text-center text-gray-400 py-10">暂时没有评论</div>
                
                <div v-for="c in comments" :key="c.id" class="bg-white/40 p-4 rounded-lg flex justify-between items-start hover:bg-white/80 transition">
                    <div>
                        <div class="flex items-center gap-2 mb-1">
                            <span class="font-bold text-slate-800">{{ c.nickname }}</span>
                            <span class="text-xs text-gray-400">评论于 《{{ c.article_title }}》</span>
                            <span class="text-xs text-gray-400">{{ c.date }}</span>
                        </div>
                        <div class="text-slate-600 text-sm bg-white/50 p-2 rounded">{{ c.content }}</div>
                    </div>
                    <button @click="deleteComment(c.id)" class="text-red-500 hover:text-red-700 text-sm border border-red-200 px-3 py-1 rounded hover:bg-red-50 transition ml-4 shrink-0">
                        删除
                    </button>
                </div>
            </div>
        </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import TiltCard from '../components/TiltCard.vue';

// 状态变量
const token = ref(sessionStorage.getItem('token') || '');
const loginForm = ref({ username: '', password: '' });
const errorMsg = ref('');
const currentTab = ref('article'); // 当前标签页: article 或 comment

// 文章相关
const articles = ref([]);
const form = ref({ title: '', category: '', tags: '', content: '' });
const isEditing = ref(false);
const editId = ref(null);

// 评论相关
const comments = ref([]);

const API_URL = '/api'; // 生产环境用相对路径
const authConfig = () => ({ headers: { Authorization: `Bearer ${token.value}` } });

// --- 登录逻辑 ---
const handleLogin = async () => {
    try {
        errorMsg.value = '';
        const res = await axios.post(`${API_URL}/login`, loginForm.value);
        token.value = res.data.access_token;
        sessionStorage.setItem('token', token.value);
        fetchArticles();
        fetchComments();
    } catch (e) { errorMsg.value = '用户名或密码错误'; }
};

const logout = () => {
    token.value = '';
    sessionStorage.removeItem('token');
};

// --- 文章逻辑 ---
const fetchArticles = async () => {
    try {
        const res = await axios.get(`${API_URL}/articles`, { params: { per_page: 100 } });
        articles.value = res.data.articles;
    } catch(e) { console.error(e) }
};

const saveArticle = async () => {
    if(!form.value.title || !form.value.content) return alert('必填项不能为空');
    try {
        if (isEditing.value) await axios.put(`${API_URL}/articles/${editId.value}`, form.value, authConfig());
        else await axios.post(`${API_URL}/articles`, form.value, authConfig());
        resetForm();
        fetchArticles();
    } catch (e) { checkAuth(e); }
};

const deleteArticle = async (id) => {
    if(!confirm('确定删除文章？')) return;
    try {
        await axios.delete(`${API_URL}/articles/${id}`, authConfig());
        fetchArticles();
    } catch (e) { checkAuth(e); }
};

const editArticle = async (article) => {
    try {
        const res = await axios.get(`${API_URL}/articles/${article.id}`);
        const full = res.data;
        form.value = { title: full.title, category: full.category, tags: full.tags.join(','), content: full.content };
        isEditing.value = true;
        editId.value = full.id;
    } catch(e) { alert('加载失败'); }
};

const resetForm = () => {
    form.value = { title: '', category: '', tags: '', content: '' };
    isEditing.value = false;
    editId.value = null;
};

// --- 评论逻辑 ---
const fetchComments = async () => {
    if(!token.value) return;
    try {
        const res = await axios.get(`${API_URL}/all-comments`, authConfig());
        comments.value = res.data;
    } catch(e) { checkAuth(e); }
};

const deleteComment = async (id) => {
    if(!confirm('确定要删除这条评论吗？此操作不可恢复。')) return;
    try {
        await axios.delete(`${API_URL}/comments/${id}`, authConfig());
        fetchComments(); // 刷新列表
    } catch(e) { checkAuth(e); }
};

// 辅助：Token过期检查
const checkAuth = (e) => {
    if(e.response && e.response.status === 401) logout();
    else alert('操作失败');
}

// 监听 tab 切换加载数据
watch(currentTab, (newVal) => {
    if(newVal === 'comment') fetchComments();
    if(newVal === 'article') fetchArticles();
});

onMounted(() => {
    if(token.value) {
        fetchArticles();
        fetchComments();
    }
});
</script>