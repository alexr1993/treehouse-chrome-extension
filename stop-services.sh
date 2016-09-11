kill $(ps aux | grep reddit-api-worker | awk '{print $2}')
kill $(ps aux | grep subreddit-finder-services | awk '{print $2}')

