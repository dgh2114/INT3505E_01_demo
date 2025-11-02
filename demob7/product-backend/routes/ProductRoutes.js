const express = require("express");
const Product = require("../models/Product");
const router = express.Router();

// GET all products
router.get("/", async (req, res) => {
  const products = await Product.find();
  res.json(products);
});

// GET product by id
router.get("/:id", async (req, res) => {
  const product = await Product.findById(req.params.id);
  if (!product) return res.status(404).json({ message: "Product not found" });
  res.json(product);
});

// POST create product
router.post("/", async (req, res) => {
  const product = await Product.create(req.body);
  res.status(201).json(product);
});

// PUT update product
router.put("/:id", async (req, res) => {
  const product = await Product.findByIdAndUpdate(req.params.id, req.body, { new: true });
  res.json(product);
});

// DELETE product
router.delete("/:id", async (req, res) => {
  await Product.findByIdAndDelete(req.params.id);
  res.status(204).send();
});

module.exports = router;
