<template>
  <div>
    <h1 class="page-title">订单详情</h1>

    <div class="card">
      <div class="order-status-bar">
        <span :class="`status status-${order.status}`">{{ statusText(order.status) }}</span>
        <span class="order-id">#{{ order.order_id }}</span>
      </div>
      <div class="order-info">
        <p>下单时间：{{ formatDate(order.created_at) }}</p>
        <p v-if="order.paid_at">支付时间：{{ formatDate(order.paid_at) }}</p>
        <p v-if="order.delivered_at">送达时间：{{ formatDate(order.delivered_at) }}</p>
      </div>
    </div>

    <!-- 菜品明细 -->
    <div class="card">
      <h4>菜品明细</h4>
      <div v-for="item in order.items" :key="item.item_id" class="item-row">
        <span>{{ item.dish_name }}</span>
        <span>x{{ item.quantity }}</span>
        <span>¥{{ (item.dish_price * item.quantity).toFixed(2) }}</span>
      </div>
      <div class="divider"></div>
      <div class="price-sum">
        <span>商品总价</span><span>¥{{ order.total_price }}</span>
      </div>
      <div class="price-sum">
        <span>配送费</span><span>¥{{ order.delivery_fee }}</span>
      </div>
      <div class="price-sum total">
        <span>实付</span><span>¥{{ order.actual_amount }}</span>
      </div>
    </div>

    <!-- 备注 -->
    <div v-if="order.remark" class="card">
      <h4>备注</h4>
      <p>{{ order.remark }}</p>
    </div>

    <!-- 操作按钮 -->
    <div class="actions">
      <button v-if="order.status === 1" class="btn btn-primary" @click="doPay">立即支付</button>
      <button v-if="order.status === 1 || order.status === 2 || order.status === 6" class="btn btn-cancel" @click="doCancel">取消订单</button>
      <button v-if="order.status === 4 && !order.review" class="btn btn-primary" @click="showReview = true">去评价</button>
    </div>

    <!-- 已评价 -->
    <div v-if="order.review" class="card">
      <h4>我的评价</h4>
      <p class="star">{"★".repeat(order.review.rating)}{"☆".repeat(5 - order.review.rating)}</p>
      <p v-if="order.review.content">{{ order.review.content }}</p>
    </div>

    <!-- 评价表单 -->
    <div v-if="showReview" class="card">
      <h4>评价订单</h4>
      <div class="rating-stars">
        <span v-for="s in 5" :key="s" class="star-btn" :class="{ on: s <= rating }"
              @click="rating = s">{{ s <= rating ? '★' : '☆' }}</span>
      </div>
      <textarea v-model="reviewContent" placeholder="写下你的评价（选填）" rows="3"></textarea>
      <p v-if="reviewError" class="error">{{ reviewError }}</p>
      <button class="btn btn-primary" @click="submitReview" :disabled="reviewSubmitting">
        {{ reviewSubmitting ? '提交中...' : '提交评价' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import { getOrder, payOrder, cancelOrder, createReview } from "../api";

const route = useRoute();
const order = ref({});
const showReview = ref(false);
const rating = ref(5);
const reviewContent = ref("");
const reviewError = ref("");
const reviewSubmitting = ref(false);

const STATUS_MAP = { 1: "待支付", 2: "待接单", 3: "配送中", 4: "已送达", 5: "已取消", 6: "待配送" };
function statusText(s) { return STATUS_MAP[s] || "未知"; }
function formatDate(d) { return d ? new Date(d).toLocaleString("zh-CN") : ""; }

async function loadOrder() {
  try {
    const { data } = await getOrder(route.params.id);
    order.value = data;
  } catch {}
}

async function doPay() {
  try {
    await payOrder(order.value.order_id);
    await loadOrder();
  } catch {}
}

async function doCancel() {
  if (!confirm("确定取消订单？")) return;
  try {
    await cancelOrder(order.value.order_id);
    await loadOrder();
  } catch {}
}

async function submitReview() {
  reviewError.value = "";
  reviewSubmitting.value = true;
  try {
    await createReview({
      order_id: order.value.order_id,
      rating: rating.value,
      content: reviewContent.value,
    });
    showReview.value = false;
    await loadOrder();
  } catch (e) {
    reviewError.value = e.response?.data?.error || "评价失败";
  } finally {
    reviewSubmitting.value = false;
  }
}

onMounted(loadOrder);
</script>

<style scoped>
.page-title { font-size: 20px; margin-bottom: 16px; }

.order-status-bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.order-id { font-size: 12px; color: #aaa; }
.order-info { font-size: 13px; color: #888; }
.order-info p { margin-bottom: 2px; }

.status { font-size: 14px; padding: 3px 12px; border-radius: 4px; font-weight: bold; }
.status-1 { background: #ffeaa7; color: #d68910; }
.status-2 { background: #dfe6e9; color: #636e72; }
.status-3 { background: #74b9ff; color: #0984e3; }
.status-4 { background: #55efc4; color: #00b894; }
.status-5 { background: #fab1a0; color: #d63031; }
.status-6 { background: #e8f5e9; color: #2e7d32; }

.item-row { display: flex; gap: 12px; font-size: 14px; padding: 4px 0; }
.item-row span:first-child { flex: 1; }
.divider { border-top: 1px solid #f0f0f0; margin: 8px 0; }
.price-sum { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 2px; }
.total { font-weight: bold; font-size: 16px; margin-top: 4px; }

.actions { display: flex; gap: 12px; margin: 16px 0; }
.btn-cancel { background: #fff; border: 1px solid #ddd; color: #999; padding: 8px 20px; border-radius: 6px; font-size: 14px; cursor: pointer; }

.star { color: #ff9c00; font-size: 18px; }
.star-btn { font-size: 28px; cursor: pointer; color: #ddd; }
.star-btn.on { color: #ff9c00; }

textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; outline: none; margin: 10px 0; resize: vertical; }
.error { color: #e74c3c; font-size: 13px; margin-bottom: 8px; }

h4 { font-size: 14px; color: #555; margin-bottom: 8px; }
</style>
