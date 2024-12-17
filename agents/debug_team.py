from typing import Dict, List, Optional
import autogen
from pathlib import Path
import traceback

class DebugTeam:
    def __init__(self, config_list: List[Dict]):
        self.llm_config = {
            "config_list": config_list,
            "timeout": 120,
            "temperature": 0
        }
        
        self.error_analyzer = autogen.AssistantAgent(
            name="error_analyzer",
            llm_config=self.llm_config,
            system_message="You analyze error messages, stack traces, and code context to identify root causes of issues.",
        )
        
        self.fix_proposer = autogen.AssistantAgent(
            name="fix_proposer",
            llm_config=self.llm_config,
            system_message="You propose specific code fixes based on error analysis. Focus on robust, maintainable solutions.",
        )
        
        self.test_validator = autogen.AssistantAgent(
            name="test_validator",
            llm_config=self.llm_config,
            system_message="You validate proposed fixes through targeted testing. Ensure fixes don't introduce new issues.",
        )
        
        self.coordinator = autogen.UserProxyAgent(
            name="debug_coordinator",
            human_input_mode="NEVER",
            code_execution_config={"work_dir": "workspace"},
            is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", "").upper(),
        )

    async def analyze_error(self, error_info: Dict) -> Dict:
        """Analyze error information and propose fixes"""
        results = {}
        
        error_context = f"""
        Error Message: {error_info.get('message', '')}
        Stack Trace: {error_info.get('traceback', '')}
        Code Context: {error_info.get('context', '')}
        """
        
        # Error analysis
        chat_result = self.coordinator.initiate_chat(
            self.error_analyzer,
            message=f"Analyze error and identify root cause:\n{error_context}"
        )
        results["error_analysis"] = chat_result.last_message["content"]
        
        # Fix proposal
        chat_result = self.coordinator.initiate_chat(
            self.fix_proposer,
            message=f"Propose specific code fixes based on analysis:\n{results['error_analysis']}"
        )
        results["fix_proposal"] = chat_result.last_message["content"]
        
        # Validation plan
        chat_result = self.coordinator.initiate_chat(
            self.test_validator,
            message=f"Design validation tests for proposed fix:\n{results['fix_proposal']}"
        )
        results["validation_plan"] = chat_result.last_message["content"]
        
        return results

    async def validate_fix(self, fix_info: Dict) -> Dict:
        """Validate proposed fix through testing"""
        validation_context = f"""
        Original Issue: {fix_info.get('original_issue', '')}
        Proposed Fix: {fix_info.get('fix', '')}
        Test Cases: {fix_info.get('test_cases', [])}
        """
        
        chat_result = self.coordinator.initiate_chat(
            self.test_validator,
            message=f"Validate fix implementation:\n{validation_context}"
        )
        return {"validation_result": chat_result.last_message["content"]}

    async def debug_code_section(self, code: str, error_message: str) -> Dict:
        """Debug specific section of code"""
        results = {}
        
        # Initial error analysis
        chat_result = self.coordinator.initiate_chat(
            self.error_analyzer,
            message=f"Analyze code section and error:\nCode:\n{code}\nError:\n{error_message}"
        )
        results["analysis"] = chat_result.last_message["content"]
        
        # Generate fix
        chat_result = self.coordinator.initiate_chat(
            self.fix_proposer,
            message=f"Propose fix based on analysis:\n{results['analysis']}"
        )
        results["fix"] = chat_result.last_message["content"]
        
        return results
