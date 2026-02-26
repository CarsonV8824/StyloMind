# StyloMind

## Requirements

- Python `3.12` or `3.13` (recommended)
- `pip`

Do not use Python `3.14+` for this project yet. spaCy currently relies on `pydantic.v1` behavior that breaks on 3.14 and causes errors like:
`ConfigError: unable to infer type for attribute "REGEX"`.

## Setup (Windows PowerShell)

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -U spacy
python -m spacy download en_core_web_sm
```

If `py` is not available, use your Python 3.13 executable path directly:

```powershell
& "C:\Path\To\Python313\python.exe" -m venv .venv
```

## Run

```powershell
.\.venv\Scripts\Activate.ps1
python learn.py
```

## Common Errors

1. `OSError: [E050] Can't find model 'en_core_web_sm'`
- Install the model in the active venv:
```powershell
python -m spacy download en_core_web_sm
```

2. `pydantic.v1.errors.ConfigError: unable to infer type for attribute "REGEX"`
- Recreate the venv with Python 3.12/3.13 and reinstall dependencies.
