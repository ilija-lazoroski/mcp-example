from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Local Agent Helper")

@mcp.tool()
def ls(path: str) -> str:
    "List the contents of a directory."
    import os
    return "\n".join(os.listdir(path))


@mcp.tool()
def cat(path: str) -> str:
    "Read the contents of a file."
    try:
        with open(path, "r") as f:
            return f.read()
    except:
        return ""


@mcp.tool()
def echo(message: str, file: str) -> str:
    "Write text to a file."
    try:
        with open(file, "w") as f:
            f.write(message)
            return "success"
    except:
        return "failed"
