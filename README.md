# AI Development Platform

A production-ready website and backend system for managing, running, and testing Python/Java AI-based LLM tools and agent workflows. Uses local LLM (Ollama) for enhanced privacy and performance.

## Features

- Python and Java code execution with autogen integration
- Local LLM integration via Ollama
- Docker-based secure code execution
- Workflow management system
- Live code updates and analysis
- Automated testing and CI/CD pipeline
- Modern, responsive UI
- Codebase analysis tools
- Test improvement automation

## Requirements

- Python 3.12
- Docker
- Ollama with llama3.1:8b model
- Modern web browser

## Setup

1. Install Python 3.12
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install and start Ollama:
- Follow instructions at [Ollama](https://ollama.ai)
- Pull the llama3.1:8b model:
```bash
ollama pull llama3.1:8b
```

4. Run the server:
```bash
python main.py
```

The application will be available at `http://localhost:8000`

## Project Structure

```
.
├── main.py              # FastAPI backend
├── agents/             # AI agent implementations
│   ├── team_manager.py
│   ├── debug_team.py
│   └── research_team.py
├── templates/           # HTML templates
│   ├── index.html      
│   ├── python_tool.html
│   └── java_tool.html
├── static/             # Static assets
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── main.js
│       ├── python_tool.js
│       └── java_tool.js
├── tests/              # Test files
│   └── test_teams.py
└── .github/            # GitHub Actions
    └── workflows/
        └── ci.yml
```

## API Endpoints

### Code Execution
- `GET /`: Main application interface
- `POST /run_python_tool`: Execute Python code
- `POST /run_java_tool`: Execute Java code

### Workflow Management
- `GET /list_workflows`: Get available workflows
- `POST /execute_workflow/{workflow_id}`: Run a specific workflow
- `POST /update_code`: Update code files

### Analysis Tools
- `POST /analyze_codebase`: Analyze existing codebase
- `POST /solve_problem`: Get solutions for coding problems
- `POST /improve_tests`: Generate and improve tests

## Agent System

The platform uses a multi-agent system powered by Autogen:

1. Assistant Agent
- Generates robust Python code
- Provides fully finished MVPs
- Terminates conversations appropriately

2. User Proxy Agent
- Executes code in Docker environment
- Provides feedback
- Manages conversation flow

3. Team Manager
- Coordinates research and debug teams
- Manages complex workflows
- Handles async operations

## Testing

Run tests with:
```bash
pytest tests/
```

## Development

### Adding New Features
1. Add new endpoint in `main.py`
2. Create corresponding UI in `templates/`
3. Add JavaScript handlers in `static/js/`
4. Write tests in `tests/`
5. Update agent system messages if needed

### New Workflows
1. Add workflow definition in `main.py`
2. Update `list_workflows` endpoint
3. Implement workflow logic
4. Add tests
5. Create UI components

## CI/CD

GitHub Actions workflow:
- Runs on every push and pull request
- Executes test suite
- Checks code formatting
- Validates agent configurations
- Generates coverage reports

## License

MIT
