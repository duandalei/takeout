<template>
  <div class="rider-page">
    <h2>骑手面板</h2>

    <div class="toolbar card">
      <span>当前骑手：{{ riderName }}</span>
      <button class="btn btn-primary" @click="fetchAll">刷新订单</button>
    </div>

    <div v-if="loading" class="loading">加载中...</div>

    <template v-else>
      <!-- 可接订单 -->
      <h3 class="section-title">可接订单</h3>
      <div v-if="availableOrders.length === 0" class="card empty">暂无可接订单</div>
      <div v-for="o in availableOrders" :key="o.order_id" class="card order-card">
        <div class="order-header">
          <span class="order-id">#{{ o.order_id }}</span>
          <span class="order-status status-6">待配送</span>
        </div>
        <div class="order-info">
          <div>商家：{{ o.merchant_name || '-' }}</div>
          <div>收货人：{{ o.contact_name || '-' }} {{ o.phone || '' }}</div>
          <div>地址：{{ o.province }}{{ o.city }}{{ o.district }}{{ o.detail }}</div>
          <div>金额：¥{{ o.actual_amount }}</div>
          <div v-if="o.remark">备注：{{ o.remark }}</div>
          <div v-if="o.items && o.items.length" class="items-summary">
            菜品：{{ o.items.map(i => `${i.dish_name} x${i.quantity}`).join('、') }}
          </div>
        </div>
        <button
          class="btn btn-primary"
          @click="handleAccept(o.order_id)"
          :disabled="accepting === o.order_id"
        >
          {{ accepting === o.order_id ? '接单中...' : '接单' }}
        </button>
      </div>

      <!-- 我的配送 -->
      <h3 class="section-title">我的配送</h3>
      <div v-if="myOrders.length === 0" class="card empty">暂无配送订单</div>
      <div v-for="o in myOrders" :key="o.order_id" class="card order-card">
        <div class="order-header">
          <span class="order-id">#{{ o.order_id }}</span>
          <span class="order-status" :class="'status-' + o.status">{{ statusText(o.status) }}</span>
        </div>
        <div class="order-info">
          <div>商家：{{ o.merchant_name || '-' }}</div>
          <div>收货人：{{ o.contact_name || '-' }} {{ o.phone || '' }}</div>
          <div>地址：{{ o.province }}{{ o.city }}{{ o.district }}{{ o.detail }}</div>
          <div>金额：¥{{ o.actual_amount }}</div>
          <div v-if="o.remark">备注：{{ o.remark }}</div>
          <div v-if="o.items && o.items.length" class="items-summary">
            菜品：{{ o.items.map(i => `${i.dish_name} x${i.quantity}`).join('、') }}
          </div>
        </div>
        <button
          v-if="o.status === 3"
          class="btn btn-primary"
          @click="handleDeliver(o.order_id)"
          :disabled="delivering === o.order_id"
        >
          {{ delivering === o.order_id ? '处理中...' : '确认送达' }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { riderOrders, riderAvailableOrders, riderAcceptOrder, deliverOrder } from "../api";
import { statusText } from "../constants";

const availableOrders = ref([]);
const myOrders = ref([]);
const loading = ref(false);
const accepting = ref(null);
const delivering = ref(null);
const riderName = ref("");

async function fetchAll() {
  loading.value = true;
  try {
    const [availableRes, myRes] = await Promise.all([
      riderAvailableOrders(),
      riderOrders(),
    ]);
    availableOrders.value = availableRes.data;
    myOrders.value = myRes.data;
    const u = JSON.parse(localStorage.getItem("user") || "{}");
    riderName.value = u.nickname || "";
  } finally {
    loading.value = false;
  }
}

async function handleAccept(orderId) {
  accepting.value = orderId;
  try {
    await riderAcceptOrder(orderId);
    await fetchAll();
  } catch (e) {
    alert(e.response?.data?.error || "接单失败");
  } finally {
    accepting.value = null;
  }
}

async function handleDeliver(orderId) {
  delivering.value = orderId;
  try {
    await deliverOrder(orderId);
    await fetchAll();
  } catch (e) {
    alert(e.response?.data?.error || "操作失败");
  } finally {
    delivering.value = null;
  }
}

onMounted(fetchAll);
</script>

<style scoped>
.rider-page h2 { margin-bottom: 16px; }
.section-title { font-size: 16px; margin: 20px 0 12px; color: #333; }
.section-title:first-of-type { margin-top: 0; }
.toolbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px 16px; margin-bottom: 16px;
}
.toolbar span { font-size: 14px; font-weight: bold; }
.order-card { margin-bottom: 12px; }
.order-header { display: flex; justify-content: space-between; margin-bottom: 8px; }
.order-id { font-weight: bold; }
.order-status { font-size: 13px; padding: 2px 8px; border-radius: 4px; }
.status-2 { background: #dfe6e9; color: #636e72; }
.status-3 { background: #fff3e0; color: #e65100; }
.status-4 { background: #e8f5e9; color: #2e7d32; }
.status-5 { background: #fab1a0; color: #d63031; }
.status-6 { background: #e8f5e9; color: #2e7d32; }
.order-info { font-size: 13px; color: #666; line-height: 1.8; margin-bottom: 10px; }
.order-info div { margin-bottom: 2px; }
.items-summary { font-size: 12px; color: #ff6b00; margin-top: 4px; }
.loading, .empty { text-align: center; padding: 32px; color: #999; }
</style>
