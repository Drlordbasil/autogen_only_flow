# AI Development Platform

A production-ready website and backend system for managing, running, and testing Python/Java AI-based LLM tools and agent workflows.

## Features

- Python and Java code execution with autogen integration
- Workflow management system
- Live code updates
- Automated testing and CI/CD pipeline
- Modern, responsive UI

## Setup

1. Install Python 3.12
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the server:
```bash
python main.py
```

The application will be available at `http://localhost:8000`

## Project Structure

```
.
├── main.py              # FastAPI backend
├── templates/           # HTML templates
│   └── index.html      
├── static/             # Static assets
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── main.js
├── tests/              # Test files
│   └── test_main.py
└── .github/            # GitHub Actions
    └── workflows/
        └── ci.yml
```

## API Endpoints

- `GET /`: Main application interface
- `POST /run_python_tool`: Execute Python code
- `POST /run_java_tool`: Execute Java code
- `GET /list_workflows`: Get available workflows
- `POST /execute_workflow/{workflow_id}`: Run a specific workflow
- `POST /update_code`: Update code files

## Testing

Run tests with:
```bash
pytest tests/
```

## Adding New Features

### New Tools
1. Add new endpoint in `main.py`
2. Create corresponding UI in `templates/index.html`
3. Add JavaScript handlers in `static/js/main.js`
4. Write tests in `tests/test_main.py`

### New Workflows
1. Add workflow definition in `main.py`
2. Update `list_workflows` endpoint
3. Implement workflow logic
4. Add tests

## CI/CD

The project uses GitHub Actions for continuous integration:
- Runs on every push to main and pull requests
- Executes test suite
- Generates coverage reports
- Fails if tests fail or coverage drops

## License

MIT
