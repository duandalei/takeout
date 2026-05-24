<template>
  <div>
    <h1 class="page-title">地址管理</h1>

    <div v-for="a in addresses" :key="a.address_id" class="card addr-card">
      <div>
        <strong>{{ a.contact_name }}</strong>
        <span class="phone">{{ a.phone }}</span>
        <span v-if="a.is_default" class="tag-default">默认</span>
      </div>
      <p class="addr-detail">{{ a.province }}{{ a.city }}{{ a.district }} {{ a.detail }}</p>
      <button class="btn-text" @click="delAddr(a.address_id)">删除</button>
    </div>

    <div v-if="!addresses.length && !loading" class="empty">暂无地址，请添加</div>

    <button class="btn btn-primary" style="margin-top:16px" @click="showForm = !showForm">
      {{ showForm ? '收起' : '添加地址' }}
    </button>

    <div v-if="showForm" class="card" style="margin-top:12px">
      <h4>新增地址</h4>
      <div class="form-grid">
        <div class="field">
          <label>联系人 *</label>
          <input v-model="form.contact_name" />
        </div>
        <div class="field">
          <label>电话 *</label>
          <input v-model="form.phone" />
        </div>
        <div class="field">
          <label>省</label>
          <input v-model="form.province" />
        </div>
        <div class="field">
          <label>市</label>
          <input v-model="form.city" />
        </div>
        <div class="field">
          <label>区</label>
          <input v-model="form.district" />
        </div>
        <div class="field full">
          <label>详细地址 *</label>
          <input v-model="form.detail" placeholder="街道、门牌号等" />
        </div>
        <div class="field">
          <label><input type="checkbox" v-model="form.is_default" /> 设为默认</label>
        </div>
      </div>
      <p v-if="formError" class="error">{{ formError }}</p>
      <button class="btn btn-primary" @click="addAddr" :disabled="formSubmitting">
        {{ formSubmitting ? '添加中...' : '保存' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from "vue";
import { getAddresses, createAddress, deleteAddress } from "../api";

const addresses = ref([]);
const loading = ref(false);
const showForm = ref(false);
const formError = ref("");
const formSubmitting = ref(false);
const form = reactive({
  contact_name: "",
  phone: "",
  province: "",
  city: "",
  district: "",
  detail: "",
  is_default: false,
});

async function loadAddrs() {
  loading.value = true;
  try {
    const { data } = await getAddresses();
    addresses.value = data;
  } finally {
    loading.value = false;
  }
}

async function addAddr() {
  formError.value = "";
  if (!form.contact_name || !form.phone || !form.detail) {
    formError.value = "联系人、电话和详细地址必填";
    return;
  }
  formSubmitting.value = true;
  try {
    await createAddress({ ...form, is_default: form.is_default ? 1 : 0 });
    showForm.value = false;
    Object.keys(form).forEach(k => form[k] = "");
    await loadAddrs();
  } catch (e) {
    formError.value = e.response?.data?.error || "添加失败";
  } finally {
    formSubmitting.value = false;
  }
}

async function delAddr(id) {
  if (!confirm("确定删除该地址？")) return;
  try {
    await deleteAddress(id);
    await loadAddrs();
  } catch {}
}

onMounted(loadAddrs);
</script>

<style scoped>
.page-title { font-size: 20px; margin-bottom: 16px; }

.addr-card { font-size: 14px; }
.addr-card strong { margin-right: 8px; }
.phone { color: #888; font-size: 13px; margin-left: 6px; }
.tag-default { font-size: 11px; background: #ff6b00; color: #fff; padding: 1px 6px; border-radius: 3px; margin-left: 6px; }
.addr-detail { color: #666; margin: 4px 0; font-size: 13px; }
.addr-card .btn-text { color: #e74c3c; font-size: 12px; background: none; border: none; cursor: pointer; padding: 0; margin-top: 4px; }

.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 8px; }
.field.full { grid-column: 1 / 3; }
.field label { display: block; font-size: 13px; color: #666; margin-bottom: 2px; }
.field input { width: 100%; padding: 8px 10px; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; outline: none; }
.field input:focus { border-color: #ff6b00; }

.error { color: #e74c3c; font-size: 13px; margin: 8px 0; }
.empty { text-align: center; color: #999; margin-top: 40px; }

h4 { font-size: 15px; margin-bottom: 0; }
.btn-text { background: none; border: none; cursor: pointer; }
</style>
