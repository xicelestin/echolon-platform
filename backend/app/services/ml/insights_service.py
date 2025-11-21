"""Insights service using OpenAI to generate business insights from forecast data."""

import openai
from typing import List
import json

from .schemas import InsightsRequest, InsightsResponse, ForecastPoint
from .config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY


class InsightsService:
    """Service for generating AI-powered business insights."""
    
    @staticmethod
    def generate_insights(request: InsightsRequest) -> InsightsResponse:
        """
        Generate AI insights using OpenAI GPT.
        
        Args:
            request: InsightsRequest with business context and forecast data
        
        Returns:
            InsightsResponse with insights, findings, and recommendations
        """
        # Prepare context for OpenAI
        context = InsightsService._prepare_context(request)
        
        # Create prompt
        prompt = InsightsService._create_prompt(request, context)
        
        # Call OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert business analyst specializing in data-driven insights and forecasting. Provide actionable, specific recommendations based on the data provided."},
                    {"role": "user", "content": prompt}
                ],
                temperature=OPENAI_TEMPERATURE,
                max_tokens=OPENAI_MAX_TOKENS
            )
            
            # Parse response
            insights_text = response.choices[0].message.content
            
            # Extract structured information
            parsed = InsightsService._parse_insights(insights_text)
            
            return InsightsResponse(
                business_id=request.business_id,
                metric_name=request.metric_name,
                insights=insights_text,
                key_findings=parsed["key_findings"],
                recommendations=parsed["recommendations"]
            )
            
        except Exception as e:
            # Fallback response if OpenAI fails
            return InsightsResponse(
                business_id=request.business_id,
                metric_name=request.metric_name,
                insights=f"Unable to generate insights: {str(e)}",
                key_findings=["OpenAI API error"],
                recommendations=["Please check API key and try again"]
            )
    
    @staticmethod
    def _prepare_context(request: InsightsRequest) -> dict:
        """
        Prepare context dictionary from request data.
        """
        context = {
            "business_id": request.business_id,
            "metric": request.metric_name,
            "has_forecast": request.forecast_data is not None,
            "has_historical": request.historical_summary is not None
        }
        
        if request.forecast_data:
            forecast_values = [p.value for p in request.forecast_data]
            context["forecast_count"] = len(forecast_values)
            context["forecast_mean"] = sum(forecast_values) / len(forecast_values) if forecast_values else 0
            context["forecast_min"] = min(forecast_values) if forecast_values else 0
            context["forecast_max"] = max(forecast_values) if forecast_values else 0
        
        if request.historical_summary:
            context.update(request.historical_summary)
        
        return context
    
    @staticmethod
    def _create_prompt(request: InsightsRequest, context: dict) -> str:
        """
        Create OpenAI prompt from request and context.
        """
        prompt_parts = [
            f"Analyze the following business metric data for '{request.metric_name}':\n"
        ]
        
        # Add historical summary if available
        if request.historical_summary:
            prompt_parts.append("\nHistorical Context:")
            for key, value in request.historical_summary.items():
                prompt_parts.append(f"- {key}: {value}")
        
        # Add forecast data if available
        if request.forecast_data:
            prompt_parts.append(f"\nForecast Data ({len(request.forecast_data)} periods):")
            forecast_summary = f"- Average predicted value: {context.get('forecast_mean', 0):.2f}"
            prompt_parts.append(forecast_summary)
            prompt_parts.append(f"- Range: {context.get('forecast_min', 0):.2f} to {context.get('forecast_max', 0):.2f}")
            
            # Add first few and last few forecast points
            if len(request.forecast_data) > 0:
                prompt_parts.append("\nSample Forecast Points:")
                sample_points = request.forecast_data[:5] + request.forecast_data[-5:] if len(request.forecast_data) > 10 else request.forecast_data
                for point in sample_points:
                    prompt_parts.append(f"- {point.date}: {point.value:.2f}")
        
        prompt_parts.append("\nPlease provide:")
        prompt_parts.append("1. Key Findings: 3-5 bullet points highlighting important patterns or trends")
        prompt_parts.append("2. Recommendations: 3-5 actionable recommendations for the business")
        prompt_parts.append("3. Overall Analysis: A comprehensive paragraph summarizing the insights")
        
        return "\n".join(prompt_parts)
    
    @staticmethod
    def _parse_insights(insights_text: str) -> dict:
        """
        Extract key findings and recommendations from insights text.
        """
        lines = insights_text.split("\n")
        key_findings = []
        recommendations = []
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect sections
            if "key finding" in line.lower() or "findings:" in line.lower():
                current_section = "findings"
                continue
            elif "recommendation" in line.lower():
                current_section = "recommendations"
                continue
            elif "analysis" in line.lower() or "summary" in line.lower():
                current_section = None
                continue
            
            # Extract bullet points
            if line.startswith("-") or line.startswith("•") or (len(line) > 2 and line[0].isdigit() and line[1] in ".)"):
                cleaned = line.lstrip("-•0123456789.) ").strip()
                if current_section == "findings" and cleaned:
                    key_findings.append(cleaned)
                elif current_section == "recommendations" and cleaned:
                    recommendations.append(cleaned)
        
        # Fallback if parsing fails
        if not key_findings:
            key_findings = ["Analysis complete - see full insights for details"]
        if not recommendations:
            recommendations = ["Review forecast data for strategic planning"]
        
        return {
            "key_findings": key_findings[:5],  # Limit to 5
            "recommendations": recommendations[:5]  # Limit to 5
        }
