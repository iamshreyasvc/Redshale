# ML Pipeline Studio

macOS-first **desktop app** for building **no-code** ML pipelines as a **node graph**: dataset → preprocess → train (PyTorch or TensorFlow) → evaluate → quality gate → export.

## Features (v1)

- Visual editor ([NodeGraphQt](https://github.com/jchanvfx/NodeGraphQt)) with inspectors for node parameters.
- Pipeline saved as JSON (`PipelineDocument`: nodes, edges, settings).
- Executors for **image folders** (class subdirectories) and **numeric CSV** (last column = label).
- Training backends: **PyTorch** and **TensorFlow** (install optional `ml` extra).
- Export: **PyTorch** `.pt`, **ONNX** (PyTorch path), **TensorFlow SavedModel** copy.

## Requirements

- **Python 3.9+** (3.10+ recommended for upstream ML wheels).
- GUI dependencies install with the package: PySide6, NodeGraphQt, pydantic, numpy, pandas, joblib.

## Install (development)

```bash
cd ml-pipeline-studio
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -U pip
pip install -e ".[dev]"
```

Install ML frameworks when you want to **run** training (heavy):

```bash
pip install -e ".[ml]"
```

## Run the app

```bash
python -m ml_pipeline_studio
# or
ml-pipeline-studio
```

Use **Template → PyTorch image classification** to load a wired graph, set **Dataset → data_path** to an [ImageFolder](https://pytorch.org/vision/stable/generated/torchvision.datasets.ImageFolder.html)-style directory, then **Run → Run pipeline**.

## New GitHub repository

This tree is intended to be the root of a **dedicated repo** (not nested in a static site). Initialize and push:

```bash
git init
git add .
git commit -m "Initial ML Pipeline Studio scaffold"
git remote add origin https://github.com/<you>/ml-pipeline-studio.git
git push -u origin main
```

## Tests

```bash
pytest
ruff check src tests
```

## Packaging a macOS `.app` (phase 2)

Bundling PySide6 + optional torch/tensorflow is non-trivial. Options:

- [PyInstaller](https://pyinstaller.org/) with a spec that collects Qt and your `ml` deps.
- [Briefcase](https://briefcase.readthedocs.io/) (BeeWare) for a structured macOS app.

Notarization requires an Apple Developer ID; distribute unsigned builds for local use only.

## License

MIT
# Redshale
