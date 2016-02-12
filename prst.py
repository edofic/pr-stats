import collections
import requests
import time


base = "https://api.github.com"


class PrSt(object):

  def __init__(self, username, password, repo_name, sprint_start, sprint_end):
    self.gh = requests.Session()
    self.gh.auth = (username, password)
    self.repo_name = repo_name
    self.sprint_start = sprint_start
    self.sprint_end = sprint_end

    self.user_stats = collections.defaultdict(
        lambda: collections.defaultdict(int))
    self.opened_prs = []
    self.merged_prs = []
    self.pull_stats = collections.defaultdict(
        lambda: collections.defaultdict(int))

    self.compute()

  def load_all(self, url):
    params = {
        "page": 1,
        "per_page": 100,
        "sort": "updated",
        "direction": "desc",
        "state": "all",
    }
    while True:
      r = self.gh.get(url, params=params)
      body = r.json()
      if len(body) > 0:
        for pr in body:
          yield pr
        params["page"] += 1
      else:
        break

  def load_prs(self):
    return self.load_all("%s/repos/%s/pulls" % (base, self.repo_name))

  def load_comments(self, pr_number):
    return self.load_all("%s/repos/%s/pulls/%d/comments" %
                         (base, self.repo_name, pr_number))

  def take_in_sprint(self, xs):
    for x in xs:
      updated = x.get("updated_at", x.get("created_at", None))
      if updated > self.sprint_end:
        continue
      if updated > self.sprint_start:
        yield x
      else:
        break

  def in_sprint(self, x):
    if x is None:
      return False
    return x > self.sprint_start and x < self.sprint_end

  def compute_pr_stats(self, ids):
    pull_stats_total = collections.defaultdict(int)
    computed_stats = dict()
    for pr_num in ids:
      pr_stats = self.pull_stats[pr_num]
      computed_stats[pr_num] = pr_stats
      for prop in ["additions", "deletions", "changed_files"]:
        pull_stats_total[prop] += pr_stats[prop]
    computed_stats["total"] = pull_stats_total
    return computed_stats

  def compute(self):
    for pr in self.take_in_sprint(self.load_prs()):
      if self.in_sprint(pr["created_at"]):
        self.user_stats[pr["user"]["login"]]["opened-prs"] += 1
        self.opened_prs.append(pr["number"])
        if pr["title"].lower().startswith("quick-fix"):
          self.user_stats[pr["user"]["login"]]["opened-qf"] += 1
      if self.in_sprint(pr["merged_at"]):
        self.merged_prs.append(pr["number"])
      if self.in_sprint(pr["created_at"]) or self.in_sprint(pr["merged_at"]):
        res = self.gh.get("%s/repos/%s/pulls/%d" %
                          (base, self.repo_name, pr["number"]))
        pr = res.json()
        for prop in ["additions", "deletions", "changed_files"]:
          self.pull_stats[pr["number"]][prop] = pr[prop]
        self.pull_stats[pr["number"]]["opener"] = pr["user"]["login"]
      users = set()
      for comment in self.take_in_sprint(self.load_comments(pr["number"])):
        login = comment["user"]["login"]
        self.user_stats[login]["comments"] += 1
        users.add(login)
      for user in users:
        self.user_stats[user]["commented-on-prs"] += 1

    for event in self.take_in_sprint(self.load_all(
                                     "%s/repos/%s/issues/events" %
                                     (base, self.repo_name))):
      login = event["actor"]["login"]
      self.user_stats[login][event["event"]] += 1
      if event["event"] == "merged":
        for prop in ["additions", "deletions", "changed_files"]:
          self.user_stats[login]["merged_" + prop] += (
              self.pull_stats[event["issue"]["number"]][prop])

    for pr_num in self.pull_stats:
      for prop in ["additions", "deletions", "changed_files"]:
        pr = self.pull_stats[pr_num]
        login = pr.get("opener", None)
        if login is None:
          continue
        self.user_stats[login]["opened_" + prop] += pr[prop]

    self.result = {
        "users": self.user_stats,
        "opened PRs": self.compute_pr_stats(self.opened_prs),
        "merged PRs": self.compute_pr_stats(self.merged_prs),
        "timespan": {
            "start": self.sprint_start,
            "end": self.sprint_end,
            "captured_at": int(time.time()),
        },
    }
