#!/usr/bin/env python3
"""
Personal Health Coach - Agentic AI
HPE GenAI for GenZ Challenge - Week 1

Main execution script that demonstrates:
- Health data compression with explainability
- Budget-aware AI behavior
- Health twin generation
- Personalized recommendations
"""

import json
import sys
import os
from datetime import datetime

# Add agents directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

# Import configuration
from config.settings import BUDGET_MODE, USE_FALLBACK_MODE

# Import agents
from agents.compression_agent import compress_health_data, compute_size
from agents.context_manager import ContextManager
from agents.recommendation_agent import RecommendationAgent

def load_sample_health_data():
    """Load sample health data from JSON file."""
    try:
        with open('data/sample_health_data.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("ERROR: data/sample_health_data.json not found!")
        print("Please ensure the sample health data file exists.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in sample health data: {e}")
        sys.exit(1)

def print_section_header(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_subsection(title):
    """Print a formatted subsection header."""
    print(f"\n--- {title} ---")

def main():
    """Main execution function."""
    print_section_header("PERSONAL HEALTH COACH - AGENTIC AI")
    print("HPE GenAI for GenZ Challenge - Week 1")
    print(f"Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Load raw health data
    print_subsection("LOADING RAW HEALTH DATA")
    raw_health_data = load_sample_health_data()
    raw_size = compute_size(raw_health_data)
    print(f"Raw data loaded successfully")
    print(f"Data categories: {list(raw_health_data.keys())}")
    
    # Step 2: Compress health data with explainability
    print_subsection("COMPRESSING HEALTH DATA")
    compressed_data = compress_health_data(raw_health_data, BUDGET_MODE)
    compressed_json_size = compute_size(compressed_data)
    
    # Display compression results
    print(f"Raw data size: {raw_size} words")
    print(f"Compressed JSON size: {compressed_json_size} words")
    print(f"Compression achieved: {((raw_size - compressed_json_size) / raw_size * 100):.1f}% reduction")
    
    # Step 3: Show explainability log
    print_subsection("EXPLAINABILITY LOG")
    if "explainability_log" in compressed_data:
        for log_entry in compressed_data["explainability_log"]:
            print(f"  {log_entry}")
    
    # Step 4: Store compressed data in context manager
    print_subsection("STORING COMPRESSED MEMORY")
    context_manager = ContextManager()
    storage_success = context_manager.store_compressed_summary(compressed_data)
    
    if storage_success:
        print("✓ Compressed data stored successfully")
        memory_stats = context_manager.get_memory_stats()
        print(f"  Total summaries stored: {memory_stats['total_summaries_stored']}")
        print(f"  Memory file size: {memory_stats['file_size_bytes']} bytes")
    else:
        print("✗ Failed to store compressed data")
    
    # Step 5: Display budget mode and API configuration
    print_subsection("BUDGET MODE CONFIGURATION")
    print(f"Selected Budget Mode: {BUDGET_MODE}")
    print(f"API Mode: {'FALLBACK (Deterministic)' if USE_FALLBACK_MODE else 'SCALEDOWN AI API'}")
    
    budget_descriptions = {
        "LOW": "Short summary + 1 recommendation, minimal data retention",
        "BALANCED": "Moderate detail + 2-3 recommendations, balanced data retention", 
        "HIGH": "Detailed insights + reasoning, comprehensive data retention"
    }
    print(f"Behavior: {budget_descriptions.get(BUDGET_MODE, 'Unknown')}")
    
    # Step 6: Generate recommendations
    print_subsection("GENERATING PERSONALIZED RECOMMENDATIONS")
    recommendation_agent = RecommendationAgent()
    
    # Get current health state from context manager
    current_state = context_manager.get_current_health_state()
    if current_state:
        recommendations = recommendation_agent.generate_recommendations(
            current_state, 
            BUDGET_MODE
        )
        
        # Step 7: Display Health Twin Snapshot
        print_subsection("HEALTH TWIN SNAPSHOT")
        print(recommendations["health_twin"])
        
        # Step 8: Display personalized recommendations
        print_subsection("PERSONALIZED RECOMMENDATIONS")
        print(f"Number of recommendations: {recommendations['recommendation_count']}")
        
        for i, rec in enumerate(recommendations["recommendations"], 1):
            print(f"  {i}. {rec}")
        
        # Show reasoning for HIGH budget mode
        if BUDGET_MODE == "HIGH" and recommendations["reasoning"]:
            print_subsection("RECOMMENDATION REASONING")
            for reason in recommendations["reasoning"]:
                print(f"  • {reason}")
        
        # Show data sources used
        print_subsection("DATA SOURCES USED")
        print(f"  Analyzed: {', '.join(recommendations['data_sources'])}")
        
        # Show API metadata if API was used
        if recommendations.get('api_generated', False):
            print_subsection("API METADATA")
            print("  ✓ ScaleDown AI API successfully called")
            print("  ✓ Real AI-generated recommendations provided")
        else:
            print_subsection("API METADATA")
            print("  ✓ Fallback mode - deterministic logic used")
        
    else:
        print("✗ No health state available for recommendations")
    
    # Step 9: Final summary
    print_section_header("EXECUTION SUMMARY")
    print(f"✓ Raw data processed: {raw_size} words")
    print(f"✓ Data compressed: {compressed_json_size} words ({((raw_size - compressed_json_size) / raw_size * 100):.1f}% reduction)")
    print(f"✓ Budget mode: {BUDGET_MODE}")
    print(f"✓ Health twin generated")
    print(f"✓ Recommendations provided: {recommendations.get('recommendation_count', 0)}")
    print(f"✓ Memory updated: {storage_success}")
    
    print_section_header("PERSONAL HEALTH COACH - EXECUTION COMPLETE")
    print("All features executed successfully!")
    print("Change BUDGET_MODE in config/settings.py to test different behaviors.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExecution interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        print("Please check your configuration and try again.")
        sys.exit(1)
