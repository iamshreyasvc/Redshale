# Redshale

**Redshale** is a desktop application for designing and running **machine-learning pipelines** without writing code. You arrange steps as a **directed graph** on a canvas—dataset loading, preprocessing, training, evaluation, a simple quality gate, and export—and execute the whole flow from the app while watching a **run log** (and an embedded **terminal** tab).

The product is distributed as the Python package `**ml-pipeline-studio`** (`import ml_pipeline_studio`). The UI is built with **PySide6 (Qt)** and **NodeGraphQt** for the node editor.

---

## What you use it for

- **Prototype end-to-end flows** from raw data to a saved model, entirely inside a visual editor.
- **Persist pipelines as JSON** so you can version, share, and reopen graphs (nodes, connections, and run settings).
- **Train small reference models** on **image folders** (folder-per-class layout, similar to PyTorch `ImageFolder`) or **tabular CSV** (features + one label column).
- **Choose PyTorch or TensorFlow** as the training backend, then **evaluate** on a held-out split, **gate** the run on a minimum metric (validate node), and **export** artifacts (PyTorch checkpoint, ONNX from the PyTorch path, or TensorFlow SavedModel directory).

Redshale targets a **macOS-first** experience (including **MPS** device hints for PyTorch when available); Linux and Windows may work with the same stack but are not the primary focus.

---

## How a pipeline works

Each **node** is one step. **Edges** connect output ports to input ports. On **Run pipeline**, the app validates the graph (ports, acyclic order, required wiring) and runs nodes in **topological order**.


| Node kind                        | Role                                                                                                                       |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Dataset**                      | Loads **image folder** or **CSV** data, splits train/val/test by ratio, exposes a `data` output.                           |
| **Preprocess**                   | Image resize / normalization presets, or tabular scaling (needs **scikit-learn** for standardization).                     |
| **Train (PyTorch / TensorFlow)** | Trains a small CNN (images) or MLP-style stack (tabular) from node parameters (epochs, batch size, learning rate, preset). |
| **Evaluate**                     | Scores the trained model on val or test split; outputs **metrics**.                                                        |
| **Validate**                     | Quality gate: fails the run if metrics (e.g. accuracy) are below a threshold.                                              |
| **Export**                       | Writes `**.pt`** / **ONNX** (PyTorch-trained models) or copies **SavedModel** (TensorFlow).                                |


**Global settings** (from **Settings → Run settings…**) control where run artifacts go (`run_output_dir`, default `./ml_runs`), **random seed**, and device hints for PyTorch (`auto`, `cpu`, `mps`, `cuda:0`) and TensorFlow.

---

## User interface (at a glance)

- **Welcome** dialog on launch: new pipeline, open file, or pick from **recent** JSON pipelines.
- **Header bar**: **File** (New / Open / Save), **Template** (e.g. PyTorch image classification starter graph), **Add Node**, **Run** (`Ctrl+R`), **Settings**.
- **Center**: interactive **node graph**.
- **Inspector** dock: edit parameters for the selected node.
- **Bottom**: **Run log** and **Terminal** tabs for output from pipeline execution.

Starter template **PyTorch image classification** wires: Dataset → Preprocess → Train → Evaluate + Validate + Export. Point **Dataset → data_path** at your image root, install ML dependencies, then run.

---

## Requirements

- **Python 3.9+** (3.10+ recommended for prebuilt ML wheels).
- **Base install**: PySide6, NodeGraphQt, pydantic, numpy, pandas, joblib (declared in `pyproject.toml`).

Heavy frameworks are **optional**: install the `**ml`** extra when you want to execute training and export.

---

## Install

Clone the repository and install in editable mode from the repo root:

```bash
git clone https://github.com/iamshreyasvc/Redshale.git
cd Redshale
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e ".[dev]"
```

Install **PyTorch**, **TensorFlow**, and **scikit-learn** for full run support (large download):

```bash
pip install -e ".[ml]"
```

---

## Run the app

```bash
python -m ml_pipeline_studio
```

Or use the console script:

```bash
ml-pipeline-studio
```

---

## Pipeline files

Pipelines are saved as **JSON** (a versioned document: settings, node list with `kind` / `id` / `params` / positions, and edge list). Use **Save As…** to write `*.json` and **Open…** to load them.

**Save location:** **Open** and **Save As…** start in your **Documents/Redshale** folder (created automatically) when you have no file open yet, so pipeline files normally stay **outside** the git repository and are not picked up by Git. After you open a file, dialogs start in that file’s folder. Saving `*.json` in the **repository root** is still discouraged; `.gitignore` ignores root-level `*.json` as a backup. Training/export output defaults to **`ml_runs/`**, which is also ignored.

---

## Development

```bash
pytest
ruff check src tests
```

---

## Packaging a macOS `.app`

Bundling Qt plus optional Torch/TensorFlow into a signed, notarized app is non-trivial. Typical approaches include **PyInstaller** (with explicit data collection for Qt and ML libs) or **Briefcase**. Unsigned local builds are the practical default for experimentation.

---

## License

MIT