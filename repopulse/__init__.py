"""RepoPulse - GitHub ecosystem automation and template sync tool."""
import os, json, urllib.request, base64, time
from datetime import datetime

class RepoPulse:
    def __init__(self, token):
        self.token = token
        self.headers = {"Authorization": "token " + token, "Accept": "application/vnd.github+json"}
        self.hput = {**self.headers, "Content-Type": "application/json"}

    def get_repos(self):
        url = "https://api.github.com/users/Raphasha27/repos?per_page=100&sort=full_name"
        return [r for r in json.loads(urllib.request.urlopen(urllib.request.Request(url, headers=self.headers)).read()) if not r.get("fork")]

    def sync_file(self, repo, branch, path, content):
        url = "https://api.github.com/repos/Raphasha27/" + repo + "/contents/" + path
        b64 = base64.b64encode(content.encode()).decode()
        payload = {"message": "chore: sync " + path + " via RepoPulse", "content": b64, "branch": branch}
        try:
            r = urllib.request.urlopen(urllib.request.Request(url + "?ref=" + branch, headers=self.headers))
            existing = json.loads(r.read())
            payload["sha"] = existing["sha"]
        except:
            pass
        req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=self.hput, method="PUT")
        try:
            urllib.request.urlopen(req)
            return True
        except:
            return False

    def run(self, files=None):
        if files is None:
            files = {".gitattributes": "* text=auto\\n*.py text eol=lf\\n*.md text eol=lf\\n"}
        repos = self.get_repos()
        results = {"checked": 0, "synced": 0}
        for repo in repos:
            branch = json.loads(urllib.request.urlopen(urllib.request.Request("https://api.github.com/repos/Raphasha27/" + repo["name"], headers=self.headers)).read()).get("default_branch", "main")
            for path, content in files.items():
                if self.sync_file(repo["name"], branch, path, content):
                    results["synced"] += 1
            results["checked"] += 1
            time.sleep(0.5)
        return results

if __name__ == "__main__":
    pulse = RepoPulse("your_token_here")
    print(json.dumps(pulse.run(), indent=2))
