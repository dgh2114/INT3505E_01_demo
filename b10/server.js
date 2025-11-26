const express = require("express");
const logger = require("./logger");
const { register, metricsMiddleware } = require("./metrics");
const paymentLimiter = require("./rate-limit");

const app = express();
app.use(express.json());

// Logging middleware
app.use((req, res, next) => {
  logger.info({
    message: "Incoming request",
    method: req.method,
    route: req.originalUrl
  });
  next();
});

// Metrics middleware
app.use(metricsMiddleware);

// Rate limited endpoint
app.post("/api/pay", paymentLimiter, (req, res) => {
  res.json({ status: "Payment processed" });
});

// Normal endpoint
app.get("/api/hello", (req, res) => {
  res.json({ message: "Hello!" });
});

// Prometheus metrics endpoint
app.get("/metrics", async (req, res) => {
  res.set("Content-Type", register.contentType);
  res.end(await register.metrics());
});

const PORT = 3000;
app.listen(PORT, () => {
  logger.info(`Server is running on http://localhost:${PORT}`);
});
