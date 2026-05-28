export const STATUS_MAP = {
  1: "待支付",
  2: "待接单",
  3: "配送中",
  4: "已送达",
  5: "已取消",
  6: "待配送",
};

export const STATUS_FLOW = [1, 2, 6, 3, 4];

export function statusText(s) {
  return STATUS_MAP[s] || "未知";
}
