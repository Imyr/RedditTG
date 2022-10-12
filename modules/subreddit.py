import config 
import constants.constants as constants

import aiohttp

async def subParse(subName):
    postList = []
    async with aiohttp.ClientSession() as session:
        async with session.get(constants.api.SUBREDDIT_URL.format(subName), 
                                headers=constants.api.HEADERS, 
                                params=config.reddit.PARAMETERS) as response:
            respJson = await response.json()
    
    for id in respJson["postIds"]:
        post = respJson["posts"][id]
        
        if post["crosspostRootId"]:
            crosspost = post["crosspostRootId"]
        else:
            crosspost = False            

        for tag in config.reddit.FILTERS:
            if not (post[tag] == config.reddit.FILTERS[tag]):
                print("AD/PIN | ", end="")
                print(f"https://redd.it/{post['id'][3:9]} | {post['title'].ljust(20)[0:20]} | None")
                break
        else:
            postList.append({
                    "id": post["id"],
                    "author": post["author"],
                    "title": post["title"],
                    "link": post["permalink"],
                    "crosspost": crosspost
                    })

    return(postList)