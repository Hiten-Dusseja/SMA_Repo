import praw
import json
from datetime import datetime
import re

# Authentication
reddit = praw.Reddit(
    client_id="YkjnPbh7fE-NVhEMap86pw",
    client_secret="kg0xkGmXuQmQZpo48cW00OkQ4nSxvQ",
    user_agent="LegalAdviceIndiaBot by YOUR_USERNAME"
)

# Access the subreddit
subreddit = reddit.subreddit("LegalAdviceIndia")

# Function to extract location (basic example)
def extract_location(text):
    # Example list of Indian cities; expand this list as needed
    locations = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Pune", "Noida", "Gurgaon"]
    for location in locations:
        if location.lower() in text.lower():
            return location
    return "Unknown"

# Fetch posts in batches
data = []
limit = 2000  # Number of posts to fetch
batch_size = 100  # PRAW allows a maximum of 100 posts per request
count = 0
after = None  # Used to paginate backward

print(f"Fetching up to {limit} posts from r/LegalAdviceIndia...\n")

while count < limit:
    # Fetch a batch of posts
    posts = subreddit.new(limit=batch_size, params={"after": after})

    batch_data = []
    for post in posts:
        count += 1
        post_data = {
            "title": post.title,
            "author": str(post.author),
            "url": post.url,
            "score": post.score,
            "created_utc": post.created_utc,
            "created_date": datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
            "num_comments": post.num_comments,
            "selftext": post.selftext,
            "id": post.id,
            "subreddit": str(post.subreddit),
            "location": extract_location(post.selftext + " " + post.title),  # Combine title and selftext
        }
        batch_data.append(post_data)

        # Stop if we reach the limit
        if count >= limit:
            break

    # Append the current batch to the main dataset
    data.extend(batch_data)

    # Set the "after" parameter to fetch the next batch
    if batch_data:
        after = batch_data[-1]["id"]
    else:
        break

    print(f"Fetched {len(batch_data)} posts. Total so far: {count}.\n")

# Save to JSON file
file_name = "legal_advice_india_all.json"
with open(file_name, "w", encoding="utf-8") as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

print(f"Data saved to '{file_name}' with {len(data)} entries.")
