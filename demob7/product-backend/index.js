const express = require("express");
const app = express();
require("dotenv").config();
app.use(express.json());

const mongoose = require("mongoose");
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log("✅ MongoDB connected"))
  .catch(err => console.error("❌ DB Error:", err));

const productRoutes = require("./routes/ProductRoutes");
app.use("/api/products", productRoutes);

app.listen(process.env.PORT || 3000, () =>
  console.log(`🚀 Server running at http://localhost:${process.env.PORT || 3000}`)
);
