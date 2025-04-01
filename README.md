Below is a README file tailored for your GitHub repository based on the official GraphRAG tutorial, incorporating your specific requirements (e.g., modifying `settings.yaml` for CSV input and graph visualization, excluding Azure OpenAI details). It’s structured clearly for your mentor to follow your project’s operational steps.

---

# GraphRAG Project README

This repository contains the documentation and code for a project utilizing the **GraphRAG** system to index and query text data, as well as visualize the resulting knowledge graph. The steps below outline the process from setup to querying and visualization, based on the official GraphRAG documentation.

## Requirements
- **Python**: 3.10–3.12

## Getting Started
To set up and run this project, follow these steps. This guide assumes you’re installing GraphRAG from PyPI and working with a sample dataset.

### Step 1: Install GraphRAG
Install the GraphRAG package via pip:
```bash
pip install graphrag
```

The `graphrag` library provides a CLI for a no-code approach. Refer to the [official CLI documentation](https://github.com/microsoft/graphrag/blob/main/docs/cli.md) for more details.

### Step 2: Prepare the Dataset
Create a directory for your input data:
```bash
mkdir -p ./ragtest/input
```

For this example, download *A Christmas Carol* by Charles Dickens from Project Gutenberg:
```bash
curl https://www.gutenberg.org/cache/epub/24022/pg24022.txt -o ./ragtest/input/book.txt
```

Alternatively, if your input is a CSV file (e.g., with columns like "Source" and "Text"), place it in `./ragtest/input`. The CSV setup is detailed in the configuration section below.

### Step 3: Initialize the Workspace
Initialize the GraphRAG workspace:
```bash
graphrag init --root ./ragtest
```

This creates two files in the `./ragtest` directory:
- `.env`: Contains environment variables (e.g., `GRAPHRAG_API_KEY=<YOUR_OPENAI_API_KEY>`). Update this with your OpenAI API key.
- `settings.yaml`: Pipeline configuration file (see customization details below).

#### Configuring `settings.yaml`
The `settings.yaml` file allows you to customize the pipeline, including the model and input type. Below are key modifications:

- **Model and Parameters**: Adjust the `llm` section to specify your desired model (e.g., `gpt-4`) and parameters (e.g., chunk size). Example:
  ```yaml
  llm:
    model: gpt-4
    max_tokens: 4096
    chunk_size: 800
  ```

- **CSV Input**: If using a CSV file instead of the default `.txt`, update the `input` section. GraphRAG will only read the `text_column` for graph creation:
  ```yaml
  input:
    type: file
    file_type: csv
    base_dir: "input"
    file_encoding: utf-8
    file_pattern: ".*\\.csv$"
    source_column: "Source"
    text_column: "Text"  # Required: GraphRAG processes this column
  ```

- **Graph Visualization**: To enable graph visualization (disabled by default), set:
  ```yaml
  snapshots:
    graphml: true
  ```

Review and modify `settings.yaml` as needed for your project.

### Step 4: Run the Indexing Pipeline
Execute the indexing pipeline:
```bash
graphrag index --root ./ragtest
```

This process may take time depending on your dataset size, model, and chunk size. Once complete, check the `./ragtest/output` folder for generated parquet files and, if enabled, a `merged_graph.graphml` file for visualization.

### Step 5: Query the Indexed Data
Use the query engine to extract insights. Examples:

- **Global Search** (high-level themes):
  ```bash
  graphrag query --root ./ragtest --method global --query "What are the top themes in this story?"
  ```

- **Local Search** (specific details):
  ```bash
  graphrag query --root ./ragtest --method local --query "Who is Scrooge and what are his main relationships?"
  ```

See the [Query Engine documentation](https://github.com/microsoft/graphrag/blob/main/docs/query_engine.md) for more on local vs. global search.

### Step 6: Visualize the Knowledge Graph
To visualize the graph, ensure `snapshots.graphml: true` is set in `settings.yaml` before indexing. Then follow these steps:

1. **Locate the Graph File**: After indexing, find `merged_graph.graphml` in `./ragtest/output`.
2. **Install Gephi**: Download and install [Gephi](https://gephi.org/).
3. **Import the Graph**: Open Gephi, import `merged_graph.graphml`, and view the initial graph.
4. **Enhance Visualization**:
   - Install the **Leiden Algorithm** plugin (Tools > Plugins).
   - Run **Statistics** (Average Degree, Leiden Algorithm with Resolution: 1).
   - Color nodes by clusters (Appearance > Nodes > Partition > Cluster).
   - Resize nodes by degree (Appearance > Nodes > Ranking > Degree, Min: 10, Max: 150).
   - Layout with **OpenORD** (Liquid/Expansion: 50) and **ForceAtlas2** (Scaling: 15, Dissuade Hubs: checked, Prevent Overlap: checked).
   - Add text labels if desired.

The resulting graph will be organized and ready for analysis.

## Project Notes
- This project uses *A Christmas Carol* as a sample dataset. Replace it with your own data in `./ragtest/input`.
- For CSV inputs, ensure your file matches the `source_column` and `text_column` specified in `settings.yaml`.
- Adjust model parameters in `settings.yaml` to optimize performance for your dataset.

## Additional Resources
- [GraphRAG GitHub](https://github.com/microsoft/graphrag)
- [Configuration Documentation](https://github.com/microsoft/graphrag/blob/main/docs/configuration.md)
- [CLI Documentation](https://github.com/microsoft/graphrag/blob/main/docs/cli.md)

---

This README is ready to be placed in your GitHub repository. It’s concise, includes all necessary steps, and reflects your project-specific adjustments (CSV input and graph visualization). Let me know if you’d like to refine it further or add code snippets!
