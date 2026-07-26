"""
Agent Process Manager & Circuit Breaker Supervisor Lifecycle Manager
Handles agent process health state, consecutive crash tracking, and automatic restarts
up to max_consecutive_crashes (default 5).
"""
import logging
import time
from typing import Dict, Any, Callable, Optional
from models.agent_schemas import (
    AgentProcessState,
    AgentDelegationPayload,
    AgentResponseSynthesis
)
from agents.base_worker import BaseWorkerAgent

logger = logging.getLogger(__name__)

class AgentProcessManager:
    def __init__(self, max_consecutive_crashes: int = 5):
        self.default_max_crashes = max_consecutive_crashes
        self.process_states: Dict[str, AgentProcessState] = {}
        self.agent_factories: Dict[str, Callable[[], BaseWorkerAgent]] = {}
        self.agent_instances: Dict[str, Optional[BaseWorkerAgent]] = {}

    def register_agent(
        self,
        agent_name: str,
        factory_fn: Callable[[], BaseWorkerAgent],
        max_consecutive_crashes: Optional[int] = None
    ) -> None:
        """
        Register a worker agent process factory and initialize its process state.
        """
        max_crashes = max_consecutive_crashes if max_consecutive_crashes is not None else self.default_max_crashes
        self.agent_factories[agent_name] = factory_fn
        self.agent_instances[agent_name] = None
        self.process_states[agent_name] = AgentProcessState(
            agent_name=agent_name,
            status="HEALTHY",
            consecutive_crashes=0,
            max_consecutive_crashes=max_crashes,
            last_error=None
        )

    def get_process_state(self, agent_name: str) -> Optional[AgentProcessState]:
        """Retrieve current process state for a registered agent."""
        return self.process_states.get(agent_name)

    def reset_process(self, agent_name: str) -> bool:
        """
        Reset an agent's process state back to HEALTHY and clear crash counts.
        """
        if agent_name in self.process_states:
            state = self.process_states[agent_name]
            state.status = "HEALTHY"
            state.consecutive_crashes = 0
            state.last_error = None
            state.last_crash_timestamp = None
            self.agent_instances[agent_name] = None
            return True
        return False

    def execute_task(self, agent_name: str, payload: AgentDelegationPayload) -> AgentResponseSynthesis:
        """
        Execute task on agent process with automatic crash protection and restart retries
        up to max_consecutive_crashes limit (5).
        """
        if agent_name not in self.process_states:
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=False,
                final_reply_text=f"Unknown agent process: {agent_name}"
            )

        state = self.process_states[agent_name]

        # Circuit open check: if agent process already exceeded max consecutive crashes
        if state.status == "FAILED_MAX_RETRIES":
            cool_off_period = 60 # seconds
            if state.last_crash_timestamp and (time.time() - state.last_crash_timestamp) > cool_off_period:
                logger.info(f"[AgentProcessManager] Cool-off period ended. Resetting agent process {agent_name} to HEALTHY.")
                self.reset_process(agent_name)
            else:
                logger.error(
                    f"[AgentProcessManager] Execution rejected. Agent process {agent_name} "
                    f"failed to restart after {state.consecutive_crashes} consecutive crashes"
                )
            return AgentResponseSynthesis(
                delegation_id=payload.delegation_id,
                success=False,
                final_reply_text="Agent process failed to restart after 5 consecutive crashes",
                metadata={
                    "agent_name": agent_name,
                    "status": state.status,
                    "consecutive_crashes": state.consecutive_crashes,
                    "last_error": state.last_error
                }
            )

        # Retry loop for handling process restarts
        while state.consecutive_crashes < state.max_consecutive_crashes:
            try:
                # Instantiate process if not active
                if self.agent_instances[agent_name] is None:
                    factory = self.agent_factories[agent_name]
                    self.agent_instances[agent_name] = factory()

                instance = self.agent_instances[agent_name]
                synthesis = instance.execute_task(payload)

                # Reset crash count upon successful execution
                state.status = "HEALTHY"
                state.consecutive_crashes = 0
                state.last_error = None
                state.last_crash_timestamp = None
                return synthesis

            except Exception as e:
                state.consecutive_crashes += 1
                state.last_error = str(e)
                state.last_crash_timestamp = time.time()
                self.agent_instances[agent_name] = None  # Terminate crashed instance

                logger.warning(
                    f"[AgentProcessManager] Agent {agent_name} process crash detected "
                    f"({state.consecutive_crashes}/{state.max_consecutive_crashes}): {e}"
                )

                if state.consecutive_crashes < state.max_consecutive_crashes:
                    state.status = "RESTARTING"
                    logger.info(f"[AgentProcessManager] Restarting process for {agent_name} (Attempt {state.consecutive_crashes + 1})...")
                else:
                    state.status = "FAILED_MAX_RETRIES"
                    logger.critical(
                        f"[AgentProcessManager] Agent process failed to restart after "
                        f"{state.consecutive_crashes} consecutive crashes"
                    )
                    break

        return AgentResponseSynthesis(
            delegation_id=payload.delegation_id,
            success=False,
            final_reply_text="Agent process failed to restart after 5 consecutive crashes",
            metadata={
                "agent_name": agent_name,
                "status": state.status,
                "consecutive_crashes": state.consecutive_crashes,
                "last_error": state.last_error
            }
        )
