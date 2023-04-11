"""
Simulates an LLMNode, but does not actually send any data to the LLM.
"""
from promptflow.src.nodes.llm_node import LLMNode
from promptflow.src.state import State


class DummyNode(LLMNode):
    """
    Simulates an LLMNode, but does not actually send any data to the LLM.
    """

    def _chat_completion(self, prompt: str, system_message: str, state: State) -> str:
        return "dummy response"

    def _completion(self, prompt: str, system_message: str, state: State) -> str:
        return "dummy response"
