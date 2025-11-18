const express = require("express");
const { v4: uuidv4 } = require("uuid");

const router = express.Router();

router.post("/", (req, res) => {
  const { amount, currency, description, idempotency_key } = req.body;

  if (!amount || !currency) {
    return res.status(400).json({
      error: "amount and currency are required in v2"
    });
  }

  const paymentId = uuidv4();

  res.status(201).json({
    payment: {
      id: paymentId,
      amount,
      currency,
      description: description || null,
      status: "PENDING"
    },
    metadata: {
      version: "v2",
      idempotency_key: idempotency_key || null
    }
  });
});

module.exports = router;
