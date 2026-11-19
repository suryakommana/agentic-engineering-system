from typing import Any, Literal
from pydantic import BaseModel, Field

Scenario = Literal["greenfield", "brownfield", "ambiguous"]

class WorkflowRequest(BaseModel):
    requirement: str = Field(min_length=10)
    scenario: Scenario = "greenfield"
    repository_path: str | None = None
    inject_failure_once: bool = False
