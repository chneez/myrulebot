import os

def load_config():
    return {
        "telegram_token": os.environ.get("TELEGRAM_TOKEN"),
        "github_token": os.environ.get("GITHUB_TOKEN"),
        "allowed_users": [int(x) for x in os.environ.get("ALLOWED_USERS", "").split(",")],
        "github": {
            "repo": os.environ.get("GITHUB_REPO"),
            "branch": os.environ.get("GITHUB_BRANCH", "main"),
            "clash_rule_path": os.environ.get("CLASH_RULE_PATH"),
            "loon_rule_path": os.environ.get("LOON_RULE_PATH")
        }
    }
