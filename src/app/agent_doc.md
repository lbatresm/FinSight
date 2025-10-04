# Agent properties

### Memory

By default, state is transient to a single graph execution. We gave the agent memory using [persistence](https://langchain-ai.github.io/langgraph/how-tos/persistence/). We use a checkpointer to save the graph state after each step. One of the easiest checkpointers to use is the `MemorySaver`, an in-memory key-value store for Graph state.

### Messages as State and Reducers 

As Langchain suggests, we should define a [state](https://docs.langchain.com/oss/python/langgraph/use-graph-api#messagesstate) for the messages, which will be a TypedDict with a single key, `messages`, which is a list of messages. Each node will return a new value for this `messages` key. But we have a problem, this new value will override the prior `messages` value.
 
As our graph runs, we want to **append** messages to our `messages` state key.  
We can use [reducer functions](https://langchain-ai.github.io/langgraph/concepts/low_level/#reducers) to address this.
Reducers allow us to specify how state updates are performed. If no reducer function is specified, then it is assumed that updates to the key should *override it* as we saw before. But, to append messages, we can use the pre-built `add_messages` reducer. 

Instead of building our own State, we could use [MessagesState](https://docs.langchain.com/oss/python/langgraph/use-graph-api#messagesstate) built in function, but we'll keep it didactive for now.