"""
Export cleaned/standardized dataset for users.
Output: parsed dates, normalized column names, derived columns (roas, gross_profit),
metadata in JSON sidecar or header comment.
"""
import pandas as pd
import json
import io
from datetime import datetime, timezone
from typing import Dict, Any, Optional, Tuple


def build_cleaned_dataframe(df: pd.DataFrame, column_mapping: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Build standardized dataframe: parsed dates, normalized names, derived columns.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    out = df.copy()

    # Parse dates
    if 'date' in out.columns:
        out['date'] = pd.to_datetime(out['date'], errors='coerce')
        out = out.dropna(subset=['date'])
        out['date'] = out['date'].dt.strftime('%Y-%m-%d')

    # Normalize column names (use mapping if provided)
    if column_mapping:
        for canonical, actual in column_mapping.items():
            if actual in out.columns and actual != canonical:
                out[canonical] = out[actual]
                out = out.drop(columns=[actual], errors='ignore')

    # Derived: gross_profit = revenue - cost
    if 'revenue' in out.columns and 'cost' in out.columns:
        out['gross_profit'] = (out['revenue'] - out['cost']).round(2)
    elif 'revenue' in out.columns and 'profit' in out.columns:
        out['gross_profit'] = out['profit'].round(2)

    # Derived: roas = revenue / marketing_spend (row-level, fill with period avg)
    mkt_col = 'marketing_spend' if 'marketing_spend' in out.columns else 'ad_spend' if 'ad_spend' in out.columns else None
    if mkt_col and 'revenue' in out.columns:
        mkt = out[mkt_col].replace(0, float('nan'))
        out['roas'] = (out['revenue'] / mkt).round(2)
        period_roas = out['revenue'].sum() / out[mkt_col].sum() if out[mkt_col].sum() > 0 else None
        if period_roas is not None:
            out['roas'] = out['roas'].fillna(round(period_roas, 2))

    return out


def get_cleaned_csv_and_metadata(
    df: pd.DataFrame,
    column_mapping: Optional[Dict[str, str]] = None,
    window_info: Optional[Dict] = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    Return (csv_string, metadata_dict).
    CSV has optional comment line: # echolon_cleaned|...
    """
    cleaned = build_cleaned_dataframe(df, column_mapping)
    if cleaned.empty:
        return "", {}

    metadata = {
        "echolon_cleaned": True,
        "version": 1,
        "exported_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "row_count": len(cleaned),
        "columns": list(cleaned.columns),
        "aggregation": "SUM over rows in window",
    }
    if window_info:
        metadata["window"] = window_info.get("label", "")

    buf = io.StringIO()
    # Comment line for metadata (many tools skip # lines)
    buf.write("# echolon_cleaned|" + json.dumps(metadata).replace("\n", " ") + "\n")
    cleaned.to_csv(buf, index=False, date_format="%Y-%m-%d")
    return buf.getvalue(), metadata


def create_download_cleaned_csv_button(
    df: pd.DataFrame,
    column_mapping: Optional[Dict[str, str]] = None,
    window_info: Optional[Dict] = None,
    key: str = "download_cleaned_csv",
) -> None:
    """Streamlit download button for cleaned CSV."""
    import streamlit as st

    if df is None or df.empty:
        st.caption("No data to export.")
        return

    csv_str, meta = get_cleaned_csv_and_metadata(df, column_mapping, window_info)
    fname = f"echolon_cleaned_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    st.download_button(
        label="📥 Download cleaned CSV",
        data=csv_str,
        file_name=fname,
        mime="text/csv",
        key=key,
        use_container_width=True,
    )
    st.caption("Parsed dates, normalized columns, derived: roas, gross_profit. Metadata in header.")
