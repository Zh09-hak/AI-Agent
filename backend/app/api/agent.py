from fastapi import APIRouter, HTTPException

from backend.app.agent.executor import execute_tool
from backend.app.agent.orchestrator import run_agent
from backend.app.agent.tool_schemas import TOOL_SCHEMAS
from backend.app.agent.tools import TOOL_REGISTRY
from backend.app.schemas.agent import AgentTaskRequest, AgentTaskResponse, ToolResult

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/task", response_model=AgentTaskResponse)
def agent_task(request: AgentTaskRequest) -> AgentTaskResponse:
    task = request.task.strip()
    if not task:
        raise HTTPException(status_code=400, detail="Task cannot be empty")

    try:
        result = run_agent(task, max_steps=request.max_steps)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent failed: {exc}")

    return AgentTaskResponse(**result)


@router.get("/tools")
def get_tools() -> list[dict]:
    return [
        {
            "name": s["function"]["name"],
            "description": s["function"]["description"],
            "parameters": s["function"].get("parameters", {}),
        }
        for s in TOOL_SCHEMAS
    ]


@router.post("/tool/{tool_name}", response_model=ToolResult)
def invoke_tool(tool_name: str, payload: dict) -> ToolResult:
    if tool_name not in TOOL_REGISTRY:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown tool '{tool_name}'. Available: {sorted(TOOL_REGISTRY.keys())}",
        )

    observation, error = execute_tool(tool_name, payload or {})

    if error:
        raise HTTPException(status_code=400, detail=error)

    return ToolResult(tool=tool_name, result=observation)