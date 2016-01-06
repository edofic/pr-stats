import collections
import json
import os
import requests
import sys


base = "https://api.github.com"

gh = requests.Session()
gh.auth = (os.environ["GITHUB_USERNAME"], os.environ["GITHUB_PASSWORD"])

repo_name, sprint_start, sprint_end = sys.argv[1:]


def load_all(url):
  params = {
      "page": 1,
      "per_page": 100,
      "sort": "updated",
      "direction": "desc",
      "state": "all",
  }
  while True:
    r = gh.get(url, params=params)
    body = r.json()
    if len(body) > 0:
      for pr in body:
        yield pr
      params["page"] += 1
    else:
      break


def load_prs():
  return load_all("%s/repos/%s/pulls" % (base, repo_name))


def load_comments(pr_number):
  return load_all("%s/repos/%s/pulls/%d/comments" %
                  (base, repo_name, pr_number))


def take_in_sprint(xs):
  for x in xs:
    updated = x.get("updated_at", x.get("created_at", None))
    if updated > sprint_end:
      continue
    if updated > sprint_start:
      yield x
    else:
      break


def in_sprint(x):
  if x is None:
    return False
  return x > sprint_start and x < sprint_end

stats = collections.defaultdict(lambda: collections.defaultdict(int))
opened_prs = []
merged_prs = []
pull_stats = collections.defaultdict(lambda: collections.defaultdict(int))


def compute_pr_stats(ids):
  pull_stats_total = collections.defaultdict(int)
  computed_stats = dict()
  for pr_num in ids:
    pr_stats = pull_stats[pr_num]
    computed_stats[pr_num] = pr_stats
    for prop in ["additions", "deletions", "changed_files"]:
      pull_stats_total[prop] += pr_stats[prop]
  computed_stats["total"] = pull_stats_total
  return computed_stats


for pr in take_in_sprint(load_prs()):
  if in_sprint(pr["created_at"]):
    stats[pr["user"]["login"]]["opened-prs"] += 1
    opened_prs.append(pr["number"])
  if in_sprint(pr["merged_at"]):
    merged_prs.append(pr["number"])
  if in_sprint(pr["created_at"]) or in_sprint(pr["merged_at"]):
    res = gh.get("%s/repos/%s/pulls/%d" % (base, repo_name, pr["number"]))
    pr = res.json()
    for prop in ["additions", "deletions", "changed_files"]:
      pull_stats[pr["number"]][prop] = pr[prop]
    pull_stats[pr["number"]]["opener"] = pr["user"]["login"]
  users = set()
  for comment in take_in_sprint(load_comments(pr["number"])):
    login = comment["user"]["login"]
    stats[login]["comments"] += 1
    users.add(login)
  for user in users:
    stats[user]["commented-on-prs"] += 1

for event in take_in_sprint(load_all("%s/repos/%s/issues/events" %
                                     (base, repo_name))):
  login = event["actor"]["login"]
  stats[login][event["event"]] += 1
  if event["event"] == "merged":
    for prop in ["additions", "deletions", "changed_files"]:
      stats[login]["merged_" + prop] += (
          pull_stats[event["issue"]["number"]][prop])


for pr_num in pull_stats:
  for prop in ["additions", "deletions", "changed_files"]:
    stats[login]["opened_" + prop] += pull_stats[pr_num][prop]

result = {
    "users": stats,
    "opened PRs": compute_pr_stats(opened_prs),
    "merged PRs": compute_pr_stats(merged_prs),
}
print(json.dumps(result, indent=2))
