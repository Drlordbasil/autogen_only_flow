import pytest
from fastapi.testclient import TestClient
from main import app, AutogenWorkflow

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

def test_run_python_tool():
    response = client.post(
        "/run_python_tool",
        json={"code": "print('hello world')", "language": "python"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "running"

def test_run_java_tool():
    response = client.post(
        "/run_java_tool",
        json={"code": "System.out.println('hello world');", "language": "java"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "running"

def test_list_workflows():
    response = client.get("/list_workflows")
    assert response.status_code == 200
    workflows = response.json()
    assert isinstance(workflows, list)

def test_execute_workflow():
    response = client.post(
        "/execute_workflow/python_analysis",
        json={}
    )
    assert response.status_code == 404

def test_execute_workflow_not_found():
    response = client.post(
        "/execute_workflow/nonexistent",
        json={}
    )
    assert response.status_code == 404

def test_update_code():
    response = client.post(
        "/update_code",
        json={
            "file_path": "test.py",
            "code": "print('test')"
        }
    )
    assert response.status_code == 404  # File doesn't exist

def test_update_code_missing_params():
    response = client.post(
        "/update_code",
        json={}
    )
    assert response.status_code == 400

def test_autogen_workflow():
    workflow = AutogenWorkflow()
    result = workflow.execute_task("Print hello world")
    assert result is not None
    assert hasattr(result, "chat_history")
    assert hasattr(result, "summary")

def test_autogen_analyze_data():
    workflow = AutogenWorkflow()
    result = workflow.analyze_data("test_data.csv", "Analyze this data")
    assert result is not None
    assert hasattr(result, "chat_history")
    assert hasattr(result, "summary")
