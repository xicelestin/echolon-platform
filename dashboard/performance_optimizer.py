"""Performance Optimization Module for Echolon Dashboard
Optimizes data processing, caching, and memory management for large datasets.
"""

import streamlit as st
import pandas as pd
import numpy as np
from functools import wraps
import time
import psutil
import logging
from typing import Callable, Any, Dict

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """Handles caching, chunked processing, and memory optimization."""
    
    CHUNK_SIZE = 10000  # Process 10k rows per batch
    MEMORY_THRESHOLD_MB = 500  # Alert if > 500MB
    
    @staticmethod
    def get_memory_usage() -> float:
        """Get current memory usage in MB."""
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    @staticmethod
    def get_memory_percentage() -> float:
        """Get memory usage as percentage of total system memory."""
        process = psutil.Process()
        return process.memory_percent()
    
    @staticmethod
    def process_large_csv(df: pd.DataFrame, chunk_callback: Callable) -> pd.DataFrame:
        """Process CSV in chunks to manage memory."""
        if len(df) <= PerformanceOptimizer.CHUNK_SIZE:
            return chunk_callback(df)
        
        results = []
        total_chunks = (len(df) + PerformanceOptimizer.CHUNK_SIZE - 1) // PerformanceOptimizer.CHUNK_SIZE
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, chunk in enumerate(np.array_split(df, total_chunks)):
            status_text.text(f"Processing chunk {i+1}/{total_chunks}...")
            result = chunk_callback(chunk)
            results.append(result)
            progress_bar.progress((i + 1) / total_chunks)
        
        progress_bar.empty()
        status_text.empty()
        
        return pd.concat(results, ignore_index=True)
    
    @staticmethod
    def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Optimize dataframe memory usage by downcasting types."""
        for col in df.columns:
            col_type = df[col].dtype
            
            if col_type == 'float64':
                df[col] = df[col].astype('float32')
            elif col_type == 'int64':
                if df[col].min() >= 0:
                    if df[col].max() < 256:
                        df[col] = df[col].astype('uint8')
                    elif df[col].max() < 65536:
                        df[col] = df[col].astype('uint16')
                    else:
                        df[col] = df[col].astype('uint32')
                else:
                    if df[col].max() < 128 and df[col].min() > -129:
                        df[col] = df[col].astype('int8')
                    elif df[col].max() < 32768 and df[col].min() > -32769:
                        df[col] = df[col].astype('int16')
                    else:
                        df[col] = df[col].astype('int32')
        
        return df
    
    @staticmethod
    def render_performance_metrics(df: pd.DataFrame) -> None:
        """Render performance monitoring dashboard."""
        col1, col2, col3, col4 = st.columns(4)
        
        file_size_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
        current_memory = PerformanceOptimizer.get_memory_usage()
        
        with col1:
            st.metric(
                "File Size",
                f"{file_size_mb:.1f} MB" if file_size_mb > 1 else f"{file_size_mb*1024:.0f} KB",
                help="Estimated memory usage"
            )
        
        with col2:
            st.metric(
                "Row Count",
                f"{len(df):,}",
                help="Total rows in dataset"
            )
        
        with col3:
            processing_time = st.session_state.get('last_processing_time', 0)
            st.metric(
                "Processing Time",
                f"{processing_time:.2f}s" if processing_time > 0 else "<0.1s",
                help="Time to load and process data"
            )
        
        with col4:
            quality_score = st.session_state.get('data_quality_score', 0)
            st.metric(
                "Quality Score",
                f"{quality_score}%",
                help="Data quality assessment (0-100%)"
            )
        
        # Memory warning
        if current_memory > PerformanceOptimizer.MEMORY_THRESHOLD_MB:
            st.warning(f"⚠️ Memory usage high: {current_memory:.0f}MB / {PerformanceOptimizer.MEMORY_THRESHOLD_MB}MB threshold")
        else:
            st.success(f"✅ Memory usage healthy: {current_memory:.0f}MB")


def cached_data_processing(func: Callable) -> Callable:
    """Decorator for cached data processing with hash-based invalidation."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from function name and arguments
        cache_key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
        
        if cache_key in st.session_state:
            return st.session_state[cache_key]
        
        start_time = time.time()
        result = func(*args, **kwargs)
        processing_time = time.time() - start_time
        
        # Store in session state
        st.session_state[cache_key] = result
        st.session_state['last_processing_time'] = processing_time
        
        logger.info(f"{func.__name__} completed in {processing_time:.2f}s")
        return result
    
    return wrapper


def estimate_data_quality(df: pd.DataFrame) -> int:
    """Estimate data quality score (0-100)."""
    score = 100
    
    # Check for missing values
    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    score -= min(missing_pct, 20)  # -20 max for missing values
    
    # Check for duplicates
    dup_pct = (df.duplicated().sum() / len(df)) * 100
    score -= min(dup_pct * 2, 15)  # -15 max for duplicates
    
    # Check for outliers in numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outliers = 0
    for col in numeric_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outlier_count = len(df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)])
        outliers += outlier_count
    
    outlier_pct = (outliers / len(df)) * 100
    score -= min(outlier_pct, 10)  # -10 max for outliers
    
    return max(0, score)


def lazy_load_csv(uploaded_file, nrows: int = None) -> pd.DataFrame:
    """Lazy load CSV to manage large files."""
    try:
        df = pd.read_csv(uploaded_file, nrows=nrows)
        st.session_state['data_quality_score'] = estimate_data_quality(df)
        return df
    except Exception as e:
        st.error(f"Error loading CSV: {str(e)}")
        return None
