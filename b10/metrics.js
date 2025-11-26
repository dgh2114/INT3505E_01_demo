// metrics.js
const client = require("prom-client");

const register = new client.Registry();

// Thu thập metric mặc định của Node.js
client.collectDefaultMetrics({ register });

const requestCounter = new client.Counter({
  name: "api_request_count",
  help: "Number of API requests",
  labelNames: ["method", "route", "status"]
});

register.registerMetric(requestCounter);

function metricsMiddleware(req, res, next) {
  res.on("finish", () => {
    requestCounter.inc({
      method: req.method,
      route: req.originalUrl,
      status: res.statusCode
    });
  });
  next();
}

module.exports = { register, metricsMiddleware };
