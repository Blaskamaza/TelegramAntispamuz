"""
Circuit Breaker — Prevents cascade failures when Vertex AI is unavailable.

Pattern: After N failures, circuit "opens" and rejects requests for T seconds.
This prevents hammering a dead service and allows recovery.

Usage:
    cb = CircuitBreaker("vertex_ai")
    
    if cb.is_open():
        raise ServiceUnavailable("Vertex AI circuit breaker is OPEN")
    
    try:
        result = vertex_client.generate(prompt)
        cb.record_success()
    except Exception:
        cb.record_failure()
        raise
"""

import time
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger("CircuitBreaker")


@dataclass
class CircuitState:
    """State of a single circuit breaker."""
    failures: int = 0
    successes: int = 0
    last_failure_time: Optional[float] = None
    opened_at: Optional[float] = None
    
    # Config
    max_failures: int = 5
    timeout_seconds: int = 300  # 5 minutes
    half_open_after: int = 60   # Try again after 1 minute


class CircuitBreaker:
    """
    Thread-safe circuit breaker with three states:
    - CLOSED: Normal operation
    - OPEN: Rejecting all requests
    - HALF_OPEN: Allowing test requests
    """
    
    # Shared state across instances (per service)
    _circuits: Dict[str, CircuitState] = {}
    _lock = threading.Lock()
    
    def __init__(
        self,
        service_name: str,
        max_failures: int = 5,
        timeout_seconds: int = 300
    ):
        self.service_name = service_name
        
        with self._lock:
            if service_name not in self._circuits:
                self._circuits[service_name] = CircuitState(
                    max_failures=max_failures,
                    timeout_seconds=timeout_seconds
                )
    
    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._circuits[self.service_name]
    
    def is_open(self) -> bool:
        """Check if circuit is open (blocking requests)."""
        state = self.state
        
        if state.opened_at is None:
            return False
        
        elapsed = time.time() - state.opened_at
        
        # Check if we should transition to half-open
        if elapsed > state.half_open_after:
            return False  # Allow test request
        
        return True
    
    def is_half_open(self) -> bool:
        """Check if circuit is in half-open state (testing)."""
        state = self.state
        
        if state.opened_at is None:
            return False
        
        elapsed = time.time() - state.opened_at
        return elapsed > state.half_open_after
    
    def record_success(self) -> None:
        """Record a successful request."""
        with self._lock:
            state = self.state
            state.successes += 1
            
            # If in half-open state, close the circuit
            if state.opened_at is not None:
                logger.info(f"✅ Circuit {self.service_name} CLOSED (recovered)")
                state.opened_at = None
                state.failures = 0
    
    def record_failure(self) -> None:
        """Record a failed request."""
        with self._lock:
            state = self.state
            state.failures += 1
            state.last_failure_time = time.time()
            
            # Check if we should open the circuit
            if state.failures >= state.max_failures:
                if state.opened_at is None:
                    state.opened_at = time.time()
                    logger.warning(
                        f"🔴 Circuit {self.service_name} OPENED "
                        f"(failures: {state.failures})"
                    )
    
    def reset(self) -> None:
        """Manually reset the circuit."""
        with self._lock:
            state = self.state
            state.failures = 0
            state.successes = 0
            state.opened_at = None
            state.last_failure_time = None
            logger.info(f"🔄 Circuit {self.service_name} RESET")
    
    def get_status(self) -> Dict:
        """Get circuit status for monitoring."""
        state = self.state
        
        if state.opened_at is None:
            status = "CLOSED"
        elif self.is_half_open():
            status = "HALF_OPEN"
        else:
            status = "OPEN"
        
        return {
            "service": self.service_name,
            "status": status,
            "failures": state.failures,
            "successes": state.successes,
            "last_failure": datetime.fromtimestamp(state.last_failure_time).isoformat() if state.last_failure_time else None,
            "opened_at": datetime.fromtimestamp(state.opened_at).isoformat() if state.opened_at else None,
        }


# === Singleton accessors ===

_vertex_breaker: Optional[CircuitBreaker] = None

def get_vertex_circuit_breaker() -> CircuitBreaker:
    """Get singleton Vertex AI circuit breaker."""
    global _vertex_breaker
    if _vertex_breaker is None:
        _vertex_breaker = CircuitBreaker(
            "vertex_ai",
            max_failures=5,
            timeout_seconds=300
        )
    return _vertex_breaker


# === CLI for testing ===

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Circuit Breaker CLI")
    parser.add_argument("command", choices=["status", "test-fail", "test-success", "reset"])
    parser.add_argument("--service", default="vertex_ai")
    
    args = parser.parse_args()
    cb = CircuitBreaker(args.service)
    
    if args.command == "status":
        import json
        print(json.dumps(cb.get_status(), indent=2))
    
    elif args.command == "test-fail":
        for i in range(6):
            cb.record_failure()
            print(f"Failure {i+1}: is_open={cb.is_open()}")
    
    elif args.command == "test-success":
        cb.record_success()
        print(f"Success recorded: is_open={cb.is_open()}")
    
    elif args.command == "reset":
        cb.reset()
        print("Circuit reset")
