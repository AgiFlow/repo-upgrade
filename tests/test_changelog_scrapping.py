import pytest
from src.tools import Changelog, File
import json

# class TestChangelogDiffer:
#     @pytest.fixture(autouse=True)
#     def setup(self):
#         self.changelog = Changelog()

#     def test_diff(self):
#         result = self.changelog.latest_changes('https://github.com/langchain-ai/langchain/releases')
#         assert len(result) == 10


class TestFile:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.file = File()

    def test_dependencies(self):
        result = self.file.read_dependencies('.')
        assert len(result) == 1
