from github import Github
import base64

import time
from github import Github, GithubException
import base64

class GitHubManager:
    def __init__(self, token, repo, branch):
        self.repo = Github(token).get_repo(repo)
        self.branch = branch

    def read_file(self, path):
        file = self.repo.get_contents(path, ref=self.branch)
        return base64.b64decode(file.content).decode().splitlines(), file.sha

    def write_file(self, path, lines, sha, message):
        content = '\n'.join(lines)
        commit = self.repo.update_file(path, message, content, sha, branch=self.branch)
        return commit['commit'].html_url

    def add_rule_to_file(self, path, rule, message, max_retries=3):
        for i in range(max_retries):
            try:
                lines, sha = self.read_file(path)
                if rule in lines:
                    return None, "exists"

                lines.append(rule)
                content = '\n'.join(lines)
                commit = self.repo.update_file(path, message, content, sha, branch=self.branch)
                return commit['commit'].html_url, "added"
            except GithubException as e:
                if e.status == 409:  # Conflict
                    time.sleep(1)
                    continue
                raise e
            except Exception as e:
                raise e
        return None, "failed"

    def check_domain_exists(self, path, domain):
        try:
            lines, _ = self.read_file(path)
            for line in lines:
                if domain in line:
                    return True
            return False
        except Exception as e:
            return False
