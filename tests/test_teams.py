import pytest
from pathlib import Path
from agents import ResearchTeam, DebugTeam, TeamManager

@pytest.fixture
def config_list():
    return [{
        'model': 'llama3.1:8b',
        'base_url': "http://localhost:11434/v1",
        'api_key': "ollama"
    }]

@pytest.fixture
def research_team(config_list):
    return ResearchTeam(config_list)

@pytest.fixture
def debug_team(config_list):
    return DebugTeam(config_list)

@pytest.fixture
def team_manager(config_list):
    return TeamManager(config_list)

@pytest.mark.asyncio
async def test_research_team_analysis(research_team, tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("def test_function():\n    pass")
    
    results = await research_team.analyze_codebase(test_file)
    assert "code_analysis" in results
    assert "solution_research" in results
    assert "test_strategy" in results

@pytest.mark.asyncio
async def test_debug_team_error_analysis(debug_team):
    error_info = {
        "message": "Test error",
        "traceback": "Test traceback",
        "context": "Test context"
    }
    
    results = await debug_team.analyze_error(error_info)
    assert "error_analysis" in results
    assert "fix_proposal" in results
    assert "validation_plan" in results

@pytest.mark.asyncio
async def test_team_manager_coordination(team_manager, tmp_path):
    test_file = tmp_path / "test.py"
    test_file.write_text("def test_function():\n    pass")
    
    results = await team_manager.analyze_and_improve(test_file)
    assert "research" in results
    assert "debug" in results

@pytest.mark.asyncio
async def test_problem_solving(team_manager):
    problem = "Optimize a function for better performance"
    results = await team_manager.solve_problem(problem)
    assert "research" in results
    assert "validation" in results

@pytest.mark.asyncio
async def test_test_coverage_improvement(team_manager):
    feature = "User authentication system"
    results = await team_manager.improve_test_coverage(feature)
    assert "test_plan" in results
    assert "validation" in results
