import asyncio

from fastmcp import Client


async def main():
    async with Client("http://localhost:8000/mcp/") as c:
        print("tools:", [t.name for t in await c.list_tools()])
        print("create:", (await c.call_tool("create_todo", {"title": "via-mcp"})).data)
        print("list:  ", (await c.call_tool("list_todos", {})).data)
        print("update:", (await c.call_tool("update_todo", {"todo_id": 1, "title": "updated", "completed": True})).data)
        print("delete:", (await c.call_tool("delete_todo", {"todo_id": 1})).data)


asyncio.run(main())
