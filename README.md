# SmartLogistics AI

A beginner-friendly Python project demonstrating logistics pricing, workflow automation, REST APIs, retrieval-augmented generation (RAG), and multi-agent coordination.

## Project Overview

SmartLogistics AI is a learning prototype for a logistics company operating in Tanzania. It demonstrates how software automation and AI-related techniques can support delivery operations.

The project is divided into five stages:

1. **Foundations:** Calculate estimated delivery prices.
2. **Automation:** Validate orders, save shipment records, and check overdue deliveries.
3. **Real-World Systems:** Expose shipment operations through a FastAPI REST API backed by SQLite.
4. **RAG Systems:** Retrieve relevant passages from company-policy documents.
5. **Multi-Agent Systems:** Coordinate specialized order, pricing, tracking, and support agents.

## Technologies

- Python
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite
- Pydantic
- scikit-learn
- pytest

## Requirements

- Python 3.10 or newer
- Visual Studio Code or another Python editor
- Internet access for installing packages

The core application runs locally after dependencies are installed. The initial RAG and multi-agent implementations do not require an LLM API key.

## Folder Structure

```text
smartlogistics-ai/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── shared/
├── tests/
├── prompts/
├── stage1_foundations/
├── stage2_automation/
├── stage3_systems/
├── stage4_rag/
└── stage5_agents/
```

Each stage has its own responsibility. The `shared/` folder contains reusable project utilities, `tests/` contains automated checks, and `prompts/` stores instructions for future LLM integrations.

## Installation

### 1. Open the project folder

Open the `smartlogistics-ai` root folder in VS Code.

Open the integrated terminal. All commands below should be run from the project root unless otherwise stated.

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
```

Activate it in Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Or in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

If you have not yet added all required packages to `requirements.txt`, install them with:

```bash
python -m pip install fastapi "uvicorn[standard]" sqlalchemy scikit-learn pytest httpx
```

## Running the Project

### Stage 1: Pricing

Run the Stage 1 script from its folder:

```bash
cd stage1_foundations
python main.py
```

Return to the project root before running other stages:

```bash
cd ..
```

### Stage 2: Automation

From the project root:

```bash
python -m stage2_automation.main
```

The program can create shipment records in its JSON file, view saved shipments, update statuses, and check overdue deliveries.

### Stage 3: REST API

From the project root:

```bash
python -m uvicorn stage3_systems.main:app --reload
```

Open the API:

- Home: http://127.0.0.1:8000/
- Interactive API documentation: http://127.0.0.1:8000/docs

The Stage 3 application stores shipments in a SQLite database. The current implementation uses a database file under `stage3_systems/`.

### Stage 4: RAG assistant

From the project root:

```bash
python -m stage4_rag.main
```

Ask questions about the sample company policies in `stage4_rag/documents/company_policy.md`.

The initial implementation uses TF-IDF and cosine similarity to retrieve relevant passages. It does not yet use a generative language model.

### Stage 5: Multi-agent system

From the project root:

```bash
python -m stage5_agents.main
```

Choose from pricing, shipment booking, tracking, and company-policy questions.

The current coordinator uses an explicit menu rather than an LLM that autonomously interprets natural-language requests.

## Running Tests

Install the test dependencies if needed:

```bash
python -m pip install pytest httpx
```

Run all tests from the project root:

```bash
python -m pytest tests -v
```

Run an individual test module:

```bash
python -m pytest tests/test_pricing.py -v
```

```bash
python -m pytest tests/test_shipments.py -v
```

```bash
python -m pytest tests/test_rag.py -v
```

## Sample Pricing

The current demo pricing formula is:

- Base fee: TZS 2,500
- Weight fee: TZS 800 per kilogram
- Distance fee: TZS 5 per kilometre
- Express service multiplier: 1.4

For a 3 kg standard delivery from Dodoma to Dar es Salaam, the sample calculation is:

`2500 + (3 × 800) + (450 × 5) = TZS 7,150`

These values are illustrative development settings, not verified commercial tariffs.

## Configuration

`.env.example` documents intended environment variables. The current application does not automatically load `.env` files, and the Stage 3 database path is not yet controlled by the `DATABASE_URL` variable.

Do not commit real credentials, customer records, or other sensitive information to version control.

## Important Limitations

This is a learning prototype, not a production-ready logistics platform.

Before production deployment:

- Add authentication and role-based authorization.
- Ensure each customer can access only their authorized shipment records.
- Protect personal and business data.
- Add audit logging and robust error handling.
- Make shipment-ID generation safe under concurrent requests.
- Validate policies and commercial pricing with approved company information.
- Add integration tests, backups, monitoring, and deployment configuration.
- Use an LLM and appropriate retrieval architecture only after defining security and evaluation requirements.

The Stage 2 JSON store and Stage 3 SQLite database are separate. Shipment records are not automatically synchronized between them.

## Learning Objectives

After working through the five stages, a learner should understand:

- How to structure a Python project.
- How to validate input and implement business rules.
- How to build a REST API and persist data.
- How document retrieval supports a basic RAG workflow.
- How specialized agents can be coordinated through software.
- How to write and run automated tests.

## License

This is a learning project. Add a license before distributing or using it commercially.