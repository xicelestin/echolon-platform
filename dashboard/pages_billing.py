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
            st.markdown("**Starter** — $49/mo · $39/mo annual")
            st.caption("Dashboard, Analytics, Insights, 90 days")
            if tier == "free":
                sub_col1, sub_col2 = st.columns(2)
                with sub_col1:
                    if st.button("Monthly", key="sub_starter_monthly"):
                        _redirect_to_checkout("starter", annual=False)
                with sub_col2:
                    if st.button("Annual", key="sub_starter_annual"):
                        _redirect_to_checkout("starter", annual=True)
            elif tier == "starter":
                st.success("Current plan")
    
    with col3:
        with st.container(border=True):
            st.markdown("**Growth** — $99/mo · $79/mo annual")
            st.caption("All features, unlimited sources, 12 months")
            if tier != "growth":
                sub_col1, sub_col2 = st.columns(2)
                with sub_col1:
                    if st.button("Monthly", key="sub_growth_monthly", type="primary"):
                        _redirect_to_checkout("growth", annual=False)
                with sub_col2:
                    if st.button("Annual", key="sub_growth_annual", type="primary"):
                        _redirect_to_checkout("growth", annual=True)
            else:
                st.success("Current plan")
    
    st.markdown("---")
    st.caption("14-day free trial on paid plans. Cancel anytime. Annual billing saves 20%.")


def _redirect_to_checkout(plan: str, annual: bool = False):
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
        if annual:
            price_ids = {
                "starter": st.secrets.get("STRIPE_PRICE_STARTER_ANNUAL", ""),
                "growth": st.secrets.get("STRIPE_PRICE_GROWTH_ANNUAL", ""),
            }
        else:
            price_ids = {
                "starter": st.secrets.get("STRIPE_PRICE_STARTER_MONTHLY", ""),
                "growth": st.secrets.get("STRIPE_PRICE_GROWTH_MONTHLY", ""),
            }
        price_id = price_ids.get(plan)
        if not price_id:
            st.warning("Billing not configured yet. Add STRIPE_PRICE_* keys to secrets.")
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
