import post
import subreddit

import asyncio

async def main():
    for i in await subreddit.subParse():
        await post.postParse(i)

asyncio.get_event_loop().run_until_complete(main())