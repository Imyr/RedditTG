import media
import config
import constants

import aiohttp
from telethon import TelegramClient, events, sync

tgClient = TelegramClient('reddiditbot-session', config.credentials.API_ID, 
                        config.credentials.API_HASH).start(bot_token=config.credentials.BOT_TOKEN)
tgClient.start()
tgClient.parse_mode = 'html' 

async def postMedia(postJson):
    mediaJson = postJson["media"]

    try:
        if mediaJson:
            if mediaJson["type"] == "video":
                mediaUrl = mediaJson["dashUrl"]
                return(await media.redditvideo(mediaUrl))

            if mediaJson["type"] == "gallery":
                metadataJson = mediaJson["mediaMetadata"]
                return(await media.gallery(metadataJson))
                
            mediaUrl = mediaJson["content"]
            if mediaJson["type"] in ["image", "gifvideo"]:
                try:
                    return(await media.reddit(mediaUrl))
                except aiohttp.client_exceptions.InvalidURL:
                    mediaUrl = postJson["source"]["url"]
                    return(await media.imgur(mediaUrl))

            if mediaJson["type"] == "embed":
                if mediaJson["provider"] == "Gfycat":
                    return(await media.gfycat(mediaUrl))
                if mediaJson["provider"] == "RedGIFs":
                    return(await media.redgifs(mediaUrl))
            else:
                print(f"{mediaJson['provider']} | {mediaJson['type']} | {mediaUrl}")
                return None
            
        else:
            sourceJson = postJson["source"]
            return(await media.noEmbed(sourceJson))

    except Exception as e:
        print(e)
        return None

async def postParse(postParsed):
    print("NORMAL | ", end="") 
    print(f"https://redd.it/{postParsed['id'][3:]} | {postParsed['title'].ljust(20)[0:20]} | ", end="")
    async with aiohttp.ClientSession() as session:
        async with session.get(constants.api.POST_URL.format(postParsed["id"])) as response:
            postJson = (await response.json())["posts"][postParsed["id"]]

    message = config.telegram.MESSAGE_STRUCTURE.format(postParsed["title"], postParsed["author"], 
                                            postParsed["link"], config.reddit.SUBREDDIT_LINK.split("/")[-2])
    await tgClient.send_message(config.telegram.GROUP_ID, message, 
                                file=await postMedia(postJson), 
                                force_document=True, link_preview=False)