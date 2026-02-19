"""
Session logging system for tracking all development prompts and actions.
This helps recover from crashes and understand development history.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class SessionLogger:
    """Logs all user prompts and actions taken during development."""

    def __init__(self, log_dir: str = "Logs/sessions"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Create new session file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_file = self.log_dir / f"session_{timestamp}.log"
        self.session_data = {
            "session_start": datetime.now().isoformat(),
            "entries": []
        }

        self._write_header()

    def _write_header(self):
        """Write session header."""
        with open(self.session_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("MY KINGDOM - DEVELOPMENT SESSION LOG\n")
            f.write(f"Session Started: {self.session_data['session_start']}\n")
            f.write("=" * 80 + "\n\n")

    def log_prompt(self, prompt: str):
        """Log a user prompt."""
        timestamp = datetime.now().isoformat()
        entry = {
            "type": "prompt",
            "timestamp": timestamp,
            "content": prompt
        }
        self.session_data["entries"].append(entry)

        with open(self.session_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"[{timestamp}] USER PROMPT:\n")
            f.write(f"{'-'*80}\n")
            f.write(f"{prompt}\n")

    def log_action(self, action_type: str, description: str, details: Dict[str, Any] = None):
        """
        Log an action taken.

        Args:
            action_type: Type of action (e.g., "file_edit", "file_create", "bash_command", "analysis")
            description: Human-readable description
            details: Additional details about the action
        """
        timestamp = datetime.now().isoformat()
        entry = {
            "type": "action",
            "action_type": action_type,
            "timestamp": timestamp,
            "description": description,
            "details": details or {}
        }
        self.session_data["entries"].append(entry)

        with open(self.session_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp}] ACTION - {action_type.upper()}:\n")
            f.write(f"  Description: {description}\n")
            if details:
                f.write(f"  Details: {json.dumps(details, indent=2)}\n")

    def log_step(self, step_number: int, description: str):
        """Log a step in a multi-step process."""
        timestamp = datetime.now().isoformat()
        entry = {
            "type": "step",
            "step_number": step_number,
            "timestamp": timestamp,
            "description": description
        }
        self.session_data["entries"].append(entry)

        with open(self.session_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp}] STEP {step_number}: {description}\n")

    def log_completion(self, summary: str):
        """Log task completion."""
        timestamp = datetime.now().isoformat()
        entry = {
            "type": "completion",
            "timestamp": timestamp,
            "summary": summary
        }
        self.session_data["entries"].append(entry)

        with open(self.session_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp}] ✓ COMPLETED:\n")
            f.write(f"  {summary}\n")

    def log_error(self, error: str, traceback: str = None):
        """Log an error."""
        timestamp = datetime.now().isoformat()
        entry = {
            "type": "error",
            "timestamp": timestamp,
            "error": error,
            "traceback": traceback
        }
        self.session_data["entries"].append(entry)

        with open(self.session_file, 'a', encoding='utf-8') as f:
            f.write(f"\n[{timestamp}] ✗ ERROR:\n")
            f.write(f"  {error}\n")
            if traceback:
                f.write(f"  Traceback:\n{traceback}\n")

    def end_session(self):
        """End the session and write summary."""
        self.session_data["session_end"] = datetime.now().isoformat()

        with open(self.session_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*80}\n")
            f.write(f"SESSION ENDED: {self.session_data['session_end']}\n")
            f.write(f"Total Entries: {len(self.session_data['entries'])}\n")
            f.write(f"{'='*80}\n")

        # Also save JSON version for programmatic access
        json_file = self.session_file.with_suffix('.json')
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.session_data, f, indent=2)

    @staticmethod
    def get_latest_session(log_dir: str = "Logs/sessions") -> Path:
        """Get the most recent session log file."""
        log_path = Path(log_dir)
        if not log_path.exists():
            return None

        log_files = sorted(log_path.glob("session_*.log"), reverse=True)
        return log_files[0] if log_files else None

    @staticmethod
    def read_session(session_file: Path) -> Dict[str, Any]:
        """Read a session from JSON file."""
        json_file = session_file.with_suffix('.json')
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None


# Global session logger instance
_session_logger = None


def get_session_logger() -> SessionLogger:
    """Get or create the global session logger."""
    global _session_logger
    if _session_logger is None:
        _session_logger = SessionLogger()
    return _session_logger


def log_prompt(prompt: str):
    """Convenience function to log a prompt."""
    get_session_logger().log_prompt(prompt)


def log_action(action_type: str, description: str, details: Dict[str, Any] = None):
    """Convenience function to log an action."""
    get_session_logger().log_action(action_type, description, details)


def log_step(step_number: int, description: str):
    """Convenience function to log a step."""
    get_session_logger().log_step(step_number, description)


def log_completion(summary: str):
    """Convenience function to log completion."""
    get_session_logger().log_completion(summary)


def log_error(error: str, traceback: str = None):
    """Convenience function to log an error."""
    get_session_logger().log_error(error, traceback)
