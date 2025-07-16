import asyncio
import os
import json

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import PromptReference, ResourceTemplateReference

from llama_cpp import Llama

llm = Llama(model_path="mcp_example/models/gemma-2-2b-it-Q4_K_M.gguf", n_ctx=2048, verbose=False)

# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command="uv",  # Using uv to run the server
    args=["run", "server", "server", "stdio"],  # Server with completion support
    env={"UV_INDEX": os.environ.get("UV_INDEX", "")},
)

import re
import json

def extract_json(text: str) -> dict:
    """
    Extract JSON from LLM output that may be wrapped in code blocks like
    ```json ... ```, ```tool_code ... ```, or have extra whitespace.
    """
    text = text.strip()

    # Match triple-backtick block (optionally with a label)
    code_block_pattern = re.compile(r"```(?:\w+)?\s*(.*?)\s*```", re.DOTALL)
    match = code_block_pattern.search(text)
    if match:
        text = match.group(1).strip()  # Extract inner JSON string

    # Try parsing JSON
    return json.loads(text)


async def run():
    """Run the completion client example."""
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()

            objects = await session.list_tools()

            print("\n🔧 Available tools:")
            tools = ""
            for obj in objects.tools:
                print(f"- {obj.name}: {obj.description} {obj}")
                tools += f"- {obj.name}: {obj.description} input schema: {obj.inputSchema}\n"

            history = ""
            while True:
                user_input = input("\nYou: ")

                # Build the context for the LLM
                prompt = f"""You are a helpful assistant that can execute shell-like tools to answer questions.

                Available tools:
                {tools}

                Instructions:
                - If a tool is needed, respond ONLY with similar to this:
                  {{"tool": "<tool_name>", "input": {{ ... }}}}
                - If no tool is needed, respond with a helpful message.

                ### Examples

                User: Show me the files in /home/user
                Assistant: {{"tool": "ls", "input": {{"path": "/home/user"}}}}

                User: What does README.md contain?
                Assistant: {{"tool": "cat", "input": {{"path": "README.md"}}}}

                User: echo hello world
                Assistant: {{"tool": "echo", "input": {{"message": "hello world", "file": "output.txt"}}}}

                User: What tools can you run?
                Assistant: {{"tool": "ls", "input": {{"path": "."}}}}

                Now it's your turn.

                User: {user_input}
                Assistant:
                """

                response = llm(prompt, max_tokens=512)
                output = response["choices"][0]["text"].strip()

                print(f"\nAssistant: {output}")

                # Try parsing a tool call
                try:
                    tool_call = extract_json(output)
                    tool_name = tool_call["tool"]
                    tool_input = tool_call["input"]

                    print(f"\n🔧 Calling tool '{tool_name}' with input: {tool_input}")
                    result = await session.call_tool(tool_name, tool_input)
                    result = result.content[0].text.strip()

                    # Re-invoke the LLM with the tool result
                    followup_prompt = f"""The user asked: {user_input}

                    You called the tool '{tool_name}' and got this result:
                    {result}

                    Now reply to the user what you found out from the tool and nothing else!"""
                    final = llm(followup_prompt, max_tokens=512)
                    print(f"\n🤖 LLM: {final['choices'][0]['text'].strip()}")

                except json.JSONDecodeError:
                    print("\n❗ No tool call detected, responding directly.")
                except Exception as e:
                    print(f"\n❌ Error calling tool: {e}")


def main():
    """Entry point for the completion client."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
