from llama_cpp import Llama

llm = Llama(model_path="models/phi-2.Q4_K_M.gguf", n_ctx=2048, verbose=False)


import subprocess

server = subprocess.Popen(
    ['uv', 'run', 'mcp', 'run', 'server.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    stdin=subprocess.PIPE,
    text=True,
)

import json
def create_message(method_name, params, id = None):
    message = {
        "jsonrpc": "2.0",
        "method": method_name,
        "params": params,
        "id": id
    }
    return json.dumps(message)

def send_message(message):
    server.stdin.write(message + "\n")
    server.stdin.flush()

def receive_message():
    print(server.stdout.readline())
    server_output = json.loads(server.stdout.readline())
    if "result" in server_output:
        return server_output["result"]
    else:
        return "Error"


id = 1
init_message = create_message(
    "initialize",
    {
        "clientInfo": {
            "name": "Llama Agent",
            "version": "0.1"
        },
        "protocolVersion": "2024-11-05",
        "capabilities": {},
    },
    id
)

send_message(init_message)
print(server.stdout.readline())  # Read the server's response to the initialization request
response = receive_message()
server_name = response["serverInfo"]["name"]
print("Initializing  " + server_name + "...")

init_complete_message = create_message("notifications/initialized", {})
send_message(init_complete_message)
print("Initialization complete.")
