from agiflow import Agiflow
from agiflow.opentelemetry import workflow
from dotenv import load_dotenv
import os
from pathlib import Path

from langgraph.checkpoint import MemorySaver
from langgraph.graph import END, START, StateGraph, MessagesState
from langchain_core.messages import RemoveMessage
from langgraph.prebuilt import ToolNode
from typing import Literal
from langchain_core.messages import HumanMessage
from ..langgraph.agents import ProductTeamAgents

load_dotenv(override=True)

Agiflow.init(
  app_name="langgraph-agents",
  api_endpoint=os.environ['AGIFLOW_BASE_URL'],
  api_key=os.environ['AGIFLOW_API_KEY'],
)

# Define the function that determines whether to continue or not
def should_continue_changelog(state: MessagesState) -> Literal["changelog_tools", "changelog_summary", END]:
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "changelog_tools"

    content = last_message.content
    if content.endswith('END TURN'):
        return "changelog_summary"
    # Otherwise, we stop (reply to the user)
    return END

# Define the function that determines whether to continue or not
def should_continue_repo(state: MessagesState) -> Literal["repo_tools", "repo_summary", "senior_developer_agent", END]:
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "repo_tools"

    content = last_message.content
    if content.endswith('END TURN'):
        return "repo_summary"

    if len(messages) > 10:
        return END

    return "senior_developer_agent"


def delete_messages(state):
    messages = state['messages']
    return {"messages": [RemoveMessage(id=m.id) for m in messages[1:-1]]}


def create_app():
    agents = ProductTeamAgents()
    from ..tools import Repo, Changelog

    print("## Welcome to the Product Agents")
    print('-------------------------------')

    workflow = StateGraph(MessagesState)

    workflow.add_node("lead_developer_agent", agents.lead_developer_agent)
    workflow.add_node("changelog_tools", ToolNode([Changelog.latest_changes]))
    workflow.add_node("changelog_summary", delete_messages)

    workflow.add_node("senior_developer_agent", agents.senior_developer_agent)
    workflow.add_node("repo_tools", ToolNode([Repo.read_dependencies, Repo.read_source_codes]))
    workflow.add_node("repo_summary", delete_messages)

    workflow.add_node("product_manager_agent", agents.product_manager)

    workflow.set_entry_point("lead_developer_agent")

    workflow.add_conditional_edges(
        "lead_developer_agent",
        should_continue_changelog,
    )

    workflow.add_edge('changelog_tools', 'lead_developer_agent')
    workflow.add_edge('changelog_summary', 'senior_developer_agent')

    workflow.add_conditional_edges(
        "senior_developer_agent",
        should_continue_repo,
    )

    workflow.add_edge('repo_tools', 'senior_developer_agent')
    workflow.add_edge('repo_summary', 'product_manager_agent')

    workflow.add_edge(START, 'lead_developer_agent')

    checkpointer = MemorySaver()

    app = workflow.compile(checkpointer=checkpointer)

    return app

def visualise():
    app = create_app()
    app.get_graph().print_ascii()

@workflow(name="Langgraph-Ops")
def run():
    app = create_app()

    changelog_url = 'https://github.com/langchain-ai/langchain/releases'

    # TODO: change this to your python project directory
    working_dir = os.path.join(Path(os.getcwd()).resolve().parent, 'langchain-chatbot')

    # Use the Runnable
    final_state = app.invoke(
        {
            "messages": [
                HumanMessage(content=f"Upgrade dependencies in {working_dir} directory from reading changelog at {changelog_url}")
            ]
        },
        config={"configurable": { "thread_id": 2 }}
    )

    final = final_state["messages"][-1].content

    # Print results
    print("\n\n########################")
    print("## Here is the result")
    print("########################\n")
    print("Your post copy:")
    print(final)
    return final
