#!/bin/bash

repo_dir=~/git/reddit-bot

nWorkers=4

source $repo_dir/env/bin/activate

for i in `seq 1 ${nWorkers}`;
do
    nohup python $repo_dir/src/praw_worker.py &
done

nohup java -jar $repo_dir/subreddit-finder-services/build/libs/gs-spring-boot-0.1.0.jar &
