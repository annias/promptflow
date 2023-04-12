from typing import TYPE_CHECKING, Any, Optional

import tiktoken
from promptflow.src.state import State

from promptflow.src.text_data import TextData
from promptflow.src.utils import retry_with_exponential_backoff

if TYPE_CHECKING:
    from promptflow.src.flowchart import Flowchart
from promptflow.src.nodes.node_base import Node
from promptflow.src.dialogues.text_input import TextInput
from promptflow.src.dialogues.node_options import NodeOptions
from promptflow.src.themes import monokai

import tkinter as tk
import openai
import os
import enum

openai.api_key = os.getenv("OPENAI_API_KEY")


class Model(enum.Enum):
    # manually add these as they become available
    # https://platform.openai.com/docs/models
    textdavinci = "text-davinci-003"
    gpt35turbo = "gpt-3.5-turbo"
    gpt35turbo0301 = "gpt-3.5-turbo-0301"
    gpt4 = "gpt-4"
    gpt40314 = "gpt-4-0314"


chat_models = [
    Model.gpt35turbo.value,
    Model.gpt35turbo0301.value,
    Model.gpt4.value,
    Model.gpt40314.value,
]


# https://openai.com/pricing
prompt_cost_1k = {
    Model.textdavinci.value: 0.02,
    Model.gpt35turbo.value: 0.002,
    Model.gpt35turbo0301.value: 0.002,
    Model.gpt4.value: 0.03,
    Model.gpt40314.value: 0.03,
}
completion_cost_1k = {
    Model.textdavinci.value: 0.02,
    Model.gpt35turbo.value: 0.002,
    Model.gpt35turbo0301.value: 0.002,
    Model.gpt4.value: 0.06,
    Model.gpt40314.value: 0.06,
}


class LLMNode(Node):
    """
    Node that uses the OpenAI API to generate text.
    """

    node_color = monokai.green

    def __init__(
        self,
        flowchart: "Flowchart",
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        label: str,
        system_prompt: Optional[TextData | dict] = None,
        model: str = Model.gpt35turbo.value,
        **kwargs,
    ):
        self.temperature = 0.0
        self.top_p = 1.0
        self.n = 1
        # self.stop = "\n\n"
        self.max_tokens = 256
        self.presence_penalty = 0.0
        self.frequency_penalty = 0.0

        self.model_var = tk.StringVar(value=model)
        self.model = model
        super().__init__(flowchart, x1, y1, x2, y2, label, **kwargs)
        # create the prompt
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2 + 10
        if system_prompt is None:
            system_prompt = {"label": "System Prompt", "text": ""}
        if isinstance(system_prompt, dict):
            system_prompt = TextData.deserialize(system_prompt, self.flowchart)
        self.system_prompt: TextData = system_prompt

        self.system_prompt_item = self.canvas.create_text(
            center_x, center_y, text=self.system_prompt.label
        )
        self.items.extend([self.system_prompt_item])
        self.canvas.tag_bind(
            self.system_prompt_item, "<Double-Button-1>", self.edit_system_prompt
        )
        self.canvas.tag_bind(self.item, "<Double-Button-1>", self.edit_options)
        self.canvas.update()
        self.bind_drag()
        self.text_window: Optional[TextInput] = None
        self.options_popup: Optional[NodeOptions] = None

    def edit_system_prompt(self, _: tk.Event):
        """
        Create a text input window to edit the system prompt.
        """
        self.text_window = TextInput(self.canvas, self.flowchart, self.system_prompt)
        self.text_window.set_callback(self.save_system_prompt)

    def save_system_prompt(self):
        """
        Write the system prompt to the canvas.
        """
        if self.text_window is None:
            self.logger.error("text_window is None")
            return
        self.system_prompt = self.text_window.get_text()
        self.canvas.itemconfig(self.system_prompt_item, text=self.system_prompt.label)
        self.text_window.destroy()

    def edit_options(self, event: tk.Event):
        """
        Create a menu to edit the prompt.
        """
        self.options_popup = NodeOptions(
            self.canvas,
            {
                "Model": self.model_var.get(),
                "Temperature": self.temperature,
                "Top P": self.top_p,
                "n": self.n,
                # "stop": self.stop,
                "Max Tokens": self.max_tokens,
                "presence_penalty": self.presence_penalty,
                "frequency_penalty": self.frequency_penalty,
            },
            {
                "Model": [model.value for model in Model],
            },
        )
        self.canvas.wait_window(self.options_popup)
        result = self.options_popup.result
        # check if cancel
        if self.options_popup.cancelled:
            return
        self.model_var.set(result["Model"])
        self.on_model_select(None)  # todo: manually calling this is a bit hacky
        self.max_tokens = int(result["Max Tokens"])
        self.temperature = float(result["Temperature"])
        self.top_p = float(result["Top P"])
        self.n = int(result["n"])
        # self.stop = result["stop"]
        self.presence_penalty = float(result["presence_penalty"])
        self.frequency_penalty = float(result["frequency_penalty"])

    @retry_with_exponential_backoff
    def _chat_completion(self, prompt: str, system_message: str, state: State) -> str:
        """
        Simple wrapper around the OpenAI API to generate text.
        """
        messages = [
            *state.history,
            # {"role": "system", "content": system_message},
            # {"role": "user", "content": prompt},
        ]
        if system_message or len(messages) == 0:
            messages.append({"role": "system", "content": system_message})
        if prompt:
            messages.append({"role": "user", "content": prompt})
        completion = openai.ChatCompletion.create(
            model=self.model_var.get(),
            messages=messages,
            temperature=self.temperature,
            top_p=self.top_p,
            n=self.n,
            # stop=self.stop,
            max_tokens=self.max_tokens,
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty,
        )
        return completion["choices"][0]["message"]["content"]  # type: ignore

    @retry_with_exponential_backoff
    def _completion(self, prompt: str, system_message: str, state: State) -> str:
        """
        Simple wrapper around the OpenAI API to generate text.
        """
        # todo this history is really opinionated
        history = "\n".join(
            [
                system_message,
                *[
                    f"{message['role']}: {message['content']}"
                    for message in state.history
                ],
            ]
        )
        prompt = f"{history}\n{prompt}\n"
        completion = openai.Completion.create(
            model=self.model_var.get(),
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            n=self.n,
            # stop=self.stop,
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty,
        )
        return completion["choices"][0]["text"]  # type: ignore

    def run_subclass(self, state: State):
        """
        Format the prompt and run the OpenAI API.
        """
        prompt = state.result
        system_message = self.system_prompt.text.format(state=state)
        self.logger.info(f"Running LLMNode with prompt: {prompt}")
        if self.model in chat_models:
            completion = self._chat_completion(prompt, system_message, state)
        else:
            completion = self._completion(prompt, system_message, state)
        self.logger.info(f"Result of LLMNode is {completion}")  # type: ignore
        return completion  # type: ignore

    def serialize(self):
        return super().serialize() | {
            "system_prompt": self.system_prompt.serialize(),
            "model": self.model_var.get(),
        }

    def on_model_select(self, _: Optional[tk.Event]):
        """
        Callback for when the OpenAI model is changed.
        """
        self.model = self.model_var.get()
        if self.model in [Model.gpt4.value, Model.gpt40314.value]:
            self.logger.warning("You're using a GPT-4 model. This is costly.")
        self.logger.info(f"Selected model: {self.model}")

    def cost(self, state: State) -> float:
        """
        Return the cost of running this node.
        """
        # count the number of tokens
        enc = tiktoken.encoding_for_model(self.model)
        prompt_tokens = enc.encode(state.result.format(state=state))
        system_prompt_tokens = enc.encode(self.system_prompt.text.format(state=state))
        max_completion_tokens = (
            self.max_tokens - len(prompt_tokens) - len(system_prompt_tokens)
        )
        prompt_cost = prompt_cost_1k[self.model] * len(prompt_tokens) / 1000
        system_prompt_cost = (
            prompt_cost_1k[self.model] * len(system_prompt_tokens) / 1000
        )
        completion_cost = completion_cost_1k[self.model] * max_completion_tokens / 1000
        total = prompt_cost + system_prompt_cost + completion_cost
        return total
