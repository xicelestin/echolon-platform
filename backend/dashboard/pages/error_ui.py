"""Error UI components and utilities for Streamlit error handling.

Provides reusable error display components, retry mechanisms,
and error recovery flows for a better user experience.
"""

import streamlit as st
from typing import Optional, Callable, Any
import time
from datetime import datetime
import json


def display_error(
    error_message: str,
    error_code: Optional[str] = None,
    error_detail: Optional[str] = None,
    request_id: Optional[str] = None,
    show_details: bool = True,
) -> None:
    """Display a formatted error message with details.
    
    Args:
        error_message: Main error message
        error_code: Error code (e.g., 'DATASOURCE_ERROR')
        error_detail: Detailed error explanation
        request_id: Request ID for support reference
        show_details: Whether to show expandable details
    """
    with st.container():
        st.markdown("""
        <style>
            .error-container {
                padding: 15px;
                border-radius: 8px;
                border-left: 5px solid #FF6B6B;
                background-color: #FFE8E8;
                margin: 10px 0;
            }
            .error-header {
                color: #CC0000;
                font-weight: bold;
                font-size: 16px;
                margin-bottom: 8px;
            }
            .error-code {
                color: #666;
                font-size: 12px;
                font-family: monospace;
            }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([5, 1])
        
        with col1:
            st.markdown(f'<div class="error-container">', unsafe_allow_html=True)
            st.markdown(f'<div class="error-header">❌ {error_message}</div>', unsafe_allow_html=True)
            
            if error_code:
                st.markdown(f'<div class="error-code">Code: {error_code}</div>', unsafe_allow_html=True)
            
            if error_detail and show_details:
                with st.expander("📋 Error Details"):
                    st.write(error_detail)
            
            if request_id:
                st.markdown(
                    f"<small style='color:#666'>Request ID: `{request_id}` (Share this with support)</small>",
                    unsafe_allow_html=True
                )
            
            st.markdown('</div>', unsafe_allow_html=True)


def display_warning(
    warning_message: str,
    warning_code: Optional[str] = None,
) -> None:
    """Display a formatted warning message.
    
    Args:
        warning_message: Main warning message
        warning_code: Warning code (e.g., 'SLOW_QUERY')
    """
    with st.container():
        col1, col2 = st.columns([5, 1])
        with col1:
            st.warning(f"⚠️ {warning_message}")
            if warning_code:
                st.caption(f"Code: {warning_code}")


def display_success(success_message: str) -> None:
    """Display a success message.
    
    Args:
        success_message: Success message text
    """
    st.success(f"✅ {success_message}")


def retry_with_backoff(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    show_progress: bool = True,
) -> Any:
    """Execute function with exponential backoff retry.
    
    Args:
        func: Function to execute
        max_attempts: Maximum retry attempts
        base_delay: Initial delay in seconds
        show_progress: Show retry progress to user
        
    Returns:
        Function result or None if all retries fail
    """
    attempt = 0
    last_error = None
    
    while attempt < max_attempts:
        try:
            return func()
        except Exception as e:
            attempt += 1
            last_error = e
            
            if attempt < max_attempts:
                delay = base_delay * (2 ** (attempt - 1))
                
                if show_progress:
                    st.warning(
                        f"⏳ Attempt {attempt}/{max_attempts} failed. "
                        f"Retrying in {delay:.1f}s..."
                    )
                
                time.sleep(delay)
            else:
                if show_progress:
                    st.error(
                        f"❌ Failed after {max_attempts} attempts. "
                        f"Error: {str(last_error)}"
                    )
                return None
    
    return None


def retry_button(
    label: str = "🔄 Retry",
    on_retry: Optional[Callable] = None,
    key: Optional[str] = None,
) -> bool:
    """Display a retry button with state management.
    
    Args:
        label: Button label text
        on_retry: Callback function when retry is clicked
        key: Streamlit key for button
        
    Returns:
        True if retried, False otherwise
    """
    col1, col2, col3 = st.columns([1, 1, 3])
    
    with col1:
        if st.button(label, key=key, use_container_width=True):
            if on_retry:
                try:
                    on_retry()
                    display_success("Retry successful!")
                    st.rerun()
                except Exception as e:
                    display_error(f"Retry failed: {str(e)}")
            return True
    
    return False


def error_recovery_form(
    error_code: str,
    request_id: str,
) -> None:
    """Display error recovery form with support options.
    
    Args:
        error_code: Error code that occurred
        request_id: Request ID for reference
    """
    st.subheader("❓ Need Help?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📧 Contact Support", use_container_width=True):
            st.info(
                f"Send this information to support@echolon.ai:\n"
                f"- Error Code: `{error_code}`\n"
                f"- Request ID: `{request_id}`"
            )
    
    with col2:
        if st.button("📖 View Documentation", use_container_width=True):
            st.info("Documentation coming soon!")


def error_history_widget(
    max_items: int = 10,
) -> None:
    """Display recent error history.
    
    Args:
        max_items: Maximum errors to display
    """
    if "error_history" not in st.session_state:
        st.session_state.error_history = []
    
    if not st.session_state.error_history:
        st.info("No errors recorded yet.")
        return
    
    st.subheader("📊 Error History")
    
    # Display errors in reverse chronological order
    for i, error in enumerate(st.session_state.error_history[-max_items:][::-1]):
        with st.expander(
            f"❌ {error['code']} - {error['timestamp']}",
            expanded=(i == 0)
        ):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**Message:** {error['message']}")
                st.write(f"**Detail:** {error.get('detail', 'N/A')}")
                st.write(f"**Request ID:** `{error.get('request_id', 'N/A')}`")
            with col2:
                if st.button("Retry", key=f"retry_{i}"):
                    st.success("Retry initiated!")


def log_error(
    error_code: str,
    message: str,
    detail: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """Log error to session state history.
    
    Args:
        error_code: Error code
        message: Error message
        detail: Error detail
        request_id: Request ID
    """
    if "error_history" not in st.session_state:
        st.session_state.error_history = []
    
    error_entry = {
        "code": error_code,
        "message": message,
        "detail": detail,
        "request_id": request_id,
        "timestamp": datetime.now().strftime("%H:%M:%S"),
    }
    
    st.session_state.error_history.append(error_entry)
    
    # Keep only last 50 errors
    if len(st.session_state.error_history) > 50:
        st.session_state.error_history = st.session_state.error_history[-50:]


def safe_api_call(
    func: Callable,
    error_title: str = "Operation Failed",
    show_details: bool = True,
) -> Optional[Any]:
    """Wrapper for safe API calls with error handling.
    
    Args:
        func: API function to call
        error_title: Title for error display
        show_details: Show detailed error info
        
    Returns:
        Function result or None if error
    """
    try:
        return func()
    except Exception as e:
        error_code = getattr(e, 'error_code', 'UNKNOWN_ERROR')
        request_id = getattr(e, 'request_id', None)
        
        display_error(
            error_message=error_title,
            error_code=error_code,
            error_detail=str(e),
            request_id=request_id,
            show_details=show_details,
        )
        
        log_error(
            error_code=error_code,
            message=error_title,
            detail=str(e),
            request_id=request_id,
        )
        
        # Show retry option
        if st.button("🔄 Retry"):
            st.rerun()
        
        return None


def network_status_indicator(
    is_online: bool = True,
) -> None:
    """Display network status indicator.
    
    Args:
        is_online: Whether system is online
    """
    if is_online:
        st.success("🟢 Online", icon="✅")
    else:
        st.error("🔴 Offline", icon="❌")


def loading_with_fallback(
    message: str = "Loading...",
    timeout: int = 10,
) -> None:
    """Display loading indicator with timeout fallback.
    
    Args:
        message: Loading message
        timeout: Timeout in seconds
    """
    with st.spinner(f"{message}"):
        # Placeholder for timeout logic
        time.sleep(1)
