<template>
  <div id="app-container">
    <header v-if="isLoggedIn" class="topbar">
      <div class="topbar-inner">
        <div class="logo" @click="$router.push('/home')">外卖点餐</div>
        <nav>
          <router-link to="/home">首页</router-link>
          <template v-if="userRole === 'customer'">
            <router-link to="/cart">购物车</router-link>
            <router-link to="/orders">我的订单</router-link>
            <router-link to="/addresses">地址管理</router-link>
          </template>
          <template v-if="userRole === 'rider'">
            <router-link to="/rider">骑手面板</router-link>
          </template>
          <template v-if="userRole === 'merchant'">
            <router-link to="/merchant/dashboard">商家面板</router-link>
          </template>
        </nav>
        <div class="user-info">
          <span>{{ userName }}</span>
          <button class="btn-text" @click="logout">退出</button>
        </div>
      </div>
    </header>
    <main>
      <router-view @login="onLogin" />
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const isLoggedIn = ref(!!localStorage.getItem("token"));
const userRole = computed(() => {
  const u = localStorage.getItem("user");
  return u ? JSON.parse(u).role : "";
});
const userName = computed(() => {
  const u = localStorage.getItem("user");
  return u ? JSON.parse(u).nickname : "";
});

function onLogin(user) {
  localStorage.setItem("user", JSON.stringify(user));
  isLoggedIn.value = true;
  if (user.role === "rider") router.push("/rider");
  else if (user.role === "merchant") router.push("/merchant/dashboard");
  else router.push("/home");
}

function logout() {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  isLoggedIn.value = false;
  router.push("/login");
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, "Microsoft YaHei", sans-serif; background: #f5f5f5; color: #333; }

.topbar { background: #ff6b00; color: #fff; position: sticky; top: 0; z-index: 100; }
.topbar-inner { max-width: 960px; margin: 0 auto; display: flex; align-items: center; padding: 0 16px; height: 48px; gap: 20px; }
.logo { font-size: 18px; font-weight: bold; cursor: pointer; }
nav { display: flex; gap: 12px; }
nav a { color: #fff; text-decoration: none; font-size: 14px; opacity: 0.85; }
nav a.router-link-active { opacity: 1; font-weight: bold; }
.user-info { margin-left: auto; display: flex; align-items: center; gap: 8px; font-size: 14px; }
.btn-text { background: none; border: 1px solid rgba(255,255,255,.5); color: #fff; padding: 2px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; }

main { max-width: 960px; margin: 0 auto; padding: 16px; }

.btn { display: inline-block; padding: 8px 20px; border: none; border-radius: 6px; font-size: 14px; cursor: pointer; }
.btn-primary { background: #ff6b00; color: #fff; }
.btn-primary:hover { background: #e55d00; }
.btn-disabled { background: #ccc; color: #999; cursor: not-allowed; }

.card { background: #fff; border-radius: 10px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,.06); }
</style>
