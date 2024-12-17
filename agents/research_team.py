from typing import Dict, List, Optional
import autogen
from pathlib import Path

class ResearchTeam:
    def __init__(self, config_list: List[Dict]):
        self.llm_config = {
            "config_list": config_list,
            "timeout": 120,
            "temperature": 0
        }
        
        self.code_analyzer = autogen.AssistantAgent(
            name="code_analyzer",
            llm_config=self.llm_config,
            system_message="You analyze code structure, patterns, and potential improvements. Focus on code quality and best practices.",
        )
        
        self.solution_researcher = autogen.AssistantAgent(
            name="solution_researcher",
            llm_config=self.llm_config,
            system_message="You research and propose optimal solutions for coding problems. Consider performance, scalability, and maintainability.",
        )
        
        self.test_strategist = autogen.AssistantAgent(
            name="test_strategist",
            llm_config=self.llm_config,
            system_message="You design comprehensive test strategies. Focus on test coverage, edge cases, and isolation principles.",
        )
        
        self.coordinator = autogen.UserProxyAgent(
            name="research_coordinator",
            human_input_mode="NEVER",
            code_execution_config={"work_dir": "workspace"},
            is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", "").upper(),
        )

    async def analyze_codebase(self, path: Path) -> Dict:
        """Analyze codebase structure and propose improvements"""
        results = {}
        
        # Code analysis
        chat_result = await self.coordinator.initiate_chat(
            self.code_analyzer,
            message=f"Analyze code structure and patterns in: {path}"
        )
        results["code_analysis"] = chat_result.last_message["content"]
        
        # Solution research
        chat_result = await self.coordinator.initiate_chat(
            self.solution_researcher,
            message=f"Research optimal solutions and improvements for: {path}"
        )
        results["solution_research"] = chat_result.last_message["content"]
        
        # Test strategy
        chat_result = await self.coordinator.initiate_chat(
            self.test_strategist,
            message=f"Design test strategy for codebase: {path}"
        )
        results["test_strategy"] = chat_result.last_message["content"]
        
        return results

    async def research_solution(self, problem_description: str) -> Dict:
        """Research solutions for a specific coding problem"""
        results = {}
        
        # Solution research
        chat_result = await self.coordinator.initiate_chat(
            self.solution_researcher,
            message=f"Research solution approaches for: {problem_description}"
        )
        results["solution_approaches"] = chat_result.last_message["content"]
        
        # Implementation strategy
        chat_result = await self.coordinator.initiate_chat(
            self.code_analyzer,
            message=f"Analyze implementation strategy for: {problem_description}"
        )
        results["implementation_strategy"] = chat_result.last_message["content"]
        
        return results

    async def design_test_plan(self, feature_description: str) -> Dict:
        """Design comprehensive test plan for a feature"""
        chat_result = await self.coordinator.initiate_chat(
            self.test_strategist,
            message=f"Design complete test plan for: {feature_description}"
        )
        return {"test_plan": chat_result.last_message["content"]}
