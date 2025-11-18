const express = require("express");
const { v4: uuidv4 } = require("uuid");

const router = express.Router();

router.use((req, res, next) => {
  res.setHeader("Deprecation", "true");
  res.setHeader("Sunset", "2026-01-01T00:00:00Z");
  res.setHeader("Link", '</docs/api-v1-deprecation>; rel="deprecation"');
  next();
});

router.post("/", (req, res) => {
  const { amount, description } = req.body;

  if (!amount) {
    return res.status(400).json({ error: "amount is required in v1" });
  }

  const paymentId = uuidv4();

  res.status(201).json({
    id: paymentId,
    amount,
    description: description || null,
    status: "PENDING"
  });
});

module.exports = router;
