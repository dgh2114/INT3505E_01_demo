// routes/payments.v1.js
const express = require("express");
const { v4: uuidv4 } = require("uuid");

const router = express.Router();

// Middleware thêm header deprecation cho v1
router.use((req, res, next) => {
  // Thông báo đây là API deprecated
  res.setHeader("Deprecation", "true");
  // Dự kiến ngày "sunset" (ngừng hỗ trợ hẳn)
  res.setHeader("Sunset", "2026-01-01T00:00:00Z");
  // Link tới docs thông báo deprecation (ví dụ)
  res.setHeader("Link", '</docs/api-v1-deprecation>; rel="deprecation"');
  next();
});

/**
 * POST /api/v1/payments
 * Body:
 * {
 *   "amount": 100000,
 *   "description": "Top-up"
 * }
 * 
 * Đơn giản: không có currency, không có idempotency key.
 */
router.post("/", (req, res) => {
  const { amount, description } = req.body;

  if (!amount) {
    return res.status(400).json({
      error: "amount is required in v1"
    });
  }

  const paymentId = uuidv4();

  // Response kiểu v1 (đơn giản)
  res.status(201).json({
    id: paymentId,
    amount,
    description: description || null,
    status: "PENDING"
  });
});

module.exports = router;
