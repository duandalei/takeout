<template>
  <div>
    <h1 class="page-title">订单详情</h1>

    <div class="card">
      <div class="order-status-bar">
        <span :class="`status status-${order.status}`">{{ statusText(order.status) }}</span>
        <span class="order-id">#{{ order.order_id }}</span>
      </div>
      <!-- 状态进度条 -->
      <div v-if="order.status !== 5" class="progress-bar">
        <div v-for="(step, idx) in steps" :key="idx" class="step" :class="{ done: step.done, current: step.current }">
          <div class="step-dot"><span v-if="step.done">&#10003;</span></div>
          <div class="step-label">{{ step.label }}</div>
          <div v-if="idx < steps.length - 1" class="step-line" :class="{ filled: step.done }"></div>
        </div>
      </div>
      <div v-else class="cancelled-notice">此订单已取消</div>
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

    <!-- 配送地址 -->
    <div v-if="order.address" class="card">
      <h4>配送地址</h4>
      <p>{{ order.address.contact_name }} {{ order.address.phone }}</p>
      <p class="addr-detail">{{ order.address.province }}{{ order.address.city }}{{ order.address.district }} {{ order.address.detail }}</p>
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
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { getOrder, payOrder, cancelOrder, createReview } from "../api";
import { STATUS_FLOW, STATUS_MAP, statusText } from "../constants";

const route = useRoute();
const order = ref({});

const steps = computed(() => {
  const s = order.value.status;
  if (s === 5) return [];
  const currentIdx = STATUS_FLOW.indexOf(s);
  return STATUS_FLOW.map((code, idx) => ({
    label: STATUS_MAP[code],
    done: idx < currentIdx,
    current: idx === currentIdx,
  }));
});
const showReview = ref(false);
const rating = ref(5);
const reviewContent = ref("");
const reviewError = ref("");
const reviewSubmitting = ref(false);

function formatDate(d) { return d ? new Date(d).toLocaleString("zh-CN") : ""; }

async function loadOrder() {
  try {
    const { data } = await getOrder(route.params.id);
    order.value = data;
  } catch (e) {
    console.error("加载订单失败:", e);
  }
}

async function doPay() {
  if (!confirm("确认支付 ¥" + order.value.actual_amount + "？")) return;
  try {
    await payOrder(order.value.order_id);
    await loadOrder();
  } catch (e) {
    console.error("支付失败:", e);
    alert("支付失败，请重试");
  }
}

async function doCancel() {
  if (!confirm("确定取消订单？")) return;
  try {
    await cancelOrder(order.value.order_id);
    await loadOrder();
  } catch (e) {
    console.error("取消订单失败:", e);
  }
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

.addr-detail { font-size: 13px; color: #888; margin-top: 2px; }

.progress-bar { display: flex; align-items: flex-start; margin: 16px 0; padding: 0 4px; }
.step { display: flex; flex-direction: column; align-items: center; position: relative; flex: 1; }
.step-dot { width: 24px; height: 24px; border-radius: 50%; background: #e0e0e0; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #fff; z-index: 1; }
.step.done .step-dot { background: #ff6b00; }
.step.current .step-dot { background: #ff6b00; box-shadow: 0 0 0 4px rgba(255,107,0,.2); }
.step-label { font-size: 11px; color: #bbb; margin-top: 4px; white-space: nowrap; }
.step.done .step-label,
.step.current .step-label { color: #ff6b00; font-weight: bold; }
.step-line { position: absolute; top: 12px; left: 50%; width: 100%; height: 2px; background: #e0e0e0; z-index: 0; }
.step-line.filled { background: #ff6b00; }

.cancelled-notice { text-align: center; padding: 12px; color: #d63031; font-size: 14px; font-weight: bold; background: #fff0f0; border-radius: 6px; margin: 8px 0; }

h4 { font-size: 14px; color: #555; margin-bottom: 8px; }
</style>
