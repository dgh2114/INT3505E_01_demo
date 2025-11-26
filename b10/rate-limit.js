// rate-limit.js
const rateLimit = require("express-rate-limit");

const paymentLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 phút
  max: 7, // tối đa 10 request
  message: {
    error: "Quá nhiều yêu cầu, vui lòng thử lại sau."
  }
});

module.exports = paymentLimiter;
