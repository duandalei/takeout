import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 10000,
});

// 请求拦截器：自动带 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器：401 跳转登录
api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response && err.response.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

// ---- 认证 ----
export const login = (data) => api.post("/auth/login", data);
export const register = (data) => api.post("/auth/register", data);
export const getMe = () => api.get("/auth/me");

// ---- 商家 ----
export const getMerchants = () => api.get("/merchants");
export const getMerchant = (id) => api.get(`/merchants/${id}`);

// ---- 菜品 ----

// ---- 地址 ----
export const getAddresses = () => api.get("/addresses");
export const createAddress = (data) => api.post("/addresses", data);
export const updateAddress = (id, data) => api.put(`/addresses/${id}`, data);
export const deleteAddress = (id) => api.delete(`/addresses/${id}`);

// ---- 订单 ----
export const createOrder = (data) => api.post("/orders", data);
export const getMyOrders = () => api.get("/orders");
export const getOrder = (id) => api.get(`/orders/${id}`);
export const payOrder = (id) => api.put(`/orders/${id}/pay`);
export const cancelOrder = (id) => api.put(`/orders/${id}/cancel`);
export const merchantOrders = (status) =>
  api.get("/merchant/orders", { params: { status } });
export const acceptOrder = (id) => api.put(`/merchant/orders/${id}/accept`);

// ---- 骑手 ----
export const riderOrders = () =>
  api.get("/rider/orders");
export const riderAvailableOrders = () =>
  api.get("/rider/available");
export const riderAcceptOrder = (id) => api.put(`/rider/orders/${id}/accept`);
export const deliverOrder = (id) => api.put(`/rider/orders/${id}/deliver`);

// ---- 评价 ----
export const createReview = (data) => api.post("/reviews", data);
export const getMerchantReviews = (merchantId) =>
  api.get(`/reviews/merchant/${merchantId}`);

export default api;
