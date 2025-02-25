import praw
import json
import re
import time
from tqdm import tqdm
from datetime import datetime

# Reddit API Crede

reddit = praw.Reddit(
    client_id="YkjnPbh7fE-NVhEMap86pw",
    client_secret="kg0xkGmXuQmQZpo48cW00OkQ4nSxvQ",
    user_agent="LegalAdviceIndiaBot by YOUR_USERNAME"
)

# Access the subreddit
subreddit = reddit.subreddit("LegalAdviceIndia")

# ✅ List of Major Indian Cities & States for Location Extraction
INDIAN_LOCATIONS = [
    "Delhi", "Mumbai", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune", "Jaipur",
    "Ahmedabad", "Lucknow", "Chandigarh", "Patna", "Bhopal", "Thiruvananthapuram", "Guwahati",
    "Nagpur", "Indore", "Ranchi", "Coimbatore", "Kochi", "Goa", "Noida", "Gurgaon",
    "West Bengal", "Tamil Nadu", "Maharashtra", "Karnataka", "Telangana", "Uttar Pradesh",
    "Bihar", "Punjab", "Madhya Pradesh", "Kerala", "Assam", "Odisha", "Haryana"
]

# ✅ Legal category classification based on keywords
LEGAL_CATEGORIES = {
    "Criminal": ["crime", "police", "FIR", "IPC", "arrest", "theft", "fraud", "murder", "assault", "court"],
    "Civil": ["property", "contract", "agreement", "dispute", "real estate", "damage", "tort"],
    "Labour": ["job", "work", "salary", "layoff", "termination", "PF", "gratuity", "employee"],
    "Family": ["divorce", "marriage", "custody", "child", "inheritance", "alimony"],
    "Corporate": ["company", "startup", "business", "compliance", "shares", "GST", "tax", "audit"],
    "Cyber": ["hacking", "online fraud", "privacy", "data protection", "cyber crime"]
}

# ✅ Function to classify posts into legal categories
def classify_legal_category(text):
    for category, keywords in LEGAL_CATEGORIES.items():
        if any(keyword.lower() in text.lower() for keyword in keywords):
            return category
    return "Other"

# ✅ Function to extract valid city/state names
def extract_location(text):
    for location in INDIAN_LOCATIONS:
        if re.search(rf"\b{location}\b", text, re.IGNORECASE):
            return location
    return "Unknown"

# ✅ Function to fetch posts from different time periods
def fetch_posts(limit_per_category=1000):
    all_posts = []

    time_filters = [
        subreddit.top("all", limit=limit_per_category),         # Best posts from all time
        subreddit.controversial("all", limit=limit_per_category), # Heated debates from all time
        subreddit.search("legal", limit=limit_per_category),    # Search-based posts
    ]

    for posts in time_filters:
        for post in tqdm(posts, desc="Fetching posts"):
            post_data = {
                "title": post.title,
                "text": post.selftext,
                "score": post.score,
                "num_comments": post.num_comments,
                "created_utc": datetime.utcfromtimestamp(post.created_utc).strftime('%Y-%m-%d %H:%M:%S'),
                "location": extract_location(post.title + " " + post.selftext),
                "category": classify_legal_category(post.title + " " + post.selftext),
                "permalink": f"https://www.reddit.com{post.permalink}"
            }
            all_posts.append(post_data)

            # Stop once we reach 3K+ posts
            if len(all_posts) >= 3000:
                break
        if len(all_posts) >= 3000:
            break

    # Save to JSON file
    with open("legalad_posts.json", "w", encoding="utf-8") as f:
        json.dump(all_posts, f, indent=4, ensure_ascii=False)

    print(f"✅ Data saved to legaladviceindia_posts.json with {len(all_posts)} records.")

# Run the function
fetch_posts()
