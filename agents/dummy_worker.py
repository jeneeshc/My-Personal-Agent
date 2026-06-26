"""
Dummy Worker Agent for LangGraph integration testing
"""

class DummyWorkerAgent:
    def __init__(self, name: str):
        self.name = name
        
    def execute_task(self, context: dict) -> str:
        """
        Execute a simulated task based on context.
        """
        task_info = context.get("task_info", "unknown task")
        print(f"[{self.name}] Executing task: {task_info}")
        return f"{self.name} has successfully completed: {task_info}"
