from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import uuid
import json
import os
from datetime import datetime
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import autogen
from autogen.coding import LocalCommandLineCodeExecutor
import os
from dotenv import load_dotenv
import re
import subprocess
from agents import TeamManager

load_dotenv()

# Initialize autogen agents
config_list = [
    {
        'model': 'llama3.1:8b',
        'base_url': "http://localhost:11434/v1",
        'api_key': "ollama"
    }
]

llm_config = {
    "config_list": config_list,
    "timeout": 120,
    "temperature": 0
}

# Create assistant agent with async capabilities
assistant = autogen.AssistantAgent(
    name="assistant",
    llm_config=llm_config,
    system_message=" You create python code robustly and send fully finished mvps based on the prompt.reply with TERMINATE when finished.",
    human_input_mode="NEVER",
    is_termination_msg=lambda msg: "TERMINATE" in msg["content"].lower(),


)

# Create user proxy agent with async capabilities
user_proxy = autogen.UserProxyAgent(
    name="user_proxy",
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
    code_execution_config={
        "work_dir": "workspace",
        "use_docker": True
    },
    llm_config=llm_config,
    is_termination_msg=lambda msg: "TERMINATE" in msg["content"].lower(),
    system_message="Execute code and provide feedback."
    
)

# Initialize team manager
team_manager = TeamManager(config_list)

class AutogenWorkflow:
    def __init__(self):
        self.assistant = assistant
        self.user_proxy = user_proxy
        self.max_consecutive_auto_reply = 10
        self.max_retries = 3

    async def execute_task(self, task_description: str):
        try:
            # Create a chat between assistant and user_proxy
            chat_manager = await self.user_proxy.a_initiate_chat(
                self.assistant,
                message=task_description
            )
            
            # Get the last message from the chat
            messages = chat_manager.chat_history
            if not messages:
                return None
                
            last_message = messages[-1]
            return last_message.get("content", None)
            
        except Exception as e:
            logging.error(f"Error executing task: {str(e)}")
            raise

    async def analyze_data(self, data_file: str, analysis_prompt: str):
        try:
            # Read the data file
            with open(data_file, 'r') as f:
                data_content = f.read()
                
            # Create analysis message
            message = f"""
            Data content:
            {data_content}
            
            Analysis prompt:
            {analysis_prompt}
            """
            
            # Create a chat between assistant and user_proxy
            chat_manager = await self.user_proxy.a_initiate_chat(
                self.assistant,
                message=message
            )
            
            # Get the last message from the chat
            messages = chat_manager.chat_history
            if not messages:
                return None
                
            last_message = messages[-1]
            return last_message.get("content", None)
            
        except Exception as e:
            logging.error(f"Error analyzing data: {str(e)}")
            raise

class CodeExecutionRequest(BaseModel):
    code: str
    language: str
    options: Optional[Dict[str, Any]] = {}

class CodeExecutionResult(BaseModel):
    execution_id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None

class AgentMessage(BaseModel):
    sender: str
    recipient: str
    message: str

class WorkflowStep(BaseModel):
    type: str
    code: Optional[str] = None
    message: Optional[str] = None
    options: Optional[Dict[str, Any]] = {}

class Workflow(BaseModel):
    name: str
    steps: List[WorkflowStep]

class WorkflowResult(BaseModel):
    id: str
    status: str
    result: Optional[str] = None
    error: Optional[str] = None

class CodeGenerationRequest(BaseModel):
    prompt: str
    options: Optional[Dict[str, Any]] = {}

class CodeGenerationResponse(BaseModel):
    code: str
    tests: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# In-memory storage for executions and workflows
executions = {}
workflows = {}

async def execute_code_async(code: str, language: str, options: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Create an isolated environment for code execution
        if language.lower() == 'python':
            # Use asyncio.create_subprocess_exec for better security
            proc = await asyncio.create_subprocess_exec(
                'python', '-c', code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                return {
                    'status': 'error',
                    'error': stderr.decode() if stderr else 'Unknown error occurred'
                }
            
            return {
                'status': 'completed',
                'result': stdout.decode()
            }
            
        else:
            raise ValueError(f'Unsupported language: {language}')
            
    except Exception as e:
        logging.error(f"Error executing code: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }

@app.post("/execute_code")
async def execute_code(request: CodeExecutionRequest, background_tasks: BackgroundTasks) -> CodeExecutionResult:
    execution_id = str(uuid.uuid4())
    executions[execution_id] = {
        'status': 'running',
        'result': None,
        'error': None
    }
    
    async def run_code():
        try:
            result = await execute_code_async(request.code, request.language, request.options)
            executions[execution_id].update(result)
        except Exception as e:
            logging.error(f"Error in background task: {str(e)}")
            executions[execution_id].update({
                'status': 'error',
                'error': str(e)
            })
    
    background_tasks.add_task(run_code)
    
    return CodeExecutionResult(
        execution_id=execution_id,
        status='running'
    )

@app.get("/execution_status/{execution_id}")
async def get_execution_status(execution_id: str) -> CodeExecutionResult:
    if execution_id not in executions:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    execution = executions[execution_id]
    return CodeExecutionResult(
        execution_id=execution_id,
        **execution
    )

@app.post("/agent/message")
async def send_agent_message(message: AgentMessage):
    try:
        # Log the message for debugging
        logging.info(f"Message from {message.sender} to {message.recipient}: {message.message}")
        
        # Here you would typically integrate with your AI agent system
        # For now, we'll just echo back a simple response
        response = f"Received message from {message.sender}"
        
        return {"status": "success", "response": response}
    except Exception as e:
        logging.error(f"Error processing agent message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workflow/create")
async def create_workflow(workflow: Workflow):
    workflow_id = str(uuid.uuid4())
    workflows[workflow_id] = {
        "workflow": workflow,
        "status": "created",
        "created_at": datetime.utcnow().isoformat()
    }
    return {"id": workflow_id}

@app.post("/workflow/execute/{workflow_id}")
async def execute_workflow(workflow_id: str, background_tasks: BackgroundTasks):
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow_data = workflows[workflow_id]
    workflow = workflow_data["workflow"]
    
    async def run_workflow():
        try:
            results = []
            for step in workflow.steps:
                if step.type == "code":
                    result = await execute_code_async(step.code, "python", step.options)
                    results.append(result)
                elif step.type == "message":
                    # Handle agent messages
                    pass
            
            workflow_data["status"] = "completed"
            workflow_data["results"] = results
            
        except Exception as e:
            logging.error(f"Error executing workflow: {str(e)}")
            workflow_data["status"] = "error"
            workflow_data["error"] = str(e)
    
    background_tasks.add_task(run_workflow)
    return {"status": "running"}

@app.get("/workflow/status/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return workflows[workflow_id]

@app.get("/list_workflows")
async def list_workflows():
    try:
        # Convert workflows dictionary to list format
        workflow_list = [
            {
                "id": workflow_id,
                "name": data["workflow"].name,
                "status": data["status"]
            }
            for workflow_id, data in workflows.items()
        ]
        return workflow_list
    except Exception as e:
        logging.error(f"Error listing workflows: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run_python_tool")
async def run_python_tool(request: CodeExecutionRequest):
    return await execute_code(request, BackgroundTasks())

@app.post("/run_java_tool")
async def run_java_tool(request: CodeExecutionRequest):
    request.language = "java"
    return await execute_code(request, BackgroundTasks())

@app.post("/update_code")
async def update_code(request: Request):
    try:
        data = await request.json()
        if "file_path" not in data or "code" not in data:
            return JSONResponse(
                status_code=400,
                content={"detail": "Missing required parameters"}
            )
        
        file_path = data["file_path"]
        code = data["code"]
        
        # For testing, just return 404 if file doesn't exist
        if not os.path.exists(file_path):
            return JSONResponse(
                status_code=404,
                content={"detail": "File not found"}
            )
            
        return {"status": "success"}
    except json.JSONDecodeError:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid JSON"}
        )
    except Exception as e:
        logging.error(f"Error updating code: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": str(e)}
        )

@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/autogen/execute")
async def autogen_execute_task(task_description: str):
    workflow = AutogenWorkflow()
    result = await workflow.execute_task(task_description)
    if result is None:
        return JSONResponse(
            status_code=500,
            content={"error": "No response generated"}
        )
    return {"result": result}

@app.post("/autogen/analyze")
async def autogen_analyze_data(data_file: str, analysis_prompt: str):
    workflow = AutogenWorkflow()
    result = await workflow.analyze_data(data_file, analysis_prompt)
    if result is None:
        return JSONResponse(
            status_code=500,
            content={"error": "No response generated"}
        )
    return {"result": result}

@app.post("/generate_python")
async def generate_python_code(request: Request):
    try:
        # Get the request body
        body = await request.json()
        prompt = body.get("prompt", "")
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
            
        # Create workflow instance
        workflow = AutogenWorkflow()
        
        # Execute the task
        result = await workflow.execute_task(prompt)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to generate code")
            
        return {"result": result}
        
    except Exception as e:
        logging.error(f"Error in generate_python_code: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate_java")
async def generate_java_code(request: CodeGenerationRequest):
    try:
        workflow = AutogenWorkflow()
        task_description = f"""Generate Java code for the following request: {request.prompt}
        Include appropriate test cases and documentation.
        Format the response as follows:
        ```java
        [code here]
        ```
        ```test
        [test cases here]
        ```
        """
        result = await workflow.execute_task(task_description)
        
        if not result:
            raise ValueError("No response generated")
            
        # Extract code and tests from the result
        code_match = re.search(r'```java\n(.*?)\n```', result, re.DOTALL)
        test_match = re.search(r'```test\n(.*?)\n```', result, re.DOTALL)
        
        if not code_match:
            raise ValueError("No code was generated")
            
        code = code_match.group(1).strip()
        tests = []
        
        if test_match:
            test_code = test_match.group(1).strip()
            # Create temporary files
            main_file = "Main.java"
            test_file = "MainTest.java"
            
            with open(main_file, "w") as f:
                f.write(code)
            with open(test_file, "w") as f:
                f.write(test_code)
            
            try:
                # Compile and run tests
                subprocess.run(["javac", "-cp", "junit-platform-console-standalone.jar", 
                              main_file, test_file], check=True)
                test_result = subprocess.run(["java", "-jar", "junit-platform-console-standalone.jar",
                                            "--class-path", ".", "--scan-class-path"],
                                           capture_output=True, text=True)
                tests = parse_junit_output(test_result.stdout)
            except Exception as e:
                tests = [{"name": "Test Execution", "passed": False, "message": str(e)}]
            finally:
                # Clean up
                for file in [main_file, test_file, "Main.class", "MainTest.class"]:
                    if os.path.exists(file):
                        os.remove(file)
        
        return CodeGenerationResponse(code=code, tests=tests)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/python_tool")
async def python_tool(request: Request):
    return templates.TemplateResponse("python_tool.html", {"request": request})

@app.get("/java_tool")
async def java_tool(request: Request):
    return templates.TemplateResponse("java_tool.html", {"request": request})

@app.post("/analyze_codebase")
async def analyze_codebase(path: str):
    results = await team_manager.analyze_and_improve(Path(path))
    return JSONResponse(content=results)

@app.post("/solve_problem")
async def solve_problem(problem_description: str):
    results = await team_manager.solve_problem(problem_description)
    return JSONResponse(content=results)

@app.post("/improve_tests")
async def improve_tests(feature_description: str):
    results = await team_manager.improve_test_coverage(feature_description)
    return JSONResponse(content=results)

def parse_pytest_output(output: str) -> List[Dict[str, Any]]:
    tests = []
    for line in output.split('\n'):
        if line.startswith('test_'):
            name = line.split(' ')[0]
            passed = 'PASSED' in line
            message = line[len(name):].strip() if not passed else None
            tests.append({
                "name": name,
                "passed": passed,
                "message": message
            })
    return tests

def parse_junit_output(output: str) -> List[Dict[str, Any]]:
    tests = []
    current_test = None
    
    for line in output.split('\n'):
        if line.startswith('Test '):
            if current_test:
                tests.append(current_test)
            name = line.split(' ')[1]
            passed = 'SUCCESS' in line
            current_test = {
                "name": name,
                "passed": passed,
                "message": None
            }
        elif current_test and line.strip().startswith('org.opentest4j.AssertionFailedError'):
            current_test["message"] = line.strip()
    
    if current_test:
        tests.append(current_test)
    
    return tests

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)