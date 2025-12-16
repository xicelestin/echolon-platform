# CRITICAL FIX: Page Routing Issue in app.py

## Problem Identified
The Insights, Predictions, and Recommendations navigation pages are ALL showing Profile page content (subscription plans, team members, notifications) instead of their intended functionality.

## Root Cause
In `dashboard/app.py` around line 518-520, there is a disabled Profile page section:
```python
# PAGE: PROFILE  
# PROFILE PAGE DISABLED -- TODO: Fix indentation issues
if False:  # Disabled temporarily
    render_page_header("Business Profile", "Your company metrics and account settings")
```

The problem is:
1. There is NO `elif page == "Profile":` handler in the code
2. All the Profile page content (lines ~522-650) that follows is NOT properly wrapped in a page conditional
3. This "orphaned" Profile content (subscription, team, notifications) executes for EVERY page
4. Since it comes after Insights/Predictions/Recommendations in the code, it overrides their content

## The Fix

### Step 1: Add Profile Page Handler
Find line 518 in app.py and REPLACE:
```python
# PAGE: PROFILE
# PROFILE PAGE DISABLED -- TODO: Fix indentation issues  
if False:  # Disabled temporarily
    render_page_header("Business Profile", "Your company metrics and account settings")
# Company Information Section
st.subheader("🏢 Company Information")
```

WITH:
```python
# PAGE: PROFILE
elif page == "Profile":
    render_page_header("Business Profile", "Your company metrics and account settings")
    render_last_updated()
    st.markdown(get_data_source_badge(), unsafe_allow_html=True)
    st.markdown("---")
    
    # Company Information Section
    st.subheader("🏢 Company Information")
```

### Step 2: Ensure All Profile Content is Indented
Make sure ALL content from line ~522 to line ~650 (Company Info, Goal Tracking, Integrations, Notifications, Subscription, Team Members) is properly indented under the `elif page == "Profile":` block.

All this content should have 4-space indentation.

### Step 3: Verify Page Order
The page routing should be in this order:
1. Home (line ~280)
2. Insights (line ~385) ✅ Already correct
3. Predictions (line ~412) ✅ Already correct  
4. Inventory (line ~440) ✅ Already correct
5. What-If (line ~460) ✅ Already correct
6. **Profile (line ~518) ❌ NEEDS FIX**
7. Recommendations (line ~650) ✅ Already correct
8. Upload (line ~700) ✅ Already correct

## Testing After Fix
1. Navigate to Insights page → Should show business insights/KPIs
2. Navigate to Predictions page → Should show forecast models
3. Navigate to Recommendations page → Should show AI recommendations  
4. Navigate to Profile page → Should show subscription/team/settings

Each page should display its UNIQUE content, not profile information.

## Priority
🔴 **CRITICAL** - This breaks core navigation and makes 3+ pages unusable.

## Files to Modify
- `dashboard/app.py` (lines 518-650)
