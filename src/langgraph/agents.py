import json
from langgraph.graph import MessagesState
from langchain_core.messages import SystemMessage, ToolMessage
from ..tools import Repo, Changelog
from ..models import Models

class ProductTeamAgents:
    def __init__(self):
        self.llm = Models.get_latest()

    def lead_developer_agent(self, state: MessagesState):
        print('******************** lead developer')
        llm = Models.get_latest().bind_tools([Changelog.latest_changes])
        messages = state['messages']
        messages = [
            SystemMessage(
                content="""
                You are Lead Developer.
                Your goal is analysising code base, plan and decide where code change
                is needed or not.
                """
            ),
            SystemMessage(
                content="""
                Analyze the given library changelog: {changelog_url}.

                Focus on identifying important updates which requires
                code change from the application which are consuming
                this library. Example of important update includes:
                - Function arguments and key arguments changes
                - Function return changes

                Keep in mind, attention to detail is crucial for a comprehensive story.
                Your final summary must include a list of items and a title. You must explicitely
                ended with "END TURN" once you finish the summary.

                Title: Changelog Summary.
                Each item includes.
                - library: library name, no duplication
                - version: latest version of library string
                - implementation_note: given then changelog summary from tool, add note
                for other developer to implement code change and include example.
                Add comment with link to pr_commit.
                """
            ),
        ] + messages
        if messages[-1] and isinstance(messages[-1], ToolMessage):
            messages[-1].content = json.dumps(messages[-1].content)
        response = llm.invoke(messages)
        # We return a list, because this will get added to the existing list
        return {"messages": [response]}

    def senior_developer_agent(self, state: MessagesState):
        print('******************** senior developer')
        llm = Models.get_latest().bind_tools([Repo.read_dependencies, Repo.read_source_codes])
        messages = state['messages']
        messages = [
            SystemMessage(
                content="""
                You are Senior Software Developer.
                Your goal is analysising code base, decide where code change is needed or not.
                """
            ),
            SystemMessage(
                content="""
                From previous changelog summary, analyse codes and dependencies in {working_dir}
                to determine whether update is neccessary.

                You need to check if dependencies need to be updated first. Example of dependecies upgrade needed:
                - Current version is smaller than latest library version

                For each dependency upgrade; check if code changes is needed. Example of code changes needed:
                - Function arguments and keyed arguments from new library version are updated as well.

                Finally, you need to clearly define the scope of change into stories so other developer
                can implement it easily. Only write stories for packages that requires dependencies upgrade or code changes.

                Your final summary must include a list of items. Each item includes.
                - library: library name, no duplication
                - version: latest version of library string
                - implementation_node: given then changelog summary from tool, add note
                for other developer to implement code change and include example.
                Add comment with link to pr_commit.
                - implementation_instruction: include files which need to implement change,
                and clear instruction on how to implement change.
                - complexity: using scrum story points

                You must explicitely ended with "END TURN" once you provide stories.
                """
            ),
        ] + messages
        for message in messages:
            if isinstance(message, ToolMessage):
                message.content = json.dumps(message.content)
        response = llm.invoke(messages)
        # We return a list, because this will get added to the existing list
        return {"messages": [response]}

    def product_manager(self, state: MessagesState):
        print('******************** product manager')
        messages = state['messages']
        messages = [
            SystemMessage(
                content="""
                You are Product Manager.
                Your goal is providing busines requirements, make decision
                and prioritise tasks and features..
                """
            ),
            SystemMessage(
                content="""
                From the stories drafted by developer, prioritize the
                stories in backlog.

                Focus on identifying high impact update or small wins.
                Example of high prioritized stories includes:
                - Story which boost performance
                - Story which fixes critical bugs
                - Story where storypoint is 1 and includes easy change such as dependency update.

                If the story does not fit above criteria. Feel free to drop it.

                Your final summary must include a list of stories from original story. Just need to add priority line item to each stories:
                - library: library name, no duplication
                - version: latest version of library string
                - implementation_node: given then changelog summary from tool, add note
                for other developer to implement code change and include example.
                Add comment with link to pr_commit.
                - implementation_instruction: include files which need to implement change,
                and clear instruction on how to implement change.
                - priority: rank from 0 to 5, with 5 as hightest
                - complexity: using scrum story points

                You must explicitely ended with "END TURN" once you provide stories.
                """
            ),
        ] + messages
        if messages[-1] and isinstance(messages[-1], ToolMessage):
            messages[-1].content = json.dumps(messages[-1].content)

        response = self.llm.invoke(messages)
        # We return a list, because this will get added to the existing list
        return {"messages": [response]}