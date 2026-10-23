from pydantic import BaseModel, Field


class AgentTaskRequest(BaseModel):
    task: str = Field(..., min_length=1, max_length=4000)
    max_steps: int = Field(4, ge=1, le=6)


class ToolStep(BaseModel):
    step: int
    tool: str
    arguments: dict = Field(default_factory=dict)
    observation_preview: str = ""
    error: str | None = None


class AgentTaskResponse(BaseModel):
    answer: str
    steps: int
    truncated: bool = False
    trace: list[ToolStep] = Field(default_factory=list)


class ToolResult(BaseModel):
    tool: str
    result: str