# StyloMind

## About

StyloMind is an app that I made in order to help writers and Myself when Writing papers. First, You Import your paper on the upload page. The app can take .PDF, .TXT, and .DOCX files. Second, you then can compare your papers for simular structure and Style. I use machince learning which finds this percentage for me. Third, I have a stats page which gives you graphs of stats about your paper and stats comparing papers.

## Libarys Used

- Spacy: Used for NLP

- Skilet-Learn: Used for Machine Learning

- Seaborn: Used for the graphs

- PySide6: Used to make the clean Desktop App GUI

- Sqlite3: Used for the database

## Each Page

- Upload: Where user upload and manage thier texts

- Style and Structure: Users compare texts to see how simular they are (Shown in a Percentage)

- One text stats page: Where users can get the stats of one paper

- Two Stats page: Where users can compare two papers and get stats

## Goals of App

I hope the app gives the user feedback and stats about thier paper, making the user being able to get feedback.

## Future Goals

- Make a Website along with the desktop app

- Polish Up comparision for AI Dectetion

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
