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
  app_name="crewai-hierarchical-agents",
)

manager_model = Models.get()
agents = ProductTeamAgents()
developer_agent = agents.developer_agent()
product_manager_agent = agents.product_manager()
developerTasks = DeveloperTasks()
productManagerTasks = ProductManagerTasks()

@workflow(name="CrewAI Hierarchical")
def run():

    print("## Welcome to the Product Crew")
    print('-------------------------------')
    changelog_url = 'https://github.com/langchain-ai/langchain/releases' # input("What is the product website you want a marketing strategy for?\n")

    changelog_analysis = developerTasks.changelog_analysis(developer_agent)
    changelog_review = developerTasks.changelog_review(developer_agent)
    stories_backlog = productManagerTasks.stories_backlog(product_manager_agent)

    # Create Crew responsible for Copy
    product_crew = Crew(
        agents=[
            developer_agent,
        ],
        tasks=[
            changelog_analysis,
            changelog_review,
            stories_backlog,
        ],
        manager_agent=product_manager_agent,
        process=Process.hierarchical,
        verbose=True,
    )

    product_update = product_crew.kickoff({
        "changelog_url": changelog_url,
        "working_dir": os.path.join(Path(os.getcwd()).resolve().parent, 'langchain-chatbot'),
    })

    # Print results
    print("\n\n########################")
    print("## Here is the result")
    print("########################\n")
    print("Your post copy:")
    print(product_update)
    return product_update
