import modules.post as post
import modules.subreddit as subreddit
from config import reddit

import os
import shutil
import asyncio

async def bot(sub):
    for i in await subreddit.subParse(sub):
        await post.postParse(i)

async def main():
    if os.path.exists("temp"):
        shutil.rmtree("temp")
    os.mkdir("temp")
    await asyncio.gather(*[bot(sub) for sub in reddit.SUBREDDIT_LIST])
    

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())