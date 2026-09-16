import os
import razorpay

from models.user_model import User

RAZORPAY_KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "rzp_test_key")
RAZORPAY_KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "rzp_test_secret")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))


def create_payment_order(amount, currency="INR"):
    order_data = {
        "amount": int(amount * 100),
        "currency": currency,
        "payment_capture": 1,
    }
    return client.order.create(data=order_data)


def premium_membership_service(user_id, data):
    amount = data.get("amount", 499)
    currency = data.get("currency", "INR")
    order = create_payment_order(amount, currency)
    return {
        "order_id": order.get("id"),
        "amount": order.get("amount"),
        "currency": order.get("currency"),
    }, 200
