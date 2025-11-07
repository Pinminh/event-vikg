# EventViKG

**Note:** This repository is a modification of [robert-mcdermott/ai-knowledge-graph](https://github.com/robert-mcdermott/ai-knowledge-graph) by [Robert McDermott](https://github.com/robert-mcdermott).
We extend it with additional capabilities such as event-centric extraction embedded with temporal and geographic information based on claim-level extraction.

---

## Features  
- Unstructured text → structured graph representation (entities, relationships, events, time, location)  
- Interactive visualization of the resulting graph  
- Supports any LLM compatible API endpoint  
- Configurable graph construction via `config.toml`  

---

## Installation

### Option 1: Using [uv](https://github.com/astral-sh/uv) (Recommended)
1. Install `uv` (see more [here](https://docs.astral.sh/uv/getting-started/installation/#installation-methods)):
	```cmd
	pip install uv
	```
2. To install dependencies, at the project root, run:
	```cmd
	uv sync
	```

### Option 2: Using pip and requirements.txt
1. Ensure Python >= 3.12 is installed.
2. Create python virtual environment and activate it:
    ```cmd
    python -m venv .venv
    .venv/Script/activate
    ```
2. Install dependencies, at the project root, run:
	```cmd
	pip install -r requirements.txt
	```

## API Configuration

Before running the `generate_graph.py`, you must provide your own API key for LLM endpoint.  
We used `gemini-2.0-flash` whose API key can be obtained on [Google AI Studio](https://aistudio.google.com/api-keys).  
Then specify your API key in `config.toml` in the project root.

## Running the Graph Constructor

**Note:** if not using `uv`, you do not need `uv run` in the first part of the following commands.  
To generate a knowledge graph from a text file, e.g. `doc.txt`, use:

```cmd
uv run python generate_graph.py --input doc.txt
```
This will generate all chunks, standardize and resolve all triples at once.  

- The output of each chunk is saved in the `output/` or `cumulative_output/` directories.  
- The standardized and resolved results (aggregated) are generated at the project root in `doc.json` (given your input is `doc.txt`).  
- It and can be visualized with a browser by `doc.html`.  

**Important:** Using free API key usually leads to sudden termination when constructing the graph. Luckily, the chunk results are stored in `output/` or `cumulative_output/`. You should take a look to see the progress of the graph construction (specifically, the most recent `chunk id`). Then you can continue the previous terminated graph construction by passing the next `chunk id` into `generate_graph.py`. For example, if you found out the most recent chunk is `output/doc.chunk-4.json`, to continue graph construction, run:
```cmd
    uv run python generate_graph.py --input doc.txt --next-chunk 5
```

---
For more details, see the code and configuration files in this repository.