<template>
  <div class="merchant-page">
    <h2>商家面板</h2>

    <div class="toolbar card">
      <span>欢迎，{{ merchantName }}</span>
      <button class="btn btn-primary" @click="fetchOrders">刷新订单</button>
    </div>

    <div class="filter-tabs">
      <span :class="{ active: filterStatus === null }" @click="setFilter(null)">全部</span>
      <span :class="{ active: filterStatus === 2 }" @click="setFilter(2)">待接单</span>
      <span :class="{ active: filterStatus === 6 }" @click="setFilter(6)">待配送</span>
      <span :class="{ active: filterStatus === 3 }" @click="setFilter(3)">配送中</span>
      <span :class="{ active: filterStatus === 4 }" @click="setFilter(4)">已送达</span>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="orders.length === 0" class="card empty">暂无订单</div>

    <div v-for="o in orders" :key="o.order_id" class="card order-card">
      <div class="order-header">
        <span class="order-id">#{{ o.order_id }}</span>
        <span class="order-status status-{{ o.status }}">{{ statusText(o.status) }}</span>
      </div>
      <div class="order-info">
        <div>客户：{{ o.contact_name || '-' }} {{ o.contact_phone || '' }}</div>
        <div>地址：{{ o.address_detail || '' }}</div>
        <div>金额：¥{{ o.actual_amount }}</div>
        <div v-if="o.items && o.items.length" class="items-summary">
          {{ o.items.map(i => `${i.dish_name} x${i.quantity}`).join('、') }}
        </div>
      </div>
      <button
        v-if="o.status === 2"
        class="btn btn-primary"
        @click="handleAccept(o.order_id)"
        :disabled="accepting"
      >
        {{ accepting === o.order_id ? '处理中...' : '接单' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { merchantOrders, acceptOrder } from "../api";
import { statusText } from "../constants";

const orders = ref([]);
const loading = ref(false);
const accepting = ref(null);
const filterStatus = ref(null);
const merchantName = ref("");

function setFilter(status) {
  filterStatus.value = status;
  fetchOrders();
}

async function fetchOrders() {
  loading.value = true;
  try {
    const { data } = await merchantOrders(filterStatus.value);
    orders.value = data;
    const u = JSON.parse(localStorage.getItem("user") || "{}");
    merchantName.value = u.nickname || "";
  } finally {
    loading.value = false;
  }
}

async function handleAccept(orderId) {
  accepting.value = orderId;
  try {
    await acceptOrder(orderId);
    await fetchOrders();
  } finally {
    accepting.value = null;
  }
}

onMounted(fetchOrders);
</script>

<style scoped>
.merchant-page h2 { margin-bottom: 16px; }
.toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; margin-bottom: 16px;
}
.toolbar span { font-size: 14px; font-weight: bold; }
.filter-tabs { display: flex; gap: 8px; margin-bottom: 16px; }
.filter-tabs span {
  padding: 6px 16px; border-radius: 20px; cursor: pointer;
  color: #666; background: #f5f5f5; font-size: 13px;
}
.filter-tabs span.active { color: #fff; background: #ff6b00; font-weight: bold; }
.order-card { margin-bottom: 12px; }
.order-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.order-id { font-weight: bold; }
.order-status { font-size: 13px; padding: 2px 8px; border-radius: 4px; }
.status-2 { background: #e3f2fd; color: #1565c0; }
.status-3 { background: #fff3e0; color: #e65100; }
.status-4 { background: #e8f5e9; color: #2e7d32; }
.status-6 { background: #e8f5e9; color: #2e7d32; }
.order-info { font-size: 13px; color: #666; line-height: 1.8; }
.order-info div { margin-bottom: 2px; }
.items-summary { font-size: 12px; color: #ff6b00; margin-top: 4px; }
.loading, .empty { text-align: center; padding: 32px; color: #999; }
</style>
