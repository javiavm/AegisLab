"""
Base agent class for all safety agents.

Provides common functionality for LLM interaction and tool usage.
"""

from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from safety_agent.llm.client import LLMClient

# Type variables for input and output types
InputT = TypeVar("InputT")
OutputT = TypeVar("OutputT")


class BaseAgent(ABC, Generic[InputT, OutputT]):
    """
    Abstract base class for all agents in the safety workflow.

    Agents are intelligent components that:
    - Use LLM for reasoning, extraction, and decision-making
    - Can call deterministic tools for specific operations
    - Transform input data into structured output

    Subclasses must implement:
    - run(): Main execution logic
    - _build_prompt(): Construct the LLM prompt

    Attributes:
        name: Human-readable agent name
        llm_client: Client for LLM API calls

    Example:
        >>> class MyAgent(BaseAgent[InputModel, OutputModel]):
        ...     def run(self, input_data: InputModel) -> OutputModel:
        ...         prompt = self._build_prompt(input_data)
        ...         response = self.llm_client.complete(prompt)
        ...         return self._parse_response(response)
    """

    name: str = "BaseAgent"

    def __init__(self, llm_client: LLMClient | None = None):
        """
        Initialize the agent.
        """
        self.llm_client = llm_client or LLMClient()

    @abstractmethod
    def run(self, input_data: InputT) -> OutputT:
        """
        Execute the agent's main logic.

        Args:
            input_data: Input data specific to this agent type

        Returns:
            Processed output data

        Raises:
            AgentError: If processing fails
        """
        pass

    @abstractmethod
    def _build_prompt(self, input_data: InputT) -> str:
        """
        Construct the prompt to send to the LLM.

        Args:
            input_data: Input data to include in the prompt

        Returns:
            Formatted prompt string
        """
        pass

    def _parse_response(self, response: str) -> Any:
        """
        Parse the LLM response into structured data.

        Override in subclasses for specific parsing logic.

        Args:
            response: Raw LLM response text

        Returns:
            Parsed data (structure depends on agent)
        """
        return response


class AgentError(Exception):
    """Exception raised when an agent encounters an error."""

    def __init__(self, agent_name: str, message: str):
        self.agent_name = agent_name
        self.message = message
        super().__init__(f"[{agent_name}] {message}")
