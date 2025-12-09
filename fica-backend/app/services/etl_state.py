from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ETLStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class ETLStateManager:
    """Singleton to manage ETL process state"""
    _instance = None
    _state: Dict[str, Any] = {
        "status": ETLStatus.IDLE,
        "currentStep": 0,
        "startTime": None,
        "endTime": None,
        "error": None,
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_state(self) -> Dict[str, Any]:
        """Get current ETL state"""
        return self._state.copy()

    def start_process(self):
        """Mark ETL process as started"""
        self._state = {
            "status": ETLStatus.RUNNING,
            "currentStep": 1,
            "startTime": datetime.now().isoformat(),
            "endTime": None,
            "error": None,
        }

    def update_step(self, step: int):
        """Update current step"""
        if self._state["status"] == ETLStatus.RUNNING:
            self._state["currentStep"] = step

    def complete_process(self):
        """Mark ETL process as completed"""
        self._state["status"] = ETLStatus.COMPLETED
        self._state["currentStep"] = 5
        self._state["endTime"] = datetime.now().isoformat()

    def fail_process(self, error_message: str):
        """Mark ETL process as failed"""
        self._state["status"] = ETLStatus.FAILED
        self._state["endTime"] = datetime.now().isoformat()
        self._state["error"] = error_message

    def reset(self):
        """Reset to idle state"""
        self._state = {
            "status": ETLStatus.IDLE,
            "currentStep": 0,
            "startTime": None,
            "endTime": None,
            "error": None,
        }

# Global instance
etl_state_manager = ETLStateManager()

