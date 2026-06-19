# Email Generation Assistant

FastAPI + Gradio prototype that generates professional emails from three inputs:
intent, key facts, and tone.

### System Requirements

- **Python**: 3.9 or higher
- **Git**: for cloning the repository
- **OpenAI API Key**: sign up at [https://platform.openai.com](https://platform.openai.com)
---

## Installation

## Clone the Repository**

```cmd
git clone https://github.com/TanmoyShome/Email-Generation-Assistant.git
cd Email-Generation-Assistant
```

### Windows

#### Option A: Using venv (Built-in Python)

**Step 1: Create a Virtual Environment**

```cmd
python -m venv venv
venv\Scripts\activate
```
**Step 2: Install Dependencies**

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

#### Option B: Using UV (Faster Alternative)

**Step 1: Install UV** (if not already installed)

```cmd
pip install uv
```

**Step 2: Create Virtual Environment with UV**

```cmd
uv venv venv
venv\Scripts\activate
```

**Step 3: Install Dependencies with UV**

```cmd
uv pip install -r requirements.txt
```
---

### macOS

#### Option A: Using venv (Built-in Python)

**Step 1: Create a Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Step 2: Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Option B: Using UV (Faster Alternative)

**Step 1: Install UV** (if not already installed)

```bash
pip install uv
```

Or use Homebrew:

```bash
brew install uv
```

**Step 2: Create Virtual Environment with UV**

```bash
uv venv venv
source venv/bin/activate
```

**Step 3: Install Dependencies with UV**

```bash
uv pip install -r requirements.txt
```

---

### Linux

#### Option A: Using venv (Built-in Python)

**Step 2: Create a Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Step 3: Install Dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Option B: Using UV (Faster Alternative)

**Step 1: Install UV** (if not already installed)

```bash
pip install uv
```

Or for system-wide installation:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Step 3: Create Virtual Environment with UV**

```bash
uv venv venv
source venv/bin/activate
```

**Step 4: Install Dependencies with UV**

```bash
uv pip install -r requirements.txt
```

## Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
nano .env
```

Or use your preferred editor to add:

```
OPENAI_API_KEY=your_api_key_here
```


## Running the Application

### Activate Virtual Environment (if not already active)

**Windows:**
```cmd
venv\Scripts\activate
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### Start the Server

**Windows / macOS / Linux:**
```bash
uvicorn app.main:app --reload
```

You should see output like:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Access the Application

- **Gradio Web UI**: http://127.0.0.1:8000/gradio
- **API Documentation (Swagger)**: http://127.0.0.1:8000/docs
- **API Docs (ReDoc)**: http://127.0.0.1:8000/redoc

### Docker Quick Start

```bash
docker compose up --build
```

Gradio will be available at `http://localhost:8000/gradio`.

---

## Project Structure

```
EmailGeneraton/
├── app/
│   ├── main.py               # FastAPI app entry point
│   ├── api/
│   │   ├── dependencies.py   # Service dependencies
│   │   └── v1/
│   │       ├── routes/       # API route handlers
│   │       └── api.py        # API router
│   ├── config/
│   │   └── settings.py       # Configuration settings
│   ├── data/
│   │   └── prompt_templates/ # Prompt templates
│   ├── src/
│   │   ├── evaluator.py      # Email evaluation logic
│   │   ├── llm_client.py     # OpenAI client
│   │   ├── prompt_engine.py  # Prompt builder
│   │   └── ...
│   └── ...
├── tests/                     # Test cases
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
└── README.md                 # This file
```

---

## License

This project is licensed under the MIT License. See `LICENSE` for details.
