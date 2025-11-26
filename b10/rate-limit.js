// rate-limit.js
const rateLimit = require("express-rate-limit");

const paymentLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 phút
  max: 10, // tối đa 10 request
  message: {
    error: "Too many requests, please try again later."
  }
});

module.exports = paymentLimiter;
