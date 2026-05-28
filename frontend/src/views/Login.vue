<template>
  <div class="login-page">
    <div class="login-card">
      <h2>外卖点餐系统</h2>
      <div class="tabs">
        <span :class="{ active: mode === 'login' }" @click="switchMode('login')">登录</span>
        <span :class="{ active: mode === 'register' }" @click="switchMode('register')">注册</span>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="field">
          <label>角色</label>
          <div class="role-tabs">
            <span :class="{ active: role === 'customer' }" @click="role = 'customer'">用户</span>
            <span :class="{ active: role === 'rider' }" @click="role = 'rider'">骑手</span>
            <span :class="{ active: role === 'merchant' }" @click="role = 'merchant'">商家</span>
          </div>
        </div>
        <div class="field">
          <label>手机号</label>
          <input v-model="phone" placeholder="请输入11位手机号" maxlength="11" />
        </div>
        <div class="field">
          <label>密码</label>
          <input v-model="password" type="password" placeholder="请输入密码" />
        </div>
        <div v-if="mode === 'register'" class="field">
          <label>昵称</label>
          <input v-model="nickname" placeholder="请输入昵称" />
        </div>
        <p v-if="error" class="error">{{ error }}</p>
        <button type="submit" class="btn btn-primary login-btn" :disabled="loading">
          {{ loading ? '处理中...' : (mode === 'login' ? '登录' : '注册') }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { login as apiLogin, register as apiRegister } from "../api";

const emit = defineEmits(["login"]);

const mode = ref("login");
const role = ref("customer");
const phone = ref("");
const password = ref("");
const nickname = ref("");
const error = ref("");
const loading = ref(false);

function switchMode(m) {
  mode.value = m;
  error.value = "";
}

async function handleSubmit() {
  error.value = "";
  if (!phone.value || !password.value) {
    error.value = "手机号和密码不能为空";
    return;
  }
  if (password.value.length < 6) {
    error.value = "密码长度不能少于6位";
    return;
  }
  if (mode.value === "register" && !nickname.value.trim()) {
    error.value = "昵称不能为空";
    return;
  }
  loading.value = true;
  try {
    const fn = mode.value === "login" ? apiLogin : apiRegister;
    const body = { phone: phone.value, password: password.value, role: role.value };
    if (mode.value === "register") body.nickname = nickname.value.trim();

    const { data } = await fn(body);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    localStorage.setItem("token", data.token);
    emit("login", data.user);
  } catch (e) {
    error.value = e.response?.data?.error || "请求失败";
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.login-page { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
.login-card { width: 360px; background: #fff; border-radius: 12px; padding: 32px; box-shadow: 0 2px 12px rgba(0,0,0,.08); }
h2 { text-align: center; margin-bottom: 20px; color: #ff6b00; }
.tabs { display: flex; justify-content: center; gap: 24px; margin-bottom: 24px; }
.tabs span { font-size: 15px; padding-bottom: 4px; cursor: pointer; color: #999; }
.tabs span.active { color: #ff6b00; border-bottom: 2px solid #ff6b00; font-weight: bold; }
.role-tabs { display: flex; gap: 12px; }
.role-tabs span { flex: 1; text-align: center; padding: 8px 0; border-radius: 6px; cursor: pointer; color: #999; background: #f5f5f5; font-size: 14px; }
.role-tabs span.active { color: #fff; background: #ff6b00; font-weight: bold; }
.field { margin-bottom: 14px; }
.field label { display: block; font-size: 13px; color: #666; margin-bottom: 4px; }
.field input { width: 100%; padding: 10px 12px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; outline: none; }
.field input:focus { border-color: #ff6b00; }
.error { color: #e74c3c; font-size: 13px; margin-bottom: 10px; }
.login-btn { width: 100%; padding: 12px; font-size: 16px; margin-top: 6px; }
</style>
