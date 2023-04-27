# Nodes

Nodes are the primary building blocks of a Flowchart. They are the individual components that make up a flowchart. Nodes are connected by edges, and each node has a specific function.

(Init)=
## Init

The Init node is run once and only once at the beginning of the flowchart. It is used to initialize external resources, such as vecstores, embeddings, or databases.

(Start)=
## Start

The Start node is the beginning of your flowchart. It will *always* run first, and can be connected to any other node in your flowchart.

(Input)=
## Input

Pauses the flowchart and waits for user input. Useful for chatbots or interactive programs.

(History)=
## History

Saves the output of the previous node to a running history. Useful for chatbots or interactive programs. Follows OpenAI's history scheme, with 3 roles: `assistant`, `user`, and `system`. Double-click the node to edit which role the node will save to.

For a simple example of History Node usage, see [Usage](working-with-llms).

(Prompt)=
## Prompt

Outputs an f-string style formatted string. You can edit the prompt text by double-clicking the lower `Prompt` label on the node.

For a simple example of Prompt Node usage, see [Usage](working-with-llms).

To inject the result of the previous node, use `{state.result}`. For example:

```text
You are a {state.result}. Please stay in character, and answer as a {state.result} would.
```

Connecting the following flowchart would allow the user to program any "personality" they want:

![image](../screenshots/docs/roleplay.png)

(LLM)=
## LLM

Call to a Large Language Model. Currently restricted to OpenAI's API. Double-click to edit the LLM parameters.

![image](../screenshots/docs/llm_options.png)