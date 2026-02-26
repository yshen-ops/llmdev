import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Annotated
from typing_extensions import TypedDict

load_dotenv(".env")
os.environ['OPENAI_API_KEY'] = os.environ['API_KEY']
MODEL_NAME = "gpt-4o-mini" 
memory = MemorySaver()
graph = None

SYSTEM_PROMPT = "あなたは猫です、にゃーと絵文字を使うのが大好き"

class State(TypedDict):
    messages: Annotated[list, add_messages]

def build_graph(model_name, memory):
    """
    グラフのインスタンスを作成し、ツールノードやチャットボットノードを追加します。
    モデル名とメモリを使用して、実行可能なグラフを作成します。
    """
    graph_builder = StateGraph(State)
    tavily_tool = TavilySearchResults(max_results=2)
    tools = [tavily_tool]
    tool_node = ToolNode(tools)
    graph_builder.add_node("tools", tool_node)

    llm = ChatOpenAI(model_name=model_name)
    llm_with_tools = llm.bind_tools(tools)
    def chatbot(state: State):
        messages = state["messages"]
        if not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
        return {"messages": [llm_with_tools.invoke(messages)]}
    
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_conditional_edges(
        "chatbot",
        tools_condition,
    )
    graph_builder.add_edge("tools", "chatbot")
    graph_builder.set_entry_point("chatbot")
    
    return graph_builder.compile(checkpointer=memory)

def stream_graph_updates(graph: StateGraph, user_message: str):
    """
    ユーザーからのメッセージを元に、グラフを実行し、チャットボットの応答をストリーミングします。
    """
    response = graph.invoke(
        {"messages": [("user", user_message)]},
        {"configurable": {"thread_id": "1"}},
        stream_mode="values"
    )
    return response["messages"][-1].content

def get_bot_response(user_message, memory):
    """
    ユーザーのメッセージに基づき、ボットの応答を取得します。
    初回の場合、新しいグラフを作成します。
    """
    global graph
    if graph is None:
        graph = build_graph(MODEL_NAME, memory)

    return stream_graph_updates(graph, user_message)

def get_messages_list(memory):
    """
    メモリからメッセージ一覧を取得し、ユーザーとボットのメッセージを分類します。
    """
    messages = []
    memories = memory.get({"configurable": {"thread_id": "1"}})['channel_values']['messages']
    for message in memories:
        if isinstance(message, HumanMessage):
            messages.append({'class': 'user-message', 'text': message.content.replace('\n', '<br>')})
        elif isinstance(message, AIMessage) and message.content != "":
            messages.append({'class': 'bot-message', 'text': message.content.replace('\n', '<br>')})
    return messages