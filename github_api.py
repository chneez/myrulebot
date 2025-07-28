from github import Github
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
