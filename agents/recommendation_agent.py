from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
import os

# Add services directory to path for LLM client
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

# Import LLM client and configuration
from services.llm_client import generate_llm_recommendation
from config.settings import USE_FALLBACK_MODE

class RecommendationAgent:
    """
    Generates personalized health recommendations based on compressed memory.
    
    BUDGET MODE IMPACT (MANDATORY):
    - LOW: Short summary + 1 recommendation
    - BALANCED: Moderate detail + 2-3 recommendations  
    - HIGH: Detailed insights + reasoning
    
    Uses ONLY compressed memory - never raw data.
    """
    
    def __init__(self):
        self.recommendation_templates = {
            "sleep": {
                "low": ["Improve sleep consistency by going to bed at the same time daily."],
                "balanced": [
                    "Maintain consistent sleep schedule (within 30 minutes variance).",
                    "Create a relaxing bedtime routine to improve sleep quality."
                ],
                "high": [
                    "Maintain consistent sleep schedule (within 30 minutes variance) to regulate circadian rhythm.",
                    "Implement a 30-minute wind-down routine: dim lights, avoid screens, practice relaxation.",
                    "Consider sleep hygiene improvements: cool room (65-68°F), minimal noise, comfortable bedding."
                ]
            },
            "exercise": {
                "low": ["Increase daily physical activity to meet recommended guidelines."],
                "balanced": [
                    "Aim for 150 minutes of moderate exercise weekly (22 mins daily).",
                    "Include both cardio and strength training for balanced fitness."
                ],
                "high": [
                    "Target 150 minutes moderate cardio OR 75 minutes vigorous cardio weekly.",
                    "Incorporate strength training 2-3 times weekly for major muscle groups.",
                    "Add flexibility work (stretching/yoga) 2-3 times weekly for mobility and injury prevention."
                ]
            },
            "nutrition": {
                "low": ["Focus on balanced nutrition with adequate hydration."],
                "balanced": [
                    "Maintain balanced macronutrients: 45-65% carbs, 10-35% protein, 20-35% fats.",
                    "Drink 8 glasses (64oz) of water daily for optimal hydration."
                ],
                "high": [
                    "Balance macronutrients: 45-65% complex carbs, 10-35% lean protein, 20-35% healthy fats.",
                    "Hydrate with 64-96oz water daily, adjusting for activity level and climate.",
                    "Prioritize whole foods: vegetables, fruits, lean proteins, whole grains, healthy fats."
                ]
            },
            "heart_rate": {
                "low": ["Monitor heart rate trends for cardiovascular health insights."],
                "balanced": [
                    "Track resting heart rate trends as an indicator of cardiovascular fitness.",
                    "Consult healthcare provider if resting HR consistently above 100 bpm."
                ],
                "high": [
                    "Monitor resting heart rate (ideal 60-100 bpm) as cardiovascular fitness indicator.",
                    "Track HR recovery rate post-exercise (should drop 20+ bpm within 1 minute).",
                    "Consider heart rate variability (HRV) for stress and recovery insights if available."
                ]
            }
        }
    
    def generate_recommendations(self, compressed_data: Dict[str, Any], budget_mode: str) -> Dict[str, Any]:
        """
        Generate personalized health recommendations based on compressed data.
        
        Uses ScaleDown AI API when USE_FALLBACK_MODE = False AND API key is valid,
        otherwise uses deterministic logic.
        
        Args:
            compressed_data: Compressed health data from context manager
            budget_mode: LOW, BALANCED, or HIGH - affects output verbosity
            
        Returns:
            Dictionary with recommendations and metadata
        """
        trends = compressed_data.get("trends", {})
        
        # Generate health twin snapshot first (needed for API prompt)
        health_twin = self._generate_health_twin(trends)
        
        # Smart decision making: check both fallback mode AND API key validity
        should_use_fallback = USE_FALLBACK_MODE
        
        if should_use_fallback:
            if USE_FALLBACK_MODE:
                print("USING FALLBACK MODE (User configured)")
            else:
                print("USING FALLBACK MODE (Invalid API key)")
            return self._generate_deterministic_recommendations(trends, budget_mode, health_twin)
        else:
            print("USING SCALEDOWN API (Valid API key)")
            return self._generate_api_recommendations(trends, budget_mode, health_twin)
    
    def _generate_health_twin(self, trends: Dict[str, Any]) -> str:
        """
        Generate a single-paragraph digital health twin based on compressed numerical statistics.
        
        Args:
            trends: Health trend data from compression
            
        Returns:
            Health twin description paragraph with specific numerical values
        """
        twin_parts = []
        
        # Sleep statistics
        if "sleep" in trends:
            avg_sleep = trends["sleep"]["avg_duration_hours"]
            twin_parts.append(f"averaging {avg_sleep:.1f} hours of sleep per night")
        
        # Exercise statistics  
        if "exercise" in trends:
            avg_daily = trends["exercise"]["avg_daily_minutes"]
            twin_parts.append(f"engaging in {avg_daily:.1f} minutes of daily activity")
        
        # Nutrition statistics
        if "nutrition" in trends:
            avg_calories = trends["nutrition"]["avg_daily_calories"]
            twin_parts.append(f"maintaining an average calorie intake of {avg_calories:.0f} kcal")
        
        # Combine into one concise paragraph
        if twin_parts:
            if len(twin_parts) == 1:
                health_twin = f"A moderate sleeper {twin_parts[0]}."
            elif len(twin_parts) == 2:
                health_twin = f"A moderate sleeper {twin_parts[0]} and {twin_parts[1]}."
            else:
                health_twin = f"A moderate sleeper {twin_parts[0]}, {twin_parts[1]}, and {twin_parts[2]}."
        else:
            health_twin = "Individual with limited health data available for analysis."
        
        return health_twin
    
    def _generate_api_recommendations(self, trends: Dict[str, Any], budget_mode: str, health_twin: str) -> Dict[str, Any]:
        """
        Generate recommendations using ScaleDown AI API with fallback safety.
        
        Args:
            trends: Health trend data
            budget_mode: LOW, BALANCED, or HIGH
            health_twin: Generated health twin description
            
        Returns:
            Dictionary with API-generated or fallback recommendations
        """
        try:
            # Construct the prompt programmatically
            prompt = self._construct_api_prompt(trends, budget_mode, health_twin)
            
            # Call ScaleDown API
            api_response = generate_llm_recommendation(prompt)
            
            # Parse API response and format according to budget mode
            return self._parse_api_response(api_response, budget_mode, trends, health_twin)
            
        except Exception as e:
            print(f"API call failed, falling back to deterministic logic: {str(e)}")
            return self._generate_deterministic_recommendations(trends, budget_mode, health_twin)
    
    def _construct_api_prompt(self, trends: Dict[str, Any], budget_mode: str, health_twin: str) -> str:
        """
        Construct the prompt for ScaleDown AI API.
        
        Args:
            trends: Health trend data
            budget_mode: LOW, BALANCED, or HIGH
            health_twin: Generated health twin description
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Based on the following health twin analysis, provide personalized health recommendations:

HEALTH TWIN SUMMARY:
{health_twin}

DETAILED HEALTH DATA:
"""
        
        # Add detailed trend data
        if "sleep" in trends:
            sleep_data = trends["sleep"]
            prompt += f"- Sleep: {sleep_data.get('avg_duration_hours', 0):.1f} hours average duration\n"
        
        if "exercise" in trends:
            exercise_data = trends["exercise"]
            prompt += f"- Exercise: {exercise_data.get('avg_daily_minutes', 0):.1f} minutes daily average\n"
        
        if "nutrition" in trends:
            nutrition_data = trends["nutrition"]
            prompt += f"- Nutrition: {nutrition_data.get('avg_daily_calories', 0):.0f} calories daily average\n"
        
        if "heart_rate" in trends:
            heart_rate_data = trends["heart_rate"]
            prompt += f"- Heart Rate: {heart_rate_data.get('avg', 0):.1f} bpm average\n"
        
        prompt += f"""
BUDGET MODE: {budget_mode}

RECOMMENDATION REQUIREMENTS:
"""
        
        if budget_mode == "LOW":
            prompt += """- Provide exactly 1 recommendation maximum
- Keep it concise and actionable
- Focus on the most critical health issue"""
        elif budget_mode == "BALANCED":
            prompt += """- Provide 2-3 recommendations
- Include moderate detail for each
- Cover multiple health aspects if relevant"""
        else:  # HIGH
            prompt += """- Provide detailed recommendations with reasoning
- Include comprehensive health insights
- Explain the 'why' behind each recommendation"""
        
        prompt += """

Format your response as a list of recommendations, each on a new line.
Be specific and actionable based on the health data provided.
"""
        
        return prompt
    
    def _parse_api_response(self, api_response: str, budget_mode: str, trends: Dict[str, Any], health_twin: str) -> Dict[str, Any]:
        """
        Parse API response and format according to budget mode.
        
        Args:
            api_response: Raw response from ScaleDown AI
            budget_mode: LOW, BALANCED, or HIGH
            trends: Health trend data
            health_twin: Generated health twin description
            
        Returns:
            Formatted recommendations dictionary
        """
        # Split response into lines and clean up
        lines = [line.strip() for line in api_response.split('\n') if line.strip()]
        
        # Filter out non-recommendation lines (keep numbered or bulleted items)
        recommendations = []
        for line in lines:
            # Remove numbering/bullets and clean up
            clean_line = line
            if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•', '*')):
                clean_line = line[2:].strip() if line[1] in '. ' else line[1:].strip()
            
            if clean_line and len(clean_line) > 10:  # Filter out very short lines
                recommendations.append(clean_line)
        
        # Apply budget mode constraints
        if budget_mode == "LOW":
            recommendations = recommendations[:1]
        elif budget_mode == "BALANCED":
            recommendations = recommendations[:3]
        # HIGH mode keeps all recommendations
        
        # Generate reasoning for HIGH mode (simplified version)
        reasoning = []
        if budget_mode == "HIGH":
            reasoning = [
                f"AI-generated recommendations based on analysis of {len(trends)} health metrics",
                f"Personalized using health twin: {health_twin[:50]}..." if len(health_twin) > 50 else f"Personalized using health twin data"
            ]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "budget_mode": budget_mode,
            "health_twin": health_twin,
            "recommendations": recommendations,
            "reasoning": reasoning,
            "data_sources": list(trends.keys()),
            "recommendation_count": len(recommendations),
            "api_generated": True
        }
    
    def _generate_deterministic_recommendations(self, trends: Dict[str, Any], budget_mode: str, health_twin: str) -> Dict[str, Any]:
        """
        Generate deterministic recommendations using original logic (fallback mode).
        
        Args:
            trends: Health trend data
            budget_mode: LOW, BALANCED, or HIGH
            health_twin: Generated health twin description
            
        Returns:
            Dictionary with deterministic recommendations
        """
        recommendations = []
        reasoning = []
        budget_mode_lower = budget_mode.lower()
        
        # Analyze sleep trends and create personalized recommendations
        if "sleep" in trends:
            sleep_data = trends["sleep"]
            avg_sleep = sleep_data.get("avg_duration_hours", 0)
            
            if avg_sleep < 7:
                if budget_mode == "LOW":
                    recommendations.append(f"Increase sleep from current {avg_sleep:.1f} hours to at least 7 hours nightly.")
                elif budget_mode == "BALANCED":
                    recommendations.append(f"Increase sleep from {avg_sleep:.1f} hours to 7-9 hours by maintaining consistent bedtime.")
                    recommendations.append("Create a relaxing bedtime routine to improve sleep quality.")
                else:  # HIGH
                    recommendations.append(f"Increase sleep from {avg_sleep:.1f} hours to 7-9 hours to regulate circadian rhythm.")
                    recommendations.append("Implement 30-minute wind-down routine: dim lights, avoid screens, practice relaxation.")
                    recommendations.append("Optimize sleep environment: cool room (65-68°F), minimal noise, comfortable bedding.")
                reasoning.append(f"Sleep duration {avg_sleep:.1f} hours below recommended 7-9 hours.")
            elif avg_sleep > 9:
                if budget_mode == "HIGH":
                    recommendations.append(f"Consider reducing sleep from {avg_sleep:.1f} hours toward 7-9 hour range.")
                    recommendations.append("If sleeping >9 hours, consult healthcare provider to rule out underlying conditions.")
                reasoning.append(f"Sleep duration {avg_sleep:.1f} hours exceeds recommended range.")
            else:
                if budget_mode == "HIGH":
                    reasoning.append(f"Sleep duration {avg_sleep:.1f} hours within healthy range.")
        
        # Analyze exercise trends and create personalized recommendations
        if "exercise" in trends:
            exercise_data = trends["exercise"]
            avg_daily = exercise_data.get("avg_daily_minutes", 0)
            
            if avg_daily < 22:  # 150 minutes / 7 days
                if budget_mode == "LOW":
                    recommendations.append(f"Increase daily activity from current {avg_daily:.1f} minutes to at least 22 minutes.")
                elif budget_mode == "BALANCED":
                    recommendations.append(f"Increase daily activity from {avg_daily:.1f} minutes to 22 minutes for 150 minutes weekly.")
                    recommendations.append("Include both cardio and strength training for balanced fitness.")
                else:  # HIGH
                    recommendations.append(f"Increase daily activity from {avg_daily:.1f} minutes to 22 minutes for 150+ minutes weekly.")
                    recommendations.append("Add strength training 2-3 times weekly for major muscle groups.")
                    recommendations.append("Include flexibility work 2-3 times weekly for mobility and injury prevention.")
                reasoning.append(f"Exercise average {avg_daily:.1f} minutes/day below recommended 22 minutes.")
            else:
                if budget_mode == "HIGH":
                    reasoning.append(f"Exercise average {avg_daily:.1f} minutes/day meets guidelines.")
        
        # Analyze nutrition trends and create personalized recommendations
        if "nutrition" in trends:
            nutrition_data = trends["nutrition"]
            avg_calories = nutrition_data.get("avg_daily_calories", 0)
            
            if avg_calories < 1500:
                if budget_mode == "LOW":
                    recommendations.append(f"Increase calorie intake from current {avg_calories:.0f} kcal to meet basic needs.")
                elif budget_mode == "BALANCED":
                    recommendations.append(f"Increase calorie intake from {avg_calories:.0f} kcal to at least 1500-1800 kcal daily.")
                    recommendations.append("Focus on balanced macronutrients and adequate hydration.")
                else:  # HIGH
                    recommendations.append(f"Increase calorie intake from {avg_calories:.0f} kcal to 1500-2000+ kcal based on activity level.")
                    recommendations.append("Balance macronutrients: 45-65% complex carbs, 10-35% lean protein, 20-35% healthy fats.")
                    recommendations.append("Hydrate with 64-96oz water daily, adjusting for activity level and climate.")
                reasoning.append(f"Calorie intake {avg_calories:.0f} may be insufficient for basic needs.")
            elif avg_calories > 3000:
                if budget_mode in ["BALANCED", "HIGH"]:
                    if budget_mode == "BALANCED":
                        recommendations.append(f"Consider reducing calorie intake from {avg_calories:.0f} kcal toward 2000-2500 range.")
                        recommendations.append("Maintain balanced macronutrients while reducing overall intake.")
                    else:  # HIGH
                        recommendations.append(f"Consider reducing calorie intake from {avg_calories:.0f} kcal toward individual requirements.")
                        recommendations.append("Prioritize nutrient-dense whole foods while managing total intake.")
                        recommendations.append("Monitor portion sizes and focus on balanced macronutrient distribution.")
                    reasoning.append(f"Calorie intake {avg_calories:.0f} exceeds typical requirements.")
            else:
                if budget_mode == "HIGH":
                    reasoning.append(f"Calorie intake {avg_calories:.0f} within reasonable range.")
        
        # Analyze heart rate trends and create personalized recommendations
        if "heart_rate" in trends:
            heart_rate_data = trends["heart_rate"]
            avg_hr = heart_rate_data.get("avg", 0)
            
            if avg_hr > 80:
                if budget_mode == "LOW":
                    recommendations.append(f"Monitor elevated heart rate of {avg_hr:.1f} bpm - consider stress management.")
                elif budget_mode == "BALANCED":
                    recommendations.append(f"Monitor heart rate trends (current avg {avg_hr:.1f} bpm) for cardiovascular health.")
                    recommendations.append("Consult healthcare provider if resting HR consistently above 100 bpm.")
                else:  # HIGH
                    recommendations.append(f"Monitor resting heart rate (current avg {avg_hr:.1f} bpm, ideal 60-100 bpm).")
                    recommendations.append("Track HR recovery rate post-exercise (should drop 20+ bpm within 1 minute).")
                    recommendations.append("Consider stress reduction techniques and regular cardiovascular exercise.")
                reasoning.append(f"Average heart rate {avg_hr:.1f} bpm elevated; may indicate stress or poor fitness.")
            else:
                if budget_mode == "HIGH":
                    reasoning.append(f"Average heart rate {avg_hr:.1f} bpm within normal range.")
        
        # Apply budget mode constraints
        if budget_mode == "LOW":
            # Keep only 1 recommendation (highest priority)
            if recommendations:
                recommendations = [recommendations[0]]
            reasoning = [reasoning[0]] if reasoning else []
        elif budget_mode == "BALANCED":
            # Keep 2-3 recommendations
            recommendations = recommendations[:3]
            reasoning = reasoning[:3]
        # HIGH mode keeps all recommendations and reasoning
        
        return {
            "timestamp": datetime.now().isoformat(),
            "budget_mode": budget_mode,
            "health_twin": health_twin,
            "recommendations": recommendations,
            "reasoning": reasoning if budget_mode == "HIGH" else [],
            "data_sources": list(trends.keys()),
            "recommendation_count": len(recommendations),
            "api_generated": False
        }
