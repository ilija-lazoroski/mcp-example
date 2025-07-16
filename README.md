# MCP Assistant

This project is an Personal Assistant PoC while learning about MCP (Model Context Protocol).

It uses a local LLM (Gamma-2-2b-it) and execute commands on the host system.


## Requirements

- Install [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Download Gamma model from [Hugging Face](https://huggingface.co/bartowski/gemma-2-2b-it-GGUF/blob/main/gemma-2-2b-it-Q4_K_M.gguf)
  and place it under `./mcp_example/models/` directory.

## Usage

Run the assistant with:

```bash
uv run mcp_example/clients/simple_client.py
```

## Setting up a development environment

### Install dependencies

The following commands will install prerequisites, dependencies, and configure
pre-commit hooks.

```sh
$ uv venv  # Create a virtual environment
$ pre-commit install -t pre-commit -t prepare-commit-msg
