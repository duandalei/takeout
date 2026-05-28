<template>
  <div>
    <h1 class="page-title">购物车</h1>

    <div v-if="cart.length === 0" class="empty-card card">
      <p>购物车是空的</p>
      <button class="btn btn-primary" @click="$router.push('/home')">去逛逛</button>
    </div>

    <template v-else>
      <div class="card">
        <div class="cart-merchant">
          <strong>{{ cart[0].merchant_name }}</strong>
          <span class="merchant-meta">起送 ¥{{ merchant.min_delivery_price }} | 配送 ¥{{ merchant.delivery_fee }}</span>
        </div>
        <div v-for="item in cart" :key="item.dish_id" class="cart-item">
          <span class="item-name">{{ item.name }}</span>
          <span class="item-price">¥{{ item.price }}</span>
          <div class="item-qty">
            <button @click="decItem(item)">-</button>
            <span>{{ item.quantity }}</span>
            <button @click="incItem(item)">+</button>
          </div>
          <span class="item-sub">¥{{ (item.price * item.quantity).toFixed(2) }}</span>
        </div>
      </div>

      <!-- 选择地址 -->
      <div class="card">
        <h4>配送地址</h4>
        <select v-model="addressId" class="addr-select">
          <option v-for="a in addresses" :key="a.address_id" :value="a.address_id">
            {{ a.contact_name }} {{ a.phone }} — {{ a.province }}{{ a.city }}{{ a.district }}{{ a.detail }}
          </option>
        </select>
        <p v-if="!addresses.length" class="error">请先 <router-link to="/addresses">添加地址</router-link></p>
      </div>

      <!-- 备注 -->
      <div class="card">
        <h4>备注</h4>
        <input v-model="remark" placeholder="选填：口味、配送要求等" class="remark-input" />
      </div>

      <!-- 提交 -->
      <div class="card summary">
        <div class="sum-line"><span>商品总价</span><span>¥{{ totalPrice }}</span></div>
        <div class="sum-line"><span>配送费</span><span>¥{{ deliveryFee }}</span></div>
        <div class="sum-line total"><span>实付</span><span>¥{{ actualAmount }}</span></div>
        <p v-if="totalPrice < minPrice" class="error">还差 ¥{{ (minPrice - totalPrice).toFixed(2) }} 达到起送价</p>
        <p v-if="error" class="error">{{ error }}</p>
        <button
          class="btn btn-primary submit-btn"
          :disabled="totalPrice < minPrice || !addressId || submitting"
          @click="submitOrder"
        >
          {{ submitting ? '下单中...' : '提交订单' }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { getMerchant, getAddresses, createOrder } from "../api";
import { useCart } from "../composables/useCart";

const router = useRouter();
const { items: cart, total: cartTotal, incItem, decItem, clearCart } = useCart();
const addresses = ref([]);
const addressId = ref(null);
const remark = ref("");
const error = ref("");
const submitting = ref(false);
const merchant = ref({ min_delivery_price: 0, delivery_fee: 0 });

const totalPrice = computed(() => cart.value.reduce((s, i) => s + i.price * i.quantity, 0));
const deliveryFee = computed(() => cart.value.length > 0 ? Number(merchant.value.delivery_fee) : 0);
const actualAmount = computed(() => (totalPrice.value + deliveryFee.value).toFixed(2));
const minPrice = computed(() => Number(merchant.value.min_delivery_price));

onMounted(async () => {
  if (cart.value.length > 0) {
    try {
      const { data } = await getMerchant(cart.value[0].merchant_id);
      Object.assign(merchant.value, data);
    } catch (e) {
      console.error("加载商家信息失败:", e);
    }
  }
  try {
    const { data } = await getAddresses();
    addresses.value = data;
    if (data.length) addressId.value = data.find(a => a.is_default)?.address_id || data[0].address_id;
  } catch (e) {
    console.error("加载地址失败:", e);
  }
});

async function submitOrder() {
  error.value = "";
  submitting.value = true;
  try {
    const { data } = await createOrder({
      merchant_id: cart.value[0].merchant_id,
      address_id: addressId.value,
      items: cart.value.map(i => ({ dish_id: i.dish_id, quantity: i.quantity })),
      remark: remark.value,
    });
    clearCart();
    router.push(`/order/${data.order_id}`);
  } catch (e) {
    error.value = e.response?.data?.error || "下单失败";
  } finally {
    submitting.value = false;
  }
}
</script>

<style scoped>
.page-title { font-size: 20px; margin-bottom: 16px; }

.cart-merchant { margin-bottom: 12px; }
.cart-merchant .merchant-meta { font-size: 12px; color: #999; margin-left: 12px; }

.cart-item { display: flex; align-items: center; gap: 12px; padding: 10px 0; border-bottom: 1px solid #f0f0f0; font-size: 14px; }
.cart-item:last-child { border-bottom: none; }
.item-name { flex: 1; }
.item-price { color: #ff6b00; }
.item-qty { display: flex; align-items: center; gap: 6px; }
.item-qty button { width: 22px; height: 22px; border: 1px solid #ddd; background: #fff; border-radius: 4px; cursor: pointer; }
.item-sub { font-weight: bold; }

.addr-select { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; outline: none; margin-top: 6px; }

.remark-input { width: 100%; padding: 8px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; outline: none; margin-top: 6px; }

.summary { text-align: right; }
.sum-line { display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 6px; }
.total { font-size: 18px; font-weight: bold; margin-top: 8px; padding-top: 8px; border-top: 1px solid #f0f0f0; }
.error { color: #e74c3c; font-size: 13px; margin-top: 6px; }
.submit-btn { margin-top: 12px; padding: 10px 40px; font-size: 16px; }

.empty-card { text-align: center; padding: 60px 0; }
.empty-card p { margin-bottom: 12px; color: #999; }

h4 { font-size: 14px; margin-bottom: 0; color: #555; }
</style>
