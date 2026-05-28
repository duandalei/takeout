<template>
  <div>
    <h1 class="page-title">商家列表</h1>
    <div class="search-bar">
      <input v-model="keyword" placeholder="搜索商家名称..." class="search-input" />
    </div>
    <div v-if="loading" class="loading">加载中...</div>
    <div class="merchant-grid" v-else>
      <div v-for="m in filteredMerchants" :key="m.merchant_id" class="card merchant-card"
           @click="$router.push(`/merchant/${m.merchant_id}`)">
        <div class="merchant-logo">{{ m.name.charAt(0) }}</div>
        <div class="merchant-info">
          <h3>{{ m.name }}</h3>
          <div class="meta">
            <span class="star">★ {{ m.rating }}</span>
            <span>销量 {{ m.total_sales }}</span>
          </div>
          <div class="fee">
            <span>起送 ¥{{ m.min_delivery_price }}</span>
            <span>配送 ¥{{ m.delivery_fee }}</span>
          </div>
        </div>
        <div class="merchant-arrow">›</div>
      </div>
    </div>
    <p v-if="!loading && !filteredMerchants.length" class="empty">暂无营业商家</p>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { getMerchants } from "../api";

const merchants = ref([]);
const loading = ref(false);
const keyword = ref("");

const filteredMerchants = computed(() => {
  if (!keyword.value.trim()) return merchants.value;
  const kw = keyword.value.trim().toLowerCase();
  return merchants.value.filter(m => m.name.toLowerCase().includes(kw));
});

onMounted(async () => {
  loading.value = true;
  try {
    const { data } = await getMerchants();
    merchants.value = data;
  } catch (e) {
    console.error("加载商家列表失败:", e);
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.page-title { font-size: 20px; margin-bottom: 12px; }
.search-bar { margin-bottom: 14px; }
.search-input { width: 100%; padding: 10px 14px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; }
.search-input:focus { border-color: #ff6b00; }
.merchant-card { display: flex; align-items: center; gap: 14px; cursor: pointer; transition: transform .15s; }
.merchant-card:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,.1); }
.merchant-logo { width: 48px; height: 48px; border-radius: 10px; background: #ff6b00; color: #fff; font-size: 22px; font-weight: bold; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.merchant-info { flex: 1; }
.merchant-info h3 { font-size: 16px; margin-bottom: 6px; }
.meta { font-size: 13px; color: #888; display: flex; gap: 12px; margin-bottom: 4px; }
.star { color: #ff9c00; }
.fee { font-size: 12px; color: #aaa; display: flex; gap: 12px; }
.merchant-arrow { font-size: 24px; color: #ccc; }
.loading { text-align: center; padding: 40px; color: #999; }
.empty { text-align: center; color: #999; margin-top: 40px; }
</style>
