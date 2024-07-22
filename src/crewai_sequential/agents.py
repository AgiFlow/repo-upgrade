from textwrap import dedent
from crewai import Agent
from ..tools import Changelog, Repo
from ..models import Models

class ProductTeamAgents:
    def __init__(self):
        self.llm = Models.get()

    def lead_developer_agent(self):
        return Agent(
            role="Lead Developer",
            goal=dedent("""\
                Analysising code base, plan and decide where code change
                is needed or not."""),
            backstory=dedent("""\
                As lead software developer,
                you are specialize in evaluating code change
                for product requirements."""),
            tools=[
                Changelog.latest_changes,
            ],
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )

    def senior_developer_agent(self):
        return Agent(
            role="Senior Software Developer",
            goal=dedent("""\
                Analysising code base, decide where code change
                is needed or not."""),
            backstory=dedent("""\
                As senior software developer,
                you are specialize in evaluating code change
                for product requirements."""),
            tools=[
                Repo.read_dependencies,
                Repo.read_source_codes,
            ],
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )

    def product_manager(self):
        return Agent(
            role="Product Manager",
            goal=dedent("""\
                Providing busines requirements, make decision
                and prioritise tasks and features."""),
            backstory=dedent("""\
                As a product manager from big tech,
                you are specialize in liasing with business requirements
                to priority development tasks and features."""),
            allow_delegation=False,
            llm=self.llm,
            verbose=True
        )
