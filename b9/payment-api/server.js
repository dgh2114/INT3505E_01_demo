const express = require("express");
const app = express();

const paymentsV1 = require("./routes/payments_v1");
const paymentsV2 = require("./routes/payments_v2");

app.use(express.json());

// Version theo URL
app.use("/api/v1/payments", paymentsV1);
app.use("/api/v2/payments", paymentsV2);

// Version theo header
app.post("/api/payments", (req, res, next) => {
  const version = req.header("Accept-Version");

  if (version === "2") {
    return paymentsV2(req, res, next);  // gọi router v2
  } else {
    return paymentsV1(req, res, next);  // gọi router v1
  }
});

app.get("/", (req, res) => {
  res.json({ message: "Payment API versioning demo" });
});

const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server is running at http://localhost:${PORT}`);
});
