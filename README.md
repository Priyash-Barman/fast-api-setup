# Fast Api Setup

FastAPI backend for Fast Api Setup.

## Quick Start

# Install Poetry
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
# Install dependencies
```bash
poetry install
```
# Method 1: Using Poetry script
```bash
poetry run dev
```
# Method 2: Direct uvicorn
```bash
uvicorn fast_app.main:app --reload --host 0.0.0.0 --port 8000
```


## CREATE MODULE COMMANDS

### Create module

```bash
poetry run create-module module_name
```

### Create module with files

```bash
poetry run create-form-module module_name
```

### create cms module

```bash
poetry run create-cms-module module_name
```