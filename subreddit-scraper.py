import os
import requests
from dotenv import load_dotenv
import json
import datetime

OATH_ENDPOINT = 'https://oauth.reddit.com'

# authenticate -------------------------------------------------------------------------
load_dotenv()
CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
SECRET_KEY = os.getenv("REDDIT_SECRET_KEY")
USERNAME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")

auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_KEY)
data = {
    "grant_type": "password",
    "username": USERNAME,
    "password": PASSWORD
}
user_agent = f"bot for reddit by /u/{USERNAME}"
headers = {'User-Agent': user_agent}

res = requests.post('https://www.reddit.com/api/v1/access_token',
    auth=auth, data=data, headers=headers)

TOKEN_ID = res.json()['access_token']

# main functions -----------------------------------------------------------------------
def get_new_posts(subreddit, limit):
    new_subreddit_url =  OATH_ENDPOINT + f'/r/{subreddit}/new'
    if limit > 100: limit = 100 # 100 is the max
    params = {
        'limit': limit
    }
    headers = {
        'User-Agent': user_agent,
        'Authorization': 'Bearer ' + TOKEN_ID
    }
    response = requests.get(new_subreddit_url, headers=headers, params=params)
    
    posts = response.json()['data']['children']
    # print(json.dumps(response.json(), indent=2, sort_keys=True))
    return posts

def save_to_markdown(data, output_path, output_filename):
    found = 0
    lines = []

    for post in data:
        pdata = post['data']
        id = pdata['id']
        title = pdata['title']
        content = pdata['selftext']
        url = pdata['url']
        flair_text = pdata['link_flair_text']

        lines.append(f"{url}\n")
        lines.append(f"# {title}\n\n")
        lines.append(f"Tag: {flair_text}\n")
        lines.append(f"\n{content}\n\n")
        lines.append(f"{'-'*3}\n")
        lines.append(f"\n\n")

        found += 1
    print(f"found: {found}")

    # save to markdown file
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    output_path = f"{output_path}/{output_filename}"

    try:
        out_file = open(output_path, 'w', encoding="utf-8", errors='replace')
        out_file.writelines(lines)
    except Exception:
        print("Cannot write to file")
    else:
        out_file.close()
        print(f"Saved data to {output_path}")

# usage sample -------------------------------------------------------------------------

# subreddit = "redditdev"
# now_utc = round(datetime.datetime.now().timestamp())
# now = datetime.datetime.fromtimestamp(now_utc).strftime("%m%d%Y%H%M%S")
# output_path = os.path.join(os.getcwd(), subreddit)
# new_posts = get_new_posts(subreddit, 100)
# save_to_markdown(new_posts, output_path, f"{now}.md")