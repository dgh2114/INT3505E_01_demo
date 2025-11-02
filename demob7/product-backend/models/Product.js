const mongoose = require('mongoose');

const productSchema = new mongoose.Schema({
  name: String,
  price: Number,
  description: String,
  inStock: Boolean
}, { timestamps: true });

module.exports = mongoose.model('Product', productSchema);
