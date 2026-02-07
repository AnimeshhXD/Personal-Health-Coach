import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

class ContextManager:
    """
    Manages compressed health memory storage and retrieval.
    
    STRICT RULES:
    - Stores ONLY compressed summaries
    - Overwrites outdated health memory
    - Never stores raw historical data
    - Saves to compressed_memory.json
    """
    
    def __init__(self, memory_file_path: str = "data/compressed_memory.json"):
        self.memory_file_path = memory_file_path
        self._ensure_memory_file_exists()
    
    def _ensure_memory_file_exists(self):
        """Create memory file if it doesn't exist."""
        if not os.path.exists(self.memory_file_path):
            os.makedirs(os.path.dirname(self.memory_file_path), exist_ok=True)
            initial_memory = {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "compressed_summaries": [],
                "current_health_state": None
            }
            with open(self.memory_file_path, 'w') as f:
                json.dump(initial_memory, f, indent=2)
    
    def store_compressed_summary(self, compressed_data: Dict[str, Any]) -> bool:
        """
        Store compressed health data summary.
        
        Args:
            compressed_data: Compressed health summary from compression_agent
            
        Returns:
            True if storage successful, False otherwise
        """
        try:
            # Load existing memory
            memory = self.load_memory()
            
            # Update last updated timestamp
            memory["last_updated"] = datetime.now().isoformat()
            
            # Add new compressed summary to history (keep only last 10 for context)
            memory["compressed_summaries"].append({
                "timestamp": compressed_data["compression_timestamp"],
                "budget_mode": compressed_data["budget_mode"],
                "summary": compressed_data["summary"],
                "trends": compressed_data["trends"],
                "retained_fields": compressed_data["retained_fields"],
                "discarded_fields": compressed_data["discarded_fields"]
            })
            
            # Keep only last 10 summaries to prevent unlimited growth
            if len(memory["compressed_summaries"]) > 10:
                memory["compressed_summaries"] = memory["compressed_summaries"][-10:]
            
            # Update current health state (always overwrite)
            memory["current_health_state"] = {
                "last_compression": compressed_data["compression_timestamp"],
                "budget_mode": compressed_data["budget_mode"],
                "trends": compressed_data["trends"],
                "summary": compressed_data["summary"]
            }
            
            # Save to file
            with open(self.memory_file_path, 'w') as f:
                json.dump(memory, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error storing compressed summary: {e}")
            return False
    
    def load_memory(self) -> Dict[str, Any]:
        """
        Load compressed memory from file.
        
        Returns:
            Memory dictionary with compressed summaries and current state
        """
        try:
            with open(self.memory_file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading memory: {e}")
            # Return default memory structure
            return {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "compressed_summaries": [],
                "current_health_state": None
            }
    
    def get_current_health_state(self) -> Optional[Dict[str, Any]]:
        """
        Get the most recent compressed health state.
        
        Returns:
            Current health state or None if no data exists
        """
        memory = self.load_memory()
        return memory.get("current_health_state")
    
    def get_historical_summaries(self, limit: int = 5) -> list:
        """
        Get recent compressed summaries for trend analysis.
        
        Args:
            limit: Maximum number of historical summaries to return
            
        Returns:
            List of recent compressed summaries
        """
        memory = self.load_memory()
        summaries = memory.get("compressed_summaries", [])
        return summaries[-limit:] if summaries else []
    
    def clear_memory(self) -> bool:
        """
        Clear all compressed memory (for testing/reset purposes).
        
        Returns:
            True if clearing successful, False otherwise
        """
        try:
            initial_memory = {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "compressed_summaries": [],
                "current_health_state": None
            }
            with open(self.memory_file_path, 'w') as f:
                json.dump(initial_memory, f, indent=2)
            return True
        except Exception as e:
            print(f"Error clearing memory: {e}")
            return False
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about stored memory.
        
        Returns:
            Dictionary with memory statistics
        """
        memory = self.load_memory()
        return {
            "total_summaries_stored": len(memory.get("compressed_summaries", [])),
            "last_updated": memory.get("last_updated"),
            "has_current_state": memory.get("current_health_state") is not None,
            "file_size_bytes": os.path.getsize(self.memory_file_path) if os.path.exists(self.memory_file_path) else 0
        }
