"""
Subscription tiers and Stripe billing for Echolon AI.

Tiers:
- free: 1 data source, 30 days history, Executive Briefing only
- starter: $49/mo — 1 source, 90 days, core briefing + dashboard
- growth: $99/mo — unlimited sources, 12 months, full features

Stripe Price IDs (set in secrets):
- STRIPE_PRICE_STARTER_MONTHLY
- STRIPE_PRICE_GROWTH_MONTHLY
- STRIPE_PRICE_STARTER_ANNUAL
- STRIPE_PRICE_GROWTH_ANNUAL
"""
import os
from typing import Optional

TIERS = {
    "free": {
        "name": "Free",
        "price": 0,
        "data_sources": 1,
        "history_days": 30,
        "features": ["Executive Briefing"],
        "pages_allowed": ["Executive Briefing", "Data Sources"],
    },
    "starter": {
        "name": "Starter",
        "price": 49,
        "price_annual": 39,
        "data_sources": 1,
        "history_days": 90,
        "features": ["Executive Briefing", "Dashboard", "Analytics", "Insights", "Goals"],
        "pages_allowed": ["Executive Briefing", "Dashboard", "Analytics", "Insights", "Goals", "Data Sources"],
    },
    "growth": {
        "name": "Growth",
        "price": 99,
        "price_annual": 79,
        "data_sources": 999,
        "history_days": 365,
        "features": ["All features", "Predictions", "What-If", "Recommendations", "Exports", "Unlimited sources"],
        "pages_allowed": None,  # None = all pages
    },
}

# Pages that require Growth tier
GROWTH_ONLY_PAGES = [
    "Predictions", "Recommendations", "What-If",
    "Customer Insights", "Inventory & Demand", "Anomalies & Alerts",
    "Inventory Optimization", "Margin Analysis", "Smart Alerts",
    "Cohort Analysis", "Customer LTV", "Revenue Attribution", "Competitive Benchmark",
]


def get_user_tier(username: str = None) -> str:
    """
    Get user's subscription tier. Checks session state first.
    Default: growth (full access) until Stripe is configured and enforced.
    """
    import streamlit as st
    if st.session_state.get("stripe_subscription_status") == "active":
        return st.session_state.get("subscription_tier", "growth")
    return st.session_state.get("subscription_tier", "growth")


def can_access_page(page_name: str, tier: str) -> bool:
    """Check if tier allows access to page."""
    if tier == "growth":
        return True
    if page_name == "Billing":
        return True  # Everyone can access Billing to upgrade
    config = TIERS.get(tier, TIERS["free"])
    allowed = config.get("pages_allowed")
    if allowed is None:
        return True
    return page_name in allowed


def can_add_data_source(current_count: int, tier: str) -> bool:
    """Check if user can add another data source."""
    config = TIERS.get(tier, TIERS["free"])
    return current_count < config["data_sources"]


def get_max_history_days(tier: str) -> int:
    """Max days of data history for tier."""
    return TIERS.get(tier, TIERS["free"])["history_days"]


def create_checkout_session(price_id: str, success_url: str, cancel_url: str, customer_email: str = None) -> Optional[str]:
    """
    Create Stripe Checkout session. Returns session URL or None.
    Requires STRIPE_SECRET_KEY in secrets.
    """
    try:
        import stripe
        import streamlit as st
        sk = os.environ.get("STRIPE_SECRET_KEY")
        if not sk:
            try:
                sk = st.secrets.get("stripe", {}).get("secret_key") or st.secrets.get("STRIPE_SECRET_KEY")
            except Exception:
                pass
        if not sk:
            return None
        stripe.api_key = sk
        session = stripe.checkout.Session.create(
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=cancel_url,
            customer_email=customer_email,
        )
        return session.url
    except Exception:
        return None


def create_billing_portal_session(customer_id: str, return_url: str) -> Optional[str]:
    """
    Create Stripe Customer Portal session. Returns portal URL or None.
    Lets customers manage payment method, cancel, view invoices.
    """
    try:
        import stripe
        import streamlit as st
        sk = os.environ.get("STRIPE_SECRET_KEY")
        if not sk:
            sk = st.secrets.get("stripe", {}).get("secret_key") or st.secrets.get("STRIPE_SECRET_KEY")
        if not sk or not customer_id:
            return None
        stripe.api_key = sk
        session = stripe.billing_portal.Session.create(
            customer=customer_id,
            return_url=return_url,
        )
        return session.url
    except Exception:
        return None


def get_subscription_from_session(session_id: str) -> Optional[dict]:
    """
    Retrieve checkout session and return subscription info.
    Returns {tier, status, customer_id} or None.
    """
    try:
        import stripe
        import streamlit as st
        sk = os.environ.get("STRIPE_SECRET_KEY")
        if not sk:
            sk = st.secrets.get("stripe", {}).get("secret_key") or st.secrets.get("STRIPE_SECRET_KEY")
        if not sk:
            return None
        stripe.api_key = sk
        session = stripe.checkout.Session.retrieve(session_id, expand=["subscription"])
        if session.mode != "subscription" or not session.subscription:
            return None
        sub = session.subscription
        items = sub.get("items", {}) if hasattr(sub, "get") else getattr(sub, "items", None)
        data_list = items.get("data", []) if items and hasattr(items, "get") else (getattr(items, "data", []) if items else [])
        first_item = data_list[0] if data_list else {}
        price = first_item.get("price", {}) if hasattr(first_item, "get") else getattr(first_item, "price", None)
        price_id = getattr(price, "id", None) or (price.get("id", "") if price and hasattr(price, "get") else "")
        try:
            import streamlit as st
            growth_monthly = str(st.secrets.get("STRIPE_PRICE_GROWTH_MONTHLY", ""))
            growth_annual = str(st.secrets.get("STRIPE_PRICE_GROWTH_ANNUAL", ""))
            starter_monthly = str(st.secrets.get("STRIPE_PRICE_STARTER_MONTHLY", ""))
            starter_annual = str(st.secrets.get("STRIPE_PRICE_STARTER_ANNUAL", ""))
            pid = str(price_id)
            if pid in (growth_monthly, growth_annual):
                tier = "growth"
            elif pid in (starter_monthly, starter_annual):
                tier = "starter"
            else:
                tier = "growth"
        except Exception:
            tier = "growth"
        sub_id = sub.get("id") if hasattr(sub, "get") else getattr(sub, "id", None)
        cust_id = session.get("customer") if hasattr(session, "get") else getattr(session, "customer", None)
        return {
            "tier": tier,
            "status": sub.get("status", "active") if hasattr(sub, "get") else getattr(sub, "status", "active"),
            "customer_id": cust_id,
            "subscription_id": sub_id,
        }
    except Exception:
        return None
