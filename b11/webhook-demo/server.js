// server.js
const express = require("express");
const app = express();
app.use(express.json());

// Giả lập database lưu thông báo
const notifications = [];

// Endpoint Webhook để các hệ thống (Stripe/GitHub) gửi sự kiện
app.post("/webhook/payment", (req, res) => {
    const event = req.body;

    console.log("=== Webhook Received ===");
    console.log("Event type:", event.type);
    console.log("Event data:", event.data);

    // Xử lý sự kiện
    handleEvent(event);

    // Báo cho sender biết server đã nhận
    res.status(200).send("Webhook received");
});

// Hàm xử lý sự kiện Webhook
function handleEvent(event) {
    if (event.type === "payment.succeeded") {
        notifications.push({
            userId: event.data.userId,
            message: `Thanh toán #${event.data.paymentId} thành công`,
            time: new Date()
        });
        console.log("-> Thông báo đã được tạo (Thanh toán thành công)");
    }

    if (event.type === "payment.failed") {
        notifications.push({
            userId: event.data.userId,
            message: `Thanh toán #${event.data.paymentId} thất bại`,
            time: new Date()
        });
        console.log("-> Thông báo đã được tạo (Thanh toán thất bại)");
    }

    console.log("=== Current Notifications DB ===");
    console.log(notifications);
}

// Start server
app.listen(3000, () => {
    console.log("Webhook server đang chạy tại http://localhost:3000");
});
