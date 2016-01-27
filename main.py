import time
import json
import os
import prst
import requests
import sys


try:
  import prst_config
except:
  class Config(object):
    pass
  prst_config = Config()


# for running on AWS Lambda
def lambda_handler(event, context):
  stats = prst.PrSt(prst_config.username, prst_config.password,
                    prst_config.repo_name,
                    prst_config.sprint_start, prst_config.sprint_end)
  url = getattr(prst_config, "put_url", None)
  if url is not None:
    url = url.format(time=int(time.time()))
    requests.put(url, json=stats.result)
  return json.dumps(stats.result, indent=2)

if __name__ == "__main__":
  prst_config.username = os.environ.get("GITHUB_USERNAME",
                                        prst_config.username)
  prst_config.password = os.environ.get("GITHUB_PASSWORD",
                                        prst_config.password)
  prst_config.repo_name, prst_config.sprint_start, prst_config.sprint_end = \
      sys.argv[1:]
  print(lambda_handler(None, None))
