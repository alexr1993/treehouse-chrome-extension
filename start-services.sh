#!/bin/bash

# Note:
#
# This does not start rabbitMQ and Redis which are needed to operate the extension
# Spring starts on :8080 by default, as I proxy behind Nginx
#
# Other setup required
#
# 1. Build subreddit-finder-services (java 8, openjdk)
# 2. Ensure python3.5 and pip3 are installed
# 3. Ensure virtualenv is at env
#
repo_dir=~/git/treehouse-chrome-extension
source $repo_dir/reddit-api-worker/env/bin/activate

pip install -r requirements.txt

echo "Starting praw workers"

nWorkers=4

for i in `seq 1 ${nWorkers}`;
do
    nohup python $repo_dir/reddit-api-worker/praw_worker.py &
done
deactivate

echo "Starting spring service"

cd $repo_dir/subreddit-finder-services
nohup ./gradlew bootrun &
