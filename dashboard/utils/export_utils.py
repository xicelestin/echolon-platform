"""export_utils.pyData Export Utilities for Echolon Dashboard

Provides functions for exporting data in various formats (CSV, Excel, JSON)
with download buttons ready for Streamlit integration.
"""

import pandas as pd
import streamlit as st
import io
from datetime import datetime
from typing import Optional, Dict, Any
import json


def to_csv(df: pd.DataFrame) -> str:
    """Convert DataFrame to CSV string."""
    return df.to_csv(index=False).encode('utf-8')


def to_excel(df: pd.DataFrame, sheet_name: str = 'Data') -> bytes:
    """Convert DataFrame to Excel bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()


def to_json(df: pd.DataFrame, orient: str = 'records') -> str:
    """Convert DataFrame to JSON string."""
    return df.to_json(orient=orient, date_format='iso').encode('utf-8')


def create_download_button(df: pd.DataFrame, 
                          file_format: str = 'csv',
                          filename_prefix: str = 'echolon_export',
                          button_label: Optional[str] = None,
                          key: Optional[str] = None) -> None:
    """
    Create a Streamlit download button for DataFrame export.
    
    Args:
        df: DataFrame to export
        file_format: 'csv', 'excel', or 'json'
        filename_prefix: Prefix for the downloaded file
        button_label: Custom label for the button
        key: Unique key for the button
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if file_format == 'csv':
        data = to_csv(df)
        filename = f"{filename_prefix}_{timestamp}.csv"
        mime = 'text/csv'
        label = button_label or f"📥 Download CSV ({len(df)} rows)"
    
    elif file_format == 'excel':
        data = to_excel(df)
        filename = f"{filename_prefix}_{timestamp}.xlsx"
        mime = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        label = button_label or f"📥 Download Excel ({len(df)} rows)"
    
    elif file_format == 'json':
        data = to_json(df)
        filename = f"{filename_prefix}_{timestamp}.json"
        mime = 'application/json'
        label = button_label or f"📥 Download JSON ({len(df)} rows)"
    
    else:
        raise ValueError(f"Unsupported format: {file_format}")
    
    st.download_button(
        label=label,
        data=data,
        file_name=filename,
        mime=mime,
        key=key,
        use_container_width=True
    )


def create_multi_format_export(df: pd.DataFrame,
                               filename_prefix: str = 'echolon_data',
                               formats: list = ['csv', 'excel', 'json']) -> None:
    """
    Create multiple download buttons for different formats.
    
    Args:
        df: DataFrame to export
        filename_prefix: Prefix for downloaded files
        formats: List of formats to offer
    """
    st.markdown("### 📥 Export Data")
    
    cols = st.columns(len(formats))
    for idx, fmt in enumerate(formats):
        with cols[idx]:
            create_download_button(
                df=df,
                file_format=fmt,
                filename_prefix=filename_prefix,
                key=f"export_{fmt}_{filename_prefix}"
            )


def export_with_metadata(df: pd.DataFrame,
                        metadata: Dict[str, Any],
                        format: str = 'json') -> bytes:
    """
    Export data with additional metadata.
    
    Args:
        df: DataFrame to export
        metadata: Dictionary with metadata (e.g., export_date, filters, kpis)
        format: Export format
    
    Returns:
        Bytes ready for download
    """
    export_data = {
        'metadata': metadata,
        'data': json.loads(df.to_json(orient='records', date_format='iso'))
    }
    
    return json.dumps(export_data, indent=2).encode('utf-8')


def create_filtered_export_section(df: pd.DataFrame,
                                   filters_applied: Dict[str, Any],
                                   section_name: str = "Filtered Data") -> None:
    """
    Create an export section showing what filters were applied.
    
    Args:
        df: Filtered DataFrame
        filters_applied: Dictionary of applied filters
        section_name: Name for the export section
    """
    with st.expander(f"📊 Export {section_name}", expanded=False):
        # Show applied filters
        if filters_applied:
            st.markdown("**Applied Filters:**")
            for filter_name, filter_value in filters_applied.items():
                st.text(f"• {filter_name}: {filter_value}")
            st.markdown("---")
        
        # Show data preview
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Showing 10 of {len(df)} rows")
        
        # Export buttons
        st.markdown("**Download Options:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            create_download_button(df, 'csv', f"{section_name.lower().replace(' ', '_')}")
        with col2:
            create_download_button(df, 'excel', f"{section_name.lower().replace(' ', '_')}")
        with col3:
            # Export with metadata
            metadata = {
                'export_date': datetime.now().isoformat(),
                'section': section_name,
                'filters': filters_applied,
                'row_count': len(df)
            }
            data = export_with_metadata(df, metadata)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            st.download_button(
                label="📥 JSON+Metadata",
                data=data,
                file_name=f"{section_name.lower().replace(' ', '_')}_with_metadata_{timestamp}.json",
                mime='application/json',
                use_container_width=True
            )


# Example usage
if __name__ == '__main__':
    # Test with sample data
    sample_df = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=100),
        'revenue': [1000 + i * 10 for i in range(100)],
        'orders': [50 + i for i in range(100)]
    })
    
    print("Export utilities loaded successfully!")
    print(f"Sample data shape: {sample_df.shape}")
