"""Billing and subscription management page."""
import streamlit as st
from auth import get_current_user
from utils.subscription import TIERS, get_user_tier, create_checkout_session


def render_billing_page():
    """Render billing/subscription page with upgrade options."""
    st.title("💳 Billing & Subscription")
    st.caption("Manage your plan and billing")
    
    tier = get_user_tier()
    config = TIERS.get(tier, TIERS["free"])
    
    st.markdown(f"**Current plan:** {config['name']}")
    if tier == "free":
        st.info("Upgrade to unlock Dashboard, Analytics, Insights, and more.")
    elif tier == "starter":
        st.success("You have access to core features. Upgrade to Growth for Predictions, What-If, and unlimited data sources.")
    else:
        st.success("You have full access to all features.")
    
    st.markdown("---")
    st.subheader("Plans")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        with st.container(border=True):
            st.markdown("**Free** — $0")
            st.caption("Executive Briefing, 1 source, 30 days")
            if tier != "free":
                st.button("Downgrade", key="downgrade_free", disabled=True, help="Contact support")
    
    with col2:
        with st.container(border=True):
            st.markdown("**Starter** — $49/mo")
            st.caption("Dashboard, Analytics, Insights, 90 days")
            if tier == "free":
                if st.button("Subscribe", key="sub_starter"):
                    _redirect_to_checkout("starter")
            elif tier == "starter":
                st.success("Current plan")
    
    with col3:
        with st.container(border=True):
            st.markdown("**Growth** — $99/mo")
            st.caption("All features, unlimited sources, 12 months")
            if tier != "growth":
                if st.button("Upgrade", key="sub_growth", type="primary"):
                    _redirect_to_checkout("growth")
            else:
                st.success("Current plan")
    
    st.markdown("---")
    st.caption("14-day free trial on paid plans. Cancel anytime. Annual billing saves 20%.")


def _redirect_to_checkout(plan: str):
    """Create Stripe Checkout session and redirect."""
    try:
        import streamlit as st
        from auth import _get_query_param
        # Get base URL for redirect (Streamlit Cloud or local)
        import os
        base_url = os.environ.get("STREAMLIT_SERVER_BASE_URL", "http://localhost:8501")
        if "localhost" not in base_url and base_url.startswith("http://"):
            base_url = base_url.replace("http://", "https://", 1)
        # Preserve auth session in success URL
        session_token = _get_query_param("session")
        sess_param = f"&session={session_token}" if session_token else ""
        
        # Price IDs from secrets
        price_ids = {
            "starter": st.secrets.get("STRIPE_PRICE_STARTER_MONTHLY", ""),
            "growth": st.secrets.get("STRIPE_PRICE_GROWTH_MONTHLY", ""),
        }
        price_id = price_ids.get(plan)
        if not price_id:
            st.warning("Billing not configured yet. Add STRIPE_PRICE_STARTER_MONTHLY and STRIPE_PRICE_GROWTH_MONTHLY to secrets.")
            return
        
        url = create_checkout_session(
            price_id=price_id,
            success_url=f"{base_url}/?session_id={{CHECKOUT_SESSION_ID}}{sess_param}",
            cancel_url=f"{base_url}{'?session=' + session_token if session_token else ''}",
            customer_email=st.session_state.get("user_email"),
        )
        if url:
            st.success("Complete your payment on Stripe:")
            st.link_button("→ Go to Stripe Checkout", url, type="primary")
        else:
            st.error("Could not create checkout. Check STRIPE_SECRET_KEY in secrets.")
    except Exception as e:
        st.error(f"Billing setup required. Add Stripe keys to secrets. ({str(e)[:80]})")
