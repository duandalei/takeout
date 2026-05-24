<template>
  <div>
    <h1 class="page-title">我的订单</h1>
    <div v-if="!loading && !orders.length" class="empty">暂无订单</div>
    <div v-for="o in orders" :key="o.order_id" class="card order-card"
         @click="$router.push(`/order/${o.order_id}`)">
      <div class="order-head">
        <strong>{{ o.merchant_name }}</strong>
        <span :class="`status status-${o.status}`">{{ statusText(o.status) }}</span>
      </div>
      <div class="order-body">
        <span>¥{{ o.actual_amount }}</span>
        <span class="order-time">{{ formatDate(o.created_at) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { getMyOrders } from "../api";

const orders = ref([]);
const loading = ref(false);

const STATUS_MAP = { 1: "待支付", 2: "待接单", 3: "配送中", 4: "已送达", 5: "已取消", 6: "待配送" };
function statusText(s) { return STATUS_MAP[s] || "未知"; }
function formatDate(d) { return d ? new Date(d).toLocaleString("zh-CN") : ""; }

onMounted(async () => {
  loading.value = true;
  try {
    const { data } = await getMyOrders();
    orders.value = data;
  } finally {
    loading.value = false;
  }
});
</script>

<style scoped>
.page-title { font-size: 20px; margin-bottom: 16px; }
.order-card { cursor: pointer; transition: transform .1s; }
.order-card:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,.08); }
.order-head { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 15px; }
.order-body { display: flex; justify-content: space-between; font-size: 13px; color: #999; }
.order-time { font-size: 12px; }
.status { font-size: 12px; padding: 2px 8px; border-radius: 4px; }
.status-1 { background: #ffeaa7; color: #d68910; }
.status-2 { background: #dfe6e9; color: #636e72; }
.status-3 { background: #74b9ff; color: #0984e3; }
.status-4 { background: #55efc4; color: #00b894; }
.status-5 { background: #fab1a0; color: #d63031; }
.status-6 { background: #e8f5e9; color: #2e7d32; }
.empty { text-align: center; color: #999; margin-top: 40px; }
</style>
