"""
Stripe webhook handler for subscription lifecycle events.

Deploy backend and add webhook URL in Stripe Dashboard:
https://your-backend-url/api/v1/stripe/webhook

Events: customer.subscription.updated, customer.subscription.deleted, invoice.payment_failed

Requires: STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET (from Stripe webhook signing secret)
"""
import os
from fastapi import APIRouter, Request, HTTPException, Response

router = APIRouter()


@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events. Verifies signature and processes subscription events."""
    stripe_secret = os.getenv("STRIPE_SECRET_KEY")
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not stripe_secret or not webhook_secret:
        raise HTTPException(status_code=500, detail="Stripe webhook not configured")

    import stripe
    stripe.api_key = stripe_secret
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid payload: {e}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook signature verification failed: {e}")

    # Handle subscription events
    if event["type"] == "customer.subscription.updated":
        sub = event["data"]["object"]
        # TODO: Persist subscription status (e.g. to Supabase/DB) by customer_email or metadata
        # For now, dashboard relies on session state when user returns from checkout
        pass
    elif event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        # TODO: Downgrade user to free tier
        pass
    elif event["type"] == "invoice.payment_failed":
        inv = event["data"]["object"]
        # TODO: Notify user, retry logic, etc.
        pass

    return Response(status_code=200)
