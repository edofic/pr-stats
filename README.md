# PrStats

This is a simple command line tool to compute some metrics of pull requests on a GitHub repository inside a time span.

## Usage
Currently only username/password authentication is implemented so you will need to provide your GitHub credentials in the environment

    export GITHUB_USERNAME=edofic
    export GITHUB_PASSWORD=supersecret password

And then supply repository name, start date, and end date

    python main.py google/ggrc-core "2015-12-29T00:00:00Z" "2016-02-12T00:00:00Z"

This will dump JSON formatted stats to the console.
