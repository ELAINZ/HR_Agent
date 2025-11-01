from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class UserTurn:
    query: str
    context: Optional[Dict[str, Any]] = None

@dataclass
class RoutePlan:
    tool: str
    params: Dict[str, Any]
    reason: str

@dataclass
class ExecutionTrace:
    request: Dict[str, Any]
    response: Dict[str, Any]
    latency_ms: float

@dataclass
class EvalRecord:
    case_id: str
    pass_: bool
    scores: Dict[str, float]
    reason: str
