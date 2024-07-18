from crewai import Crew, Process
from agiflow import Agiflow
from agiflow.opentelemetry import workflow
from dotenv import load_dotenv
import os
from pathlib import Path

from .tasks import DeveloperTasks, ProductManagerTasks
from .agents import ProductTeamAgents
from ..models import Models

load_dotenv()

Agiflow.init(
  app_name="summary-agents",
)

agents = ProductTeamAgents()
lead_developer_agent = agents.lead_developer_agent()
developer_agent = agents.senior_developer_agent()
product_manager_agent = agents.product_manager()
developerTasks = DeveloperTasks()
productManagerTasks = ProductManagerTasks()

@workflow(name="Changelog")
def run():

    print("## Welcome to the Product Crew")
    print('-------------------------------')
    changelog_url = 'https://github.com/langchain-ai/langchain/releases' # input("What is the product website you want a marketing strategy for?\n")

    changelog_analysis = developerTasks.changelog_analysis(lead_developer_agent)
    changelog_review = developerTasks.changelog_review(developer_agent)
    stories_backlog = productManagerTasks.stories_backlog(product_manager_agent)

    # Create Crew responsible for Copy
    product_crew = Crew(
        agents=[
            lead_developer_agent,
            developer_agent,
            product_manager_agent
        ],
        tasks=[
            changelog_analysis,
            changelog_review,
            stories_backlog,
        ],
        manager_agent=None,
        manager_llm=Models.get(),
        process=Process.hierarchical,
        verbose=True,
    )

    product_update = product_crew.kickoff({
        "changelog_url": changelog_url,
        "root": os.path.join(Path(os.getcwd()).resolve().parent, 'langchain-chatbot'),
    })

    # Print results
    print("\n\n########################")
    print("## Here is the result")
    print("########################\n")
    print("Your post copy:")
    print(product_update)
    return product_update
