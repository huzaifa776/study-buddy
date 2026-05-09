---
title: Study Buddy AI
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: gradio
app_file: app.py
pinned: false
---

# Study Buddy AI

Study Buddy AI is an interactive Gradio application that generates quizzes using a Groq-hosted LLM and grades user answers instantly. It is designed for fast self-testing with configurable topic, difficulty, and question format.

The app currently supports:
- Multiple Choice questions
- Fill in the Blank questions


Generated quizzes can be evaluated in-app and exported as CSV for later review.

## Features

- Generate 1 to 10 questions per quiz
- Choose question format:
	- Multiple Choice
	- Fill in the Blank
- Choose difficulty:
	- Easy
	- Medium
	- Hard
- Instant scoring summary after submission
- Detailed results table per question
- Export results to timestamped CSV files
- Automatic log file generation under `logs/`

## Tech Stack

- Python
- Gradio (web UI)
- Pandas (results handling)
- LangChain core parsers/prompts
- `langchain-groq` for Groq model calls
- Pydantic for structured output parsing/validation
- `python-dotenv` for environment variable loading

## How It Works

1. User configures quiz settings in the UI.
2. App creates a `QuestionGenerator` backed by Groq.
3. Prompt templates request strict JSON output from the model.
4. Responses are parsed into Pydantic schemas.
5. Questions are stored in a `QuizManager` state object.
6. User answers are submitted and evaluated.
7. Results are shown in a table and can be exported to CSV.

## Project Structure

```text
.
├── app.py                          # Gradio app entrypoint and event wiring
├── requirements.txt               # Python dependencies
├── setup.py                       # Packaging metadata
├── assets/
│   └── style.css                  # Custom UI styling
├── logs/                          # Runtime log files (created/updated automatically)
└── src/
		├── common/
		│   ├── custom_exception.py    # Detailed exception wrapper
		│   └── logger.py              # App-wide logger setup
		├── config/
		│   └── settings.py            # Environment-driven configuration
		├── generator/
		│   └── question_generator.py  # LLM generation + parsing + retries
		├── llm/
		│   └── groq_client.py         # Groq client factory
		├── models/
		│   └── question_schemas.py    # Pydantic output schemas
		├── prompt/
		│   └── templates.py           # Prompt templates for each question type
		└── utils/
				└── helpers.py             # QuizManager (state, evaluate, export)
```

## Prerequisites

- Python 3.10+
- `pip`
- Groq API key (required)

## Installation

1. Clone the repository and enter it:

```bash
git clone <your-repo-url>
cd "study buddy"
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

Optional editable install:

```bash
pip install -e .
```

## Environment Variables

Create a `.env` file in the project root:

```env
# Required for Groq model
GROQ_API_KEY=your_groq_api_key_here
```

Current defaults from code:
- Groq model: `groq/compound`
- Temperature: `0.9`
- Max retries per generation: `3`

If you want to change the model later, update `MODEL_NAME` in [src/config/settings.py]. The app reads that value in [src/llm/groq_client.py].

## Running the App

From project root:

```bash
python3 app.py
```

Gradio will print a local URL in the terminal (typically `http://127.0.0.1:7860`). Open it in your browser.

## Usage Guide

1. In Step 1, set:
	 - Topic
	 - Question format
	 - Difficulty
	 - Number of questions
2. Click `Generate Quiz`.
3. Answer questions in Step 2.
4. Click `Submit Answers`.
5. Review score and per-question results in Step 3.
6. Click `Save Results` to download a CSV.

## Output Files

- Logs:
	- Folder: `logs/`
	- File pattern: `log_YYYY-MM-DD.log`

- Result exports:
	- Folder: `results/` (created at runtime)
	- File pattern: `quiz_results_YYYYMMDD_HHMMSS.csv`

Result CSV columns:
- `question_number`
- `question`
- `question_type`
- `user_answer`
- `correct_answer`
- `is_correct`
- `options` (empty list for fill-in-the-blank)

## Error Handling and Reliability

- Generation retries up to `MAX_RETRIES` when parsing or model calls fail.
- Model output is validated through Pydantic schemas.
- MCQ integrity check ensures:
	- Exactly 4 options
	- `correct_answer` is one of those options
- Fill-in-the-blank check ensures placeholder is present in the generated question.
- Exceptions are wrapped with file and line context using `CustomException`.

## Troubleshooting

### App exits immediately when running `python3 app.py`

Check these first:
- Virtual environment is active
- Dependencies are installed from `requirements.txt`
- `.env` exists and includes the required API key for your selected model

Quick checks:

```bash
python3 -m pip show gradio pandas langchain langchain-groq python-dotenv
```

### Quiz generation fails in the UI

- Verify network access
- Verify API keys are valid and not expired
- Inspect the latest file in `logs/` for parser or provider errors

### Save Results does nothing

The app only saves after successful quiz evaluation. Generate a quiz, submit answers, then click save.

## Development Notes

- Main UI and event handlers are in `app.py`.
- If adding new question formats, update:
	- Prompt template(s)
	- Pydantic schema(s)
	- `QuestionGenerator`
	- `QuizManager.evaluate_quiz`
	- UI rendering/inputs in `app.py`

## Security Notes

- Do not commit `.env` files or API keys.
- Rotate keys if exposed.
- Prefer provider-side quotas/rate limits for cost control.


