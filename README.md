# PrStats

This is a simple command line tool to compute some metrics of pull requests on a GitHub repository inside a time span.

## Usage
Currently only username/password authentication is implemented so you will need to provide your GitHub credentials in the environment

    export GITHUB_USERNAME=edofic
    export GITHUB_PASSWORD=supersecret password

And then supply repository name, start date, and end date

    python main.py google/ggrc-core "2015-12-29T00:00:00Z" "2016-02-12T00:00:00Z"

This will dump JSON formatted stats to the console.

### AWS Lambda

You can also package this tool as an AWS Lambda function. For this you will need to provide a `prst_config.py` file - see `prst_config.sample` and then run `make dist` or `make dockerdist` for a completely isolated built.

The `prst_config.py` contains an aditional parameter: `put_url`. If present, the lambda will HTTP PUT the results to the given url after it's done.


## Viewing the results

The `view` folder contains a very simple Angular.js based renderer for the results. It is a static page and takes URL to stats as a query string.
Example:

    python main.py google/ggrc-core "2015-12-29T00:00:00Z" "2016-02-12T00:00:00Z" >> stats
    python -m SimpleHTTPServer . &
    open "http://localhost:8000/view/public/?%2Fstats"
