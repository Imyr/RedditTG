import modules.media as media
import config
import constants.constants as constants

import aiohttp
from telethon import TelegramClient, events, sync

tgClient = TelegramClient('reddiditbot-session', config.credentials.API_ID, 
                        config.credentials.API_HASH).start(bot_token=config.credentials.BOT_TOKEN)
tgClient.start()
tgClient.parse_mode = 'html' 

async def postMedia(postJson):
    return
    mediaJson = postJson["media"]

    try:

        if mediaJson:
            if mediaJson["type"] == "video":
                mediaUrl = mediaJson["dashUrl"]
                return(await media.redditHost.video(mediaUrl))

            if mediaJson["type"] == "gallery":
                metadataJson = mediaJson["mediaMetadata"]
                return(await media.redditHost.gallery(metadataJson))
                
            mediaUrl = mediaJson["content"]
            if mediaJson["type"] in ["image", "gifvideo"]:
                try:
                    return(await media.redditHost.reddit(mediaUrl))
                except aiohttp.client_exceptions.InvalidURL:
                    mediaUrl = postJson["source"]["url"]
                    return(await media.embed.imgur(mediaUrl))

            if mediaJson["type"] == "embed":
                if mediaJson["provider"] == "Gfycat":
                    return(await media.embed.gfycat(mediaUrl))
                if mediaJson["provider"] == "RedGIFs":
                    return(await media.embed.redgifs(mediaUrl))
            else:
                print(f"{mediaJson['provider']} | {mediaJson['type']} | {mediaUrl}")
                return
            
        else:
            sourceJson = postJson["source"]
            return(await media.noEmbed(sourceJson))

    except Exception as e:
        print(e)
        return

async def postParse(postParsed):
    print("NORMAL | ", end="") 
    print(f"https://redd.it/{postParsed['id'][3:]} | {postParsed['title'].ljust(20)[0:20]} | ", end="")

    async with aiohttp.ClientSession() as session:
        async with session.get(constants.api.POST_URL.format(postParsed["id"])) as response:
            postJson = (await response.json())["posts"][postParsed["id"]]

    message = config.telegram.MESSAGE_STRUCTURE.format(postParsed["title"], postParsed["author"], 
                                            postParsed["link"], postParsed["link"].split("/")[-5])
    await tgClient.send_message(config.telegram.GROUP_ID, message, 
                                file=await postMedia(postJson), 
                                force_document=True, link_preview=False)