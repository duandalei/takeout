<template>
  <div>
    <h1 class="page-title">商家列表</h1>
    <div class="merchant-grid">
      <div v-for="m in merchants" :key="m.merchant_id" class="card merchant-card"
           @click="$router.push(`/merchant/${m.merchant_id}`)">
        <div class="merchant-info">
          <h3>{{ m.name }}</h3>
          <div class="meta">
            <span class="star">★ {{ m.rating }}</span>
            <span>月售 {{ m.monthly_sales }}</span>
          </div>
          <div class="fee">
            <span>起送 ¥{{ m.min_delivery_price }}</span>
            <span>配送 ¥{{ m.delivery_fee }}</span>
          </div>
        </div>
        <div class="merchant-arrow">›</div>
      </div>
    </div>
    <p v-if="!loading && !merchants.length" class="empty">暂无营业商家</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getMerchants } from "../api";

const merchants = ref([]);
const loading = ref(false);

onMounted(async () => {
  loading.value = true;
  try {
    const { data } = await getMerchants();
    merchants.value = data;
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.page-title { font-size: 20px; margin-bottom: 16px; }
.merchant-card { display: flex; align-items: center; cursor: pointer; transition: transform .15s; }
.merchant-card:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,.1); }
.merchant-info { flex: 1; }
.merchant-info h3 { font-size: 16px; margin-bottom: 6px; }
.meta { font-size: 13px; color: #888; display: flex; gap: 12px; margin-bottom: 4px; }
.star { color: #ff9c00; }
.fee { font-size: 12px; color: #aaa; display: flex; gap: 12px; }
.merchant-arrow { font-size: 24px; color: #ccc; }
.empty { text-align: center; color: #999; margin-top: 40px; }
</style>
