import modules.post as post
import modules.subreddit as subreddit
from config import reddit

import asyncio

async def main():
    for sub in reddit.SUBREDDIT_LIST:
        for i in await subreddit.subParse(sub):
            await post.postParse(i)

asyncio.get_event_loop().run_until_complete(main())