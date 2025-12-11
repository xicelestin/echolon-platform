"""Enhanced Upload Page with Multi-Source Data Integration"""
import streamlit as st
import pandas as pd
from datetime import datetime
import time
from data_connector import get_connector

def render_enhanced_upload():
    """Render enhanced upload page with multiple data sources."""
    
    st.markdown("<div class='page-header'><h1>📊 Import Your Data</h1><p>Connect multiple data sources for comprehensive business analytics</p></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Data source selection tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📁 CSV Upload", "🛒 Shopify", "📊 Google Sheets", "💼 QuickBooks (Coming Soon)"])
    
    connector = get_connector()
    
    # TAB 1: CSV UPLOAD
    with tab1:
        st.subheader("Upload CSV File")
        st.info("📋 **Required columns**: Your CSV should include `date` and `value` columns for analysis.")

                # Sample CSV Download Section
        with st.expander("📥 Don't have a CSV? Download our sample template", expanded=False):
            st.markdown("""
            **What you'll get:**
            - Example data format showing required columns
            - Sample transaction data to test the platform
            - Clear column headers (date, value, customer_id)
            """)
            
            # Create sample data
            sample_data = pd.DataFrame({
                'date': ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05',
                        '2024-01-06', '2024-01-07', '2024-01-08', '2024-01-09', '2024-01-10'],
                'value': [1500, 2000, 1750, 2200, 1900, 2100, 1800, 2300, 1950, 2150],
                'customer_id': ['C001', 'C002', 'C003', 'C004', 'C005', 'C006', 'C007', 'C008', 'C009', 'C010']
            })
            
            # Show preview
            st.markdown("**Preview:**")
            st.dataframe(sample_data.head(), use_container_width=True)
            
            # Download button
            csv = sample_data.to_csv(index=False)
            st.download_button(
                label="⬇️ Download Sample CSV",
                data=csv,
                file_name="echolon_sample_data.csv",
                mime="text/csv",
                type="primary"
            )
            
            st.info("💡 **Tip:** Replace the sample data with your own business transactions to get personalized insights!")

        
        uploaded_file = st.file_uploader(
            "Choose a CSV file",
            type="csv",
            help="Upload your business data to replace the demo dataset"
        )
        
        if uploaded_file:
            try:
                # Progress bar for upload
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("⏳ Reading file...")
                progress_bar.progress(25)
                time.sleep(0.3)
                
                df = pd.read_csv(uploaded_file)
                
                status_text.text("⏳ Validating data...")
                progress_bar.progress(50)
                time.sleep(0.3)
                
                if 'date' not in df.columns or 'value' not in df.columns:
                    progress_bar.progress(100)
                    status_text.empty()
                    st.error("⚠ Missing required columns. Your CSV must include 'date' and 'value' columns.")
                else:
                    status_text.text("⏳ Processing...")
                    progress_bar.progress(75)
                    time.sleep(0.3)
                    
                    # Store in session state
                    st.session_state.uploaded_data = df
                    st.session_state.data_source = 'csv_upload'
                    st.session_state.last_updated = datetime.now()
                    
                    progress_bar.progress(100)
                    status_text.empty()
                    
                    st.success(f"✅ Data loaded successfully! Analyzing {df.shape[0]:,} rows and {df.shape[1]} columns.")
                                        st.info("🔄 **All insights updated!** Check the **Insights** and **Predictions** pages to see your personalized analysis.")
                    
                    # Data source badge
                    st.markdown(f"<div style='background: rgba(0,200,0,0.1); border: 1px solid #00c800; border-radius: 8px; padding: 12px; margin: 16px 0;'>"
                              f"<b>✓ Connected:</b> CSV File | <b>Rows:</b> {df.shape[0]:,} | <b>Columns:</b> {df.shape[1]}</div>", 
                              unsafe_allow_html=True)
                    
                    # Data preview
                    st.subheader("Data Preview")
                    st.caption("First 10 rows of your uploaded dataset")
                    st.dataframe(df.head(10), use_container_width=True)
                    
                    # Data quality metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        missing = df.isnull().sum().sum()
                        st.metric("Missing Values", missing)
                    with col2:
                        duplicates = df.duplicated().sum()
                        st.metric("Duplicate Rows", duplicates)
                    with col3:
                        date_col = df['date'] if 'date' in df.columns else None
                        if date_col is not None:
                            date_range = f"{len(pd.to_datetime(date_col, errors='coerce').dropna())} dates"
                        else:
                            date_range = "N/A"
                        st.metric("Date Range", date_range)
                    with col4:
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        st.metric("Numeric Columns", len(numeric_cols))
                        
            except Exception as e:
                st.error(f"⚠ We couldn't process your file. Error: {str(e)}")
    
    # TAB 2: SHOPIFY INTEGRATION
    with tab2:
        st.subheader("Connect to Shopify")
        st.info("🛒 Connect your Shopify store to import orders, products, and customer data automatically.")
        
        with st.form("shopify_form"):
            shop_url = st.text_input(
                "Shop URL",
                placeholder="your-store.myshopify.com",
                help="Enter your Shopify store URL"
            )
            access_token = st.text_input(
                "Access Token",
                type="password",
                help="Generate an API token from your Shopify admin panel"
            )
            
            submitted = st.form_submit_button("🔗 Connect to Shopify", type="primary", use_container_width=True)
            
            if submitted:
                if not shop_url or not access_token:
                    st.error("⚠ Please provide both Shop URL and Access Token.")
                else:
                    with st.spinner("🔄 Connecting to Shopify..."):
                        result = connector.connect_shopify(shop_url, access_token)
                        
                        if result.get('status') == 'success':
                            st.session_state.uploaded_data = result['data']
                            st.session_state.data_source = 'shopify'
                            st.session_state.last_updated = datetime.now()
                            
                            st.success(f"✅ Connected successfully! Imported {result['total_orders']} orders.")
                            
                            st.markdown(f"<div style='background: rgba(95,39,205,0.1); border: 1px solid #5f27cd; border-radius: 8px; padding: 12px; margin: 16px 0;'>"
                                      f"<b>✓ Connected:</b> Shopify | <b>Store:</b> {shop_url} | <b>Orders:</b> {result['total_orders']:,}</div>", 
                                      unsafe_allow_html=True)
                            
                            st.dataframe(result['data'].head(10), use_container_width=True)
                        else:
                            st.error(f"⚠ Connection failed: {result.get('message')}")
        
        st.markdown("---")
        st.markdown("""### How to get your Shopify API credentials:
        1. Go to your Shopify Admin panel
        2. Navigate to **Settings** → **Apps and sales channels**
        3. Click **Develop apps** → **Create an app**
        4. Grant permissions for **Orders**, **Products**, and **Customers**
        5. Copy your **Access Token** and paste it above
        """)
    
    # TAB 3: GOOGLE SHEETS INTEGRATION
    with tab3:
        st.subheader("Connect to Google Sheets")
        st.info("📊 Import data directly from your Google Sheets spreadsheet.")
        
        with st.form("sheets_form"):
            spreadsheet_id = st.text_input(
                "Spreadsheet ID",
                placeholder="1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
                help="Find this in your sheet URL: docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit"
            )
            
            credentials_json = st.text_area(
                "Service Account JSON",
                placeholder="Paste your Google Service Account credentials here...",
                height=150,
                help="Download from Google Cloud Console → APIs & Services → Credentials"
            )
            
            submitted_sheets = st.form_submit_button("🔗 Connect to Google Sheets", type="primary", use_container_width=True)
            
            if submitted_sheets:
                if not spreadsheet_id or not credentials_json:
                    st.error("⚠ Please provide both Spreadsheet ID and credentials JSON.")
                else:
                    with st.spinner("🔄 Connecting to Google Sheets..."):
                        result = connector.connect_google_sheets(spreadsheet_id, credentials_json)
                        
                        if result.get('status') == 'success':
                            st.session_state.uploaded_data = result['data']
                            st.session_state.data_source = 'google_sheets'
                            st.session_state.last_updated = datetime.now()
                            
                            st.success(f"✅ Connected successfully! Imported {result['rows']} rows.")
                            
                            st.markdown(f"<div style='background: rgba(16,172,132,0.1); border: 1px solid #10ac84; border-radius: 8px; padding: 12px; margin: 16px 0;'>"
                                      f"<b>✓ Connected:</b> Google Sheets | <b>Rows:</b> {result['rows']:,} | <b>Columns:</b> {len(result['columns'])}</div>", 
                                      unsafe_allow_html=True)
                            
                            st.dataframe(result['data'].head(10), use_container_width=True)
                        else:
                            st.error(f"⚠ Connection failed: {result.get('message')}")
        
        st.markdown("---")
        st.markdown("""### How to set up Google Sheets API:
        1. Go to [Google Cloud Console](https://console.cloud.google.com/)
        2. Create a new project (or select existing)
        3. Enable **Google Sheets API** and **Google Drive API**
        4. Create **Service Account** credentials
        5. Download the JSON key file and paste its contents above
        6. Share your spreadsheet with the service account email
        """)
    
    # TAB 4: QUICKBOOKS (COMING SOON)
    with tab4:
        st.subheader("QuickBooks Integration")
        st.info("💼 QuickBooks integration is coming soon! Connect your accounting data for complete financial analytics.")
        
        st.markdown("""### Planned Features:
        - Import invoices and payments automatically
        - Sync expense categories and vendor data
        - Real-time P&L and balance sheet updates
        - Tax-ready reporting integration
        
        **Want early access?** [Contact our team](mailto:support@echolonai.com) to join the beta program.
        """)
        
        if st.button("🔔 Notify me when available", use_container_width=True):
            st.success("✅ We'll notify you when QuickBooks integration launches!")

if __name__ == "__main__":
    render_enhanced_upload()
