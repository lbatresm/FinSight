# Agent properties

### Short-term memory (persistence)

By default, state is transient to a single graph execution. We gave the agent memory using [persistence](https://langchain-ai.github.io/langgraph/how-tos/persistence/). We use a checkpointer to save the graph state after each step. One of the easiest checkpointers to use is the `MemorySaver`, an in-memory key-value store for Graph state. We use thread_id to access threads.

### Messages as State and Reducers 

As Langchain suggests, we should define a [state](https://docs.langchain.com/oss/python/langgraph/use-graph-api#messagesstate) for the messages, which will be a TypedDict with a single key, `messages`, which is a list of messages. Each node will return a new value for this `messages` key. But we have a problem, this new value will override the prior `messages` value.
 
As our graph runs, we want to **append** messages to our `messages` state key.  
We can use [reducer functions](https://langchain-ai.github.io/langgraph/concepts/low_level/#reducers) to address this.
Reducers allow us to specify how state updates are performed. If no reducer function is specified, then it is assumed that updates to the key should *override it* as we saw before. But, to append messages, we can use the pre-built `add_messages` reducer. 

Instead of building our own State, we could use [MessagesState](https://docs.langchain.com/oss/python/langgraph/use-graph-api#messagesstate) built in function, but we'll keep it didactive for now.

We can use the `Annotated` type to specify a reducer function. Reducer functions also help us to handle parallel nodes case, we can design custom reducers for this.

For the moment we'll use `TypedDict State Schema`. We could change to `Pydantic` if we want to enforce types at runtime. [Info here.](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)

### Max tokens for a conversation
`trim_message`function is used to limit the maximum amount of tokens for the conversation history. 

* For simple bots 500-2000 tokens should be enough
* For more complex converrsations 4000-8000 tokens.
* gpt-40 has a limit of 128 tokens of conext

### Streaming (TODO)

LangGraph supports various streaming methods (stream() or astream()) and various modes (values, updates, custom, messages, debug)

Use:

# ---- Run ----
messages = [
    sys_msg,  # Use SystemMessage!
    HumanMessage(content="Add 3 and 4. Multiply the output by 2. Divide the output by 5."),
]


async def main():
    node_to_stream = "assistant"

    async for event in react_graph.astream_events(
        {"messages": messages}, 
        config, 
        version="v2"
    ):
        if event["event"] == "on_chat_model_stream" and event["metadata"].get("langgraph_node", "") == node_to_stream:
            print(event["data"], end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main())