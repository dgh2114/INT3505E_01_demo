// sendWebhook.js
const fetch = (...args) => import('node-fetch').then(({default: fetch}) => fetch(...args));

async function sendEvent(event) {
    console.log("Gửi webhook...");
    const res = await fetch("http://localhost:3000/webhook/payment", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(event)
    });

    console.log("Response:", await res.text());
}

// TEST 1: Thanh toán thành công
sendEvent({
    type: "payment.succeeded",
    data: {
        userId: 101,
        paymentId: "PMT_555"
    }
});

// TEST 2: Thanh toán thất bại
setTimeout(() => {
    sendEvent({
        type: "payment.failed",
        data: {
            userId: 202,
            paymentId: "PMT_777"
        }
    });
}, 1500);
