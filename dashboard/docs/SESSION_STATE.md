# Streamlit `st.session_state` — Echolon dashboard

Single source of truth for navigation and user context. **Do not** duplicate business logic in random keys; extend this list when adding features.

| Key | Purpose |
|-----|--------|
| `current_page` | Sidebar title string for the active view (e.g. `"Executive Briefing"`). |
| `current_data` | Filtered `DataFrame` for the selected date range; pages should prefer this over raw upload. |
| `window_info` | Dict from `apply_time_filter` / KPIs (labels, day counts). |
| `uploaded_data` | Raw uploaded `DataFrame` or `None` (demo mode uses `load_data()` instead). |
| `uploaded_data_provided_columns` | List of canonical column names after mapping (for `_check_data_for_page`). |
| `connected_sources` | Truthy when live integrations exist (Stripe/Shopify/etc.). |
| `date_range` | Sidebar string: `"Last 7 Days"` … `"All Time"`. |
| `industry` | Key into `INDUSTRIES` (e.g. `ecommerce`). |
| `company_name` | Display name for exports and headings. |
| `goals` | Goal targets keyed by metric (shape used by Goals page). |
| `subscription_tier` | `"free"` \| `"starter"` \| `"growth"` (with Stripe, also check `stripe_subscription_status`). |
| `stripe_subscription_status` | e.g. `"active"` when checkout completed. |
| `onboarding_dismissed` | Hides the Get Started expander. |
| `_page_from_url_applied` | One-shot guard for `?page=` query hydration. |
| `_echolon_sync_toast` | Triggers post-sync toast on Dashboard. |
| `compact_nav` | If `True` (default), sidebar uses a short **selectbox**; if `False`, full grouped module list. |

**KPIs** are recomputed in `app.py` after data load (`compute_kpis(data, window_info)`) and are **not** stored in session state as a single key today — pages receive `kpis` via arguments from `app.py`.
