"""
Base Worker Agent Contract Definition
All domain worker agents inherit from BaseWorkerAgent and adhere to contract payloads in specs/
"""
from abc import ABC, abstractmethod
from models.agent_schemas import AgentDelegationPayload, AgentResponseSynthesis

class BaseWorkerAgent(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute_task(self, payload: AgentDelegationPayload) -> AgentResponseSynthesis:
        """
        Execute delegated task based on contract payload and return synthesized response.
        """
        pass
