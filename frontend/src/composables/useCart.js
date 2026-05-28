import { ref, computed, watch } from "vue";

const CART_KEY = "takeout_cart";

function load() {
  try {
    return JSON.parse(localStorage.getItem(CART_KEY) || "[]");
  } catch {
    return [];
  }
}

const items = ref(load());

function save() {
  localStorage.setItem(CART_KEY, JSON.stringify(items.value));
}

watch(items, save, { deep: true });

export function useCart() {
  const count = computed(() => items.value.reduce((s, i) => s + i.quantity, 0));
  const total = computed(() => items.value.reduce((s, i) => s + i.price * i.quantity, 0).toFixed(2));

  function cartQty(dish) {
    const item = items.value.find(i => i.dish_id === dish.dish_id);
    return item ? item.quantity : 0;
  }

  function addItem(dish, merchantId, merchantName) {
    if (items.value.length > 0 && items.value[0].merchant_id !== merchantId) {
      if (!confirm("购物车中有其他商家的菜品，是否清空并重新选购？")) return;
      items.value = [];
    }
    const idx = items.value.findIndex(i => i.dish_id === dish.dish_id);
    if (idx >= 0) {
      items.value[idx].quantity++;
    } else {
      items.value.push({
        dish_id: dish.dish_id,
        name: dish.name,
        price: dish.price,
        quantity: 1,
        merchant_id: merchantId,
        merchant_name: merchantName,
      });
    }
  }

  function removeItem(dish) {
    const idx = items.value.findIndex(i => i.dish_id === dish.dish_id);
    if (idx >= 0) {
      items.value[idx].quantity--;
      if (items.value[idx].quantity <= 0) {
        items.value.splice(idx, 1);
      }
    }
  }

  function clearCart() {
    items.value = [];
  }

  function incItem(item) {
    item.quantity++;
  }

  function decItem(item) {
    item.quantity--;
    if (item.quantity <= 0) {
      items.value = items.value.filter(i => i.dish_id !== item.dish_id);
    }
  }

  return { items, count, total, cartQty, addItem, removeItem, clearCart, incItem, decItem };
}
