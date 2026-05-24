<template>
  <div>
    <div class="card merchant-header">
      <h2>{{ merchant.name }}</h2>
      <div class="merchant-meta">
        <span>★ {{ merchant.rating }}</span>
        <span>月售 {{ merchant.monthly_sales }}</span>
        <span>起送 ¥{{ merchant.min_delivery_price }}</span>
        <span>配送 ¥{{ merchant.delivery_fee }}</span>
      </div>
    </div>

    <!-- 分类导航 -->
    <div class="cat-tabs">
      <button v-for="cat in menu" :key="cat.category_id"
              :class="{ active: activeCat === cat.category_id }"
              @click="activeCat = cat.category_id">
        {{ cat.category_name }}
      </button>
    </div>

    <!-- 菜品列表 -->
    <div v-for="cat in menu.filter(c => c.category_id === activeCat)" :key="cat.category_id">
      <div v-for="d in cat.dishes" :key="d.dish_id" class="card dish-item">
        <div class="dish-info">
          <h4>{{ d.name }}</h4>
          <p v-if="d.description" class="desc">{{ d.description }}</p>
          <p class="sales">月售 {{ d.monthly_sales }}</p>
          <p class="price">¥{{ d.price }}</p>
        </div>
        <div class="dish-actions">
          <button class="btn btn-add" @click="removeFromCart(d)" :disabled="cartQty(d) <= 0">-</button>
          <span class="qty">{{ cartQty(d) }}</span>
          <button class="btn btn-add" @click="addToCart(d)">+</button>
        </div>
      </div>
    </div>

    <!-- 购物车浮条 -->
    <div v-if="cartCount > 0" class="cart-bar">
      <div class="cart-bar-inner">
        <span class="cart-icon">🛒 {{ cartCount }} 件</span>
        <span>¥{{ cartTotal }}</span>
        <button class="cart-go-btn" @click="$router.push('/cart')">去结算</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import { getMerchant, getMerchantMenu } from "../api";

const route = useRoute();
const merchant = ref({});
const menu = ref([]);
const activeCat = ref(null);

const CART_KEY = "takeout_cart";

function loadCart() {
  try { return JSON.parse(localStorage.getItem(CART_KEY) || "[]"); }
  catch { return []; }
}
function saveCart(c) { localStorage.setItem(CART_KEY, JSON.stringify(c)); }

const cart = ref(loadCart());

const cartCount = computed(() => cart.value.reduce((s, i) => s + i.quantity, 0));
const cartTotal = computed(() => cart.value.reduce((s, i) => s + i.price * i.quantity, 0).toFixed(2));

function cartQty(dish) {
  const item = cart.value.find(i => i.dish_id === dish.dish_id);
  return item ? item.quantity : 0;
}

function addToCart(dish) {
  const idx = cart.value.findIndex(i => i.dish_id === dish.dish_id);
  if (idx >= 0) {
    cart.value[idx].quantity++;
  } else {
    cart.value.push({
      dish_id: dish.dish_id,
      name: dish.name,
      price: dish.price,
      quantity: 1,
      merchant_id: merchant.value.merchant_id,
      merchant_name: merchant.value.name,
    });
  }
  saveCart(cart.value);
}

function removeFromCart(dish) {
  const idx = cart.value.findIndex(i => i.dish_id === dish.dish_id);
  if (idx >= 0) {
    cart.value[idx].quantity--;
    if (cart.value[idx].quantity <= 0) {
      cart.value.splice(idx, 1);
    }
  }
  saveCart(cart.value);
}

onMounted(async () => {
  const id = route.params.id;
  try {
    const { data } = await getMerchant(id);
    Object.assign(merchant.value, data);
    menu.value = data.menu || [];
    if (menu.value.length) activeCat.value = menu.value[0].category_id;
  } catch {}
});
</script>

<style scoped>
.merchant-header { margin-bottom: 12px; }
.merchant-header h2 { font-size: 20px; margin-bottom: 6px; }
.merchant-meta { display: flex; gap: 14px; font-size: 13px; color: #888; }

.cat-tabs { display: flex; gap: 0; margin-bottom: 12px; flex-wrap: wrap; }
.cat-tabs button { padding: 6px 16px; border: 1px solid #ddd; background: #fff; cursor: pointer; font-size: 13px; }
.cat-tabs button.active { background: #ff6b00; color: #fff; border-color: #ff6b00; }

.dish-item { display: flex; align-items: center; }
.dish-info { flex: 1; }
.dish-info h4 { font-size: 15px; margin-bottom: 2px; }
.desc { font-size: 12px; color: #999; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 400px; }
.sales { font-size: 12px; color: #aaa; margin-bottom: 2px; }
.price { font-size: 17px; color: #ff6b00; font-weight: bold; }

.dish-actions { display: flex; align-items: center; gap: 8px; }
.btn-add { width: 28px; height: 28px; border-radius: 50%; background: #ff6b00; color: #fff; border: none; font-size: 16px; cursor: pointer; display: flex; align-items: center; justify-content: center; }
.btn-add:disabled { background: #ccc; }
.qty { min-width: 20px; text-align: center; font-size: 14px; }

.cart-bar { position: fixed; bottom: 0; left: 0; right: 0; background: #333; color: #fff; z-index: 50; }
.cart-bar-inner { max-width: 960px; margin: 0 auto; display: flex; align-items: center; padding: 12px 20px; gap: 12px; }
.cart-icon { background: #ff6b00; padding: 2px 10px; border-radius: 12px; font-size: 14px; }
.cart-go-btn { margin-left: auto; background: #ff6b00; color: #fff; border: none; padding: 8px 22px; border-radius: 20px; font-size: 15px; font-weight: bold; cursor: pointer; }
.cart-go-btn:hover { background: #e55d00; }
</style>
