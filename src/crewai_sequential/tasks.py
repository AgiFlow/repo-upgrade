from crewai import Task
from textwrap import dedent

class DeveloperTasks:
    def changelog_analysis(self, agent):
        return Task(
            description=dedent("""\
                Analyze the given library changelog: {changelog_url}.

                Focus on identifying important updates which requires
                code change from the application which are consuming
                this library. Example of important update includes:
                - Function arguments and key arguments changes
                - Function return changes

                Keep in mind, attention to detail is crucial for a comprehensive story.
                """),
            expected_output=dedent(f"""\
                Your final summary must include a list of items and a title.
                Title: Changelog summary.
                Each item includes.
                - library: library name, no duplication
                - version: latest version of library string
                - implementation_note: given then changelog summary from tool, add note
                for other developer to implement code change and include example.
                Add comment with link to pr_commit.
                """),
            agent=agent,
        )

    def changelog_review(self, agent):
        return Task(
            description=dedent("""\
                From previous changelog summary, analyse codes and dependencies in {working_dir}
                to determine whether update is neccessary.

                You need to check if dependencies need to be updated first. Example of dependecies upgrade needed:
                - Current version is smaller than latest library version

                For each dependency upgrade; check if code changes is needed. Example of code changes needed:
                - Function arguments and keyed arguments from new library version are updated as well.

                Finally, you need to clearly define the scope of change into stories so other developer
                can implement it easily. Only write stories for packages that requires dependencies upgrade or code changes.
                """),
            expected_output=dedent(f"""\
                Your final summary must include a list of items. Each item includes.
                - library: library name, no duplication
                - version: latest version of library string
                - implementation_node: given then changelog summary from tool, add note
                for other developer to implement code change and include example.
                Add comment with link to pr_commit.
                - implementation_instruction: include files which need to implement change,
                and clear instruction on how to implement change.
                - complexity: using scrum story points
                """),
            agent=agent,
        )

class ProductManagerTasks:
    def stories_backlog(self, agent):
        return Task(
            description=dedent("""\
                From the stories drafted by developer, prioritize the
                stories in backlog.

                Focus on identifying high impact update or small wins.
                Example of high prioritized stories includes:
                - Story which boost performance
                - Story which fixes critical bugs
                - Story where storypoint is 1 and includes easy change such as dependency update.

                If the story does not fit above criteria. Feel free to drop it.
                """),
            expected_output=dedent(f"""\
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
                """),
            agent=agent,
        )
