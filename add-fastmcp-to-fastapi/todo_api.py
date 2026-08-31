import os
from pathlib import Path as FilePath

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Path, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

load_dotenv(FilePath(__file__).parent / ".env")
API_KEY = os.getenv("API_KEY", "demo-secret-key")

app = FastAPI(title="Todo API", version="1.0.0")

PUBLIC = {"/openapi.json", "/docs", "/redoc", "/health"}


@app.middleware("http")
async def auth(request: Request, call_next):
    if request.url.path in PUBLIC or request.url.path.startswith("/mcp"):
        return await call_next(request)
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    if token != API_KEY:
        return JSONResponse(status_code=401, content={"detail": "Invalid or missing Authorization"})
    return await call_next(request)


class TodoIn(BaseModel):
    title: str = Field(description="Short text of the task to do.")
    completed: bool = Field(default=False, description="Whether the task is done.")


class Todo(TodoIn):
    id: int = Field(description="Unique id assigned to the todo.")


todos: dict[int, Todo] = {}
next_id = 1


@app.post("/api/todos", operation_id="create_todo", response_model=Todo)
async def create_todo(payload: TodoIn) -> Todo:
    """Create a new todo and return it with its generated id."""
    global next_id
    todos[next_id] = Todo(id=next_id, **payload.model_dump())
    next_id += 1
    return todos[next_id - 1]


@app.get("/api/todos", operation_id="list_todos", response_model=list[Todo])
async def list_todos() -> list[Todo]:
    """List all todos."""
    return list(todos.values())


@app.put("/api/todos/{todo_id}", operation_id="update_todo", response_model=Todo)
async def update_todo(
    payload: TodoIn,
    todo_id: int = Path(description="Id of the todo to update."),
) -> Todo:
    """Replace a todo's title and completed state, found by id."""
    if todo_id not in todos:
        raise HTTPException(404, "Todo not found")
    todos[todo_id] = Todo(id=todo_id, **payload.model_dump())
    return todos[todo_id]


@app.delete("/api/todos/{todo_id}", operation_id="delete_todo")
async def delete_todo(
    todo_id: int = Path(description="Id of the todo to delete."),
) -> dict:
    """Delete a todo by id."""
    if todo_id not in todos:
        raise HTTPException(404, "Todo not found")
    del todos[todo_id]
    return {"deleted": todo_id}


@app.get("/health", include_in_schema=False)
async def health() -> dict:
    return {"status": "ok"}
