import json
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any

def compute_size(data: Any) -> int:
    """Compute size of data in words (space-separated tokens)."""
    if isinstance(data, str):
        return len(data.split())
    elif isinstance(data, dict):
        return sum(compute_size(str(key)) + compute_size(value) for key, value in data.items())
    elif isinstance(data, list):
        return sum(compute_size(item) for item in data)
    else:
        return len(str(data).split())

def _generate_health_summary_text(compressed_data: Dict) -> str:
    """
    Generate a readable health summary text from compressed data.
    
    Args:
        compressed_data: The compressed health data
        
    Returns:
        Readable health summary as text
    """
    summary_parts = []
    trends = compressed_data.get("trends", {})
    
    if "sleep" in trends:
        avg_sleep = trends["sleep"]["avg_duration_hours"]
        summary_parts.append(f"Average sleep: {avg_sleep:.1f} hours per night")
    
    if "exercise" in trends:
        avg_exercise = trends["exercise"]["avg_daily_minutes"]
        summary_parts.append(f"Average daily activity: {avg_exercise:.1f} minutes")
    
    if "nutrition" in trends:
        avg_calories = trends["nutrition"]["avg_daily_calories"]
        summary_parts.append(f"Average calorie intake: {avg_calories:.0f} kcal per day")
    
    if "heart_rate" in trends:
        avg_hr = trends["heart_rate"]["avg"]
        summary_parts.append(f"Average heart rate: {avg_hr:.1f} bpm")
    
    return "; ".join(summary_parts) if summary_parts else "Limited health data available"

def compress_health_data(raw_data: Dict, budget_mode: str) -> Dict:
    """
    Compress health data by aggregating trends and removing redundant information.
    
    Args:
        raw_data: Raw health data as JSON
        budget_mode: LOW, BALANCED, or HIGH - affects compression depth
        
    Returns:
        Compressed health summary with explainability logs
    """
    raw_size = compute_size(raw_data)
    
    # Initialize explainability log
    explainability_log = []
    compressed = {
        "compression_timestamp": datetime.now(timezone.utc).isoformat(),
        "budget_mode": budget_mode,
        "summary": {},
        "trends": {},
        "retained_fields": [],
        "discarded_fields": []
    }
    
    # Process different health data categories
    if "sleep" in raw_data:
        sleep_data = raw_data["sleep"]
        if isinstance(sleep_data, list) and sleep_data:
            # Aggregate sleep trends
            now_utc = datetime.now(timezone.utc)
            recent_sleep = [entry for entry in sleep_data 
                          if datetime.fromisoformat(entry["date"].replace("Z", "+00:00")) 
                          > now_utc - timedelta(days=30)]
            
            if recent_sleep:
                avg_duration = sum(entry.get("duration_hours", 0) for entry in recent_sleep) / len(recent_sleep)
                compressed["trends"]["sleep"] = {
                    "avg_duration_hours": round(avg_duration, 1),
                    "data_points": len(recent_sleep),
                    "trend_period_days": 30
                }
                compressed["retained_fields"].append("sleep_duration_trend")
                explainability_log.append(
                    f"Retained: sleep duration trend ({len(recent_sleep)} days) - "
                    f"avg {avg_duration:.1f} hours/night"
                )
                
                # Discard older sleep data based on budget mode
                if budget_mode == "LOW":
                    cutoff_days = 7
                elif budget_mode == "BALANCED":
                    cutoff_days = 14
                else:  # HIGH
                    cutoff_days = 30
                    
                old_sleep_count = len([entry for entry in sleep_data 
                                     if datetime.fromisoformat(entry["date"].replace("Z", "+00:00")) 
                                     <= now_utc - timedelta(days=cutoff_days)])
                
                if old_sleep_count > 0:
                    compressed["discarded_fields"].append(f"sleep_data_older_than_{cutoff_days}_days")
                    explainability_log.append(
                        f"Discarded: {old_sleep_count} sleep entries older than {cutoff_days} days - "
                        f"Reason: low impact on current recommendations"
                    )
    
    if "exercise" in raw_data:
        exercise_data = raw_data["exercise"]
        if isinstance(exercise_data, list) and exercise_data:
            # Aggregate exercise trends
            recent_exercise = [entry for entry in exercise_data 
                             if datetime.fromisoformat(entry["date"].replace("Z", "+00:00")) 
                             > now_utc - timedelta(days=30)]
            
            if recent_exercise:
                total_minutes = sum(entry.get("duration_minutes", 0) for entry in recent_exercise)
                avg_daily = total_minutes / 30  # 30-day average
                compressed["trends"]["exercise"] = {
                    "avg_daily_minutes": round(avg_daily, 1),
                    "total_sessions": len(recent_exercise),
                    "trend_period_days": 30
                }
                compressed["retained_fields"].append("exercise_frequency_trend")
                explainability_log.append(
                    f"Retained: exercise frequency trend ({len(recent_exercise)} sessions) - "
                    f"avg {avg_daily:.1f} minutes/day"
                )
                
                # Budget-based exercise data retention
                if budget_mode == "LOW":
                    keep_types = ["cardio", "strength"]
                elif budget_mode == "BALANCED":
                    keep_types = ["cardio", "strength", "flexibility"]
                else:  # HIGH
                    keep_types = ["cardio", "strength", "flexibility", "sports", "other"]
                
                discarded_exercises = [entry for entry in recent_exercise 
                                     if entry.get("type", "").lower() not in keep_types]
                
                if discarded_exercises:
                    compressed["discarded_fields"].append("niche_exercise_types")
                    explainability_log.append(
                        f"Discarded: {len(discarded_exercises)} exercise entries of types {set(e.get('type') for e in discarded_exercises)} - "
                        f"Reason: budget mode '{budget_mode}' limits exercise type diversity"
                    )
    
    if "nutrition" in raw_data:
        nutrition_data = raw_data["nutrition"]
        if isinstance(nutrition_data, list) and nutrition_data:
            # Aggregate nutrition trends
            recent_nutrition = [entry for entry in nutrition_data 
                              if datetime.fromisoformat(entry["date"].replace("Z", "+00:00")) 
                              > now_utc - timedelta(days=14)]  # Shorter window for nutrition
            
            if recent_nutrition:
                avg_calories = sum(entry.get("calories", 0) for entry in recent_nutrition) / len(recent_nutrition)
                compressed["trends"]["nutrition"] = {
                    "avg_daily_calories": round(avg_calories, 0),
                    "data_points": len(recent_nutrition),
                    "trend_period_days": 14
                }
                compressed["retained_fields"].append("calorie_intake_trend")
                explainability_log.append(
                    f"Retained: calorie intake trend ({len(recent_nutrition)} days) - "
                    f"avg {avg_calories:.0f} calories/day"
                )
                
                # Discard detailed meal breakdowns based on budget
                if budget_mode == "LOW":
                    # Keep only daily totals
                    compressed["discarded_fields"].append("detailed_meal_breakdowns")
                    explainability_log.append(
                        "Discarded: detailed meal breakdowns - "
                        "Reason: LOW budget mode requires minimal nutrition tracking"
                    )
                elif budget_mode == "BALANCED":
                    # Keep meal types but not ingredients
                    compressed["discarded_fields"].append("ingredient_level_details")
                    explainability_log.append(
                        "Discarded: ingredient-level details - "
                        "Reason: BALANCED budget mode optimizes for meal-level tracking"
                    )
    
    if "vitals" in raw_data:
        vitals_data = raw_data["vitals"]
        if isinstance(vitals_data, list) and vitals_data:
            # Keep only recent vitals
            if budget_mode == "LOW":
                cutoff_days = 7
            elif budget_mode == "BALANCED":
                cutoff_days = 14
            else:  # HIGH
                cutoff_days = 30
                
            recent_vitals = [entry for entry in vitals_data 
                            if datetime.fromisoformat(entry["date"].replace("Z", "+00:00")) 
                            > now_utc - timedelta(days=cutoff_days)]
            
            if recent_vitals:
                # Aggregate key vitals
                heart_rates = [entry.get("heart_rate", 0) for entry in recent_vitals if entry.get("heart_rate")]
                if heart_rates:
                    compressed["trends"]["heart_rate"] = {
                        "avg": round(sum(heart_rates) / len(heart_rates), 1),
                        "data_points": len(heart_rates)
                    }
                    compressed["retained_fields"].append("heart_rate_trend")
                    explainability_log.append(
                        f"Retained: heart rate trend ({len(heart_rates)} readings) - "
                        f"avg {sum(heart_rates) / len(heart_rates):.1f} bpm"
                    )
            
            old_vitals_count = len([entry for entry in vitals_data 
                                  if datetime.fromisoformat(entry["date"].replace("Z", "+00:00")) 
                                  <= now_utc - timedelta(days=cutoff_days)])
            
            if old_vitals_count > 0:
                compressed["discarded_fields"].append(f"vitals_older_than_{cutoff_days}_days")
                explainability_log.append(
                    f"Discarded: {old_vitals_count} vital readings older than {cutoff_days} days - "
                    f"Reason: outdated health metrics"
                )
    
    # Add summary statistics
    compressed["summary"]["total_data_points"] = (
        compressed["trends"].get("sleep", {}).get("data_points", 0) +
        compressed["trends"].get("exercise", {}).get("total_sessions", 0) +
        compressed["trends"].get("nutrition", {}).get("data_points", 0) +
        compressed["trends"].get("heart_rate", {}).get("data_points", 0)
    )
    
    compressed["summary"]["compression_ratio"] = f"{len(compressed['retained_fields'])}:{len(compressed['discarded_fields'])}"
    
    compressed_json_size = compute_size(compressed)
    
    # Generate health summary text for separate size calculation
    health_summary_text = _generate_health_summary_text(compressed)
    health_summary_size = compute_size(health_summary_text)
    
    # Final explainability summary
    explainability_log.insert(0, f"Raw size: {raw_size} words")
    explainability_log.insert(1, f"Compressed JSON size: {compressed_json_size} words")
    explainability_log.insert(2, f"Health summary text size: {health_summary_size} words")
    explainability_log.append(f"Compression achieved: {((raw_size - compressed_json_size) / raw_size * 100):.1f}% reduction")
    
    compressed["explainability_log"] = explainability_log
    compressed["health_summary_text"] = health_summary_text
    
    return compressed
