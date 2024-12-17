from typing import Dict, List, Optional
import asyncio
from pathlib import Path
from .research_team import ResearchTeam
from .debug_team import DebugTeam

class TeamManager:
    def __init__(self, config_list: List[Dict]):
        self.research_team = ResearchTeam(config_list)
        self.debug_team = DebugTeam(config_list)

    async def analyze_and_improve(self, path: Path) -> Dict:
        """Coordinate research and debug teams for codebase improvement"""
        results = {}
        
        # Run research and debug tasks in parallel
        research_task = asyncio.create_task(
            self.research_team.analyze_codebase(path)
        )
        
        # Simulate error info for demonstration
        error_info = {
            "message": "Analyzing potential issues in codebase",
            "context": str(path),
            "traceback": ""
        }
        debug_task = asyncio.create_task(
            self.debug_team.analyze_error(error_info)
        )
        
        # Wait for both teams to complete their analysis
        results["research"], results["debug"] = await asyncio.gather(research_task, debug_task)
        
        return results

    async def solve_problem(self, problem_description: str) -> Dict:
        """Coordinate teams to solve a specific problem"""
        results = {}
        
        # Research solutions
        results["research"] = await self.research_team.research_solution(
            problem_description
        )
        
        # Validate proposed solution
        fix_info = {
            "original_issue": problem_description,
            "fix": results["research"]["solution_approaches"],
            "test_cases": []
        }
        results["validation"] = await self.debug_team.validate_fix(fix_info)
        
        return results

    async def improve_test_coverage(self, feature_description: str) -> Dict:
        """Design and validate test improvements"""
        results = {}
        
        # Get test plan
        results["test_plan"] = await self.research_team.design_test_plan(
            feature_description
        )
        
        # Validate test plan
        results["validation"] = await self.debug_team.validate_fix({
            "original_issue": "Test coverage improvement",
            "fix": str(results["test_plan"]),
            "test_cases": []
        })
        
        return results
