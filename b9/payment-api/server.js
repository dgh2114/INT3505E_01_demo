// server.js
const express = require("express");
const app = express();

const paymentsV1 = require("./routes/payments.v1");
const paymentsV2 = require("./routes/payments.v2");

app.use(express.json());

// ========== Version theo URL ==========
app.use("/api/v1/payments", paymentsV1);
app.use("/api/v2/payments", paymentsV2);

// ========== Gateway: version theo header ==========
// Client gọi POST /api/payments
// - Nếu gửi Accept-Version: 2 -> dùng v2
// - Nếu không -> fallback v1
app.post("/api/payments", (req, res, next) => {
  const version = req.header("Accept-Version");

  if (version === "2") {
    // Chuyển tiếp sang handler v2
    // Trick đơn giản: đổi url rồi cho chạy tiếp qua stack middleware
    req.url = "/";         // root của router v2
    return paymentsV2.handle(req, res, next);
  } else {
    // Mặc định: v1
    req.url = "/";
    return paymentsV1.handle(req, res, next);
  }
});

// Health check
app.get("/", (req, res) => {
  res.json({ message: "Payment API versioning demo" });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server listening on http://localhost:${PORT}`);
});
