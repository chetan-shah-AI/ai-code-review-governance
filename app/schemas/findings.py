from enum import Enum
from pydantic import BaseModel


class Severity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SourceType(str, Enum):
    DETERMINISTIC = "DETERMINISTIC"
    AI = "AI"
    GOVERNANCE = "GOVERNANCE"


class Finding(BaseModel):
    file_path: str | None = None
    line_number: int | None = None
    severity: Severity
    category: str
    title: str
    description: str
    recommendation: str | None = None
    source_type: SourceType
    tool_name: str | None = None
    confidence: float = 1.0


class ToolResult(BaseModel):
    tool_name: str
    success: bool
    raw_output: str
    findings: list[Finding]