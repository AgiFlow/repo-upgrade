from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from langchain.tools import tool
import os

class Changelog():

    @staticmethod
    def get_pr_info(ele, browser):
        mes = ele.text
        pr = ele.find('a')
        if pr is not None:
            if pr.has_attr('href'):
                pr_link = pr['href']
                page = browser.new_page()
                page.goto(pr_link + '/files')
                html = page.content()
                soup = BeautifulSoup(html, 'html.parser')
                added = []
                for ele in soup.find_all(lambda tag: tag.name=='span' and tag.has_attr('data-code-marker') and tag['data-code-marker']=="+"):
                    added.append(ele.text)
                removed = []
                for ele in soup.find_all(lambda tag: tag.name=='span' and tag.has_attr('data-code-marker') and tag['data-code-marker']=="-"):
                    removed.append(ele.text)
            pr_commit = pr.text
            if pr_commit is not None:
                mes.replace(pr_commit, '')
            return {
                "message": mes,
                "pr_link": pr_link,
                "pr_commit": pr_commit,
                "added": added,
                "removed": removed,
            }
        else:
            return {
                "message": mes,
            }

    @staticmethod
    @tool
    def latest_changes(url: str):
        """
            Get latest changes from library changelog.
            :param str url: The url of the web page
        """
        url = url.replace('"', '')
        with sync_playwright() as playwright:
            chromium = playwright.chromium
            browser = chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)  # Navigate to the old url
            html = page.content()

            soup = BeautifulSoup(html, 'html.parser')
            releases = []
            for ele in soup.find_all('section'):
                title = ele.find('h2').text
                [package, version] = title.split('==')
                body = ele.find(lambda tag: tag.name=='div' and tag.has_attr('data-test-selector') and tag['data-test-selector']=="body-content")
                changes = []
                for mes_ele in body.find_all('p'):
                    changes.append(Changelog.get_pr_info(mes_ele, browser))

                releases.append({
                    'package': package,
                    'version': version,
                    'changes': changes,
                })

        return releases


class Repo():

    @staticmethod
    @tool
    def read_dependencies(root):
        """
            List dependencies from package manager file
            :param str root: The root directory of the project
        """
        dependencies_fnames = ['pyproject.toml', 'requirements.txt']
        dependencies = []
        for root, dirs, files in os.walk(root):
            for file in files:
                for fname in dependencies_fnames:
                    file_path = os.path.join(root, file)
                    if file.endswith(fname) and '.venv' not in file_path:
                        with open(file_path) as f:
                            content = f.read()
                            dependencies.append({
                                "file_path": file_path ,
                                "content": content,
                            })
        return dependencies

    @staticmethod
    @tool
    def read_source_codes(root):
        """
            List source codes with content
            :param str root: The root directory of the project
        """
        codes = []
        for root, dirs, files in os.walk(root):
            for file in files:
                file_path = os.path.join(root, file)
                if file.endswith('.py') and '.venv' not in file_path:
                    with open(file_path) as f:
                        content = f.read()
                        codes.append({
                            "file_path": file_path ,
                            "content": content,
                        })
        return codes
