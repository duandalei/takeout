import { createRouter, createWebHashHistory } from "vue-router";

const routes = [
  {
    path: "/",
    redirect: "/home",
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/Login.vue"),
  },
  {
    path: "/home",
    name: "Home",
    component: () => import("../views/Home.vue"),
  },
  {
    path: "/merchant/:id",
    name: "Merchant",
    component: () => import("../views/Merchant.vue"),
  },
  {
    path: "/cart",
    name: "Cart",
    component: () => import("../views/Cart.vue"),
  },
  {
    path: "/orders",
    name: "Orders",
    component: () => import("../views/Orders.vue"),
  },
  {
    path: "/order/:id",
    name: "OrderDetail",
    component: () => import("../views/OrderDetail.vue"),
  },
  {
    path: "/addresses",
    name: "Addresses",
    component: () => import("../views/Addresses.vue"),
  },
  {
    path: "/rider",
    name: "Rider",
    component: () => import("../views/Rider.vue"),
    meta: { role: "rider" },
  },
  {
    path: "/merchant/dashboard",
    name: "MerchantDashboard",
    component: () => import("../views/MerchantDashboard.vue"),
    meta: { role: "merchant" },
  },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

// 路由守卫：未登录重定向 + 角色校验
router.beforeEach((to) => {
  const token = localStorage.getItem("token");
  if (!token && to.name !== "Login") {
    return { name: "Login" };
  }
  if (token && to.name === "Login") {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    if (user.role === "rider") return { name: "Rider" };
    if (user.role === "merchant") return { name: "MerchantDashboard" };
    return { name: "Home" };
  }
  if (to.meta.role) {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    if (user.role !== to.meta.role) {
      return { name: "Home" };
    }
  }
});

export default router;
