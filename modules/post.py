import modules.media as media
import config
import constants.constants as constants

import aiohttp
from telethon import TelegramClient, errors

tgClient = TelegramClient('reddiditbot-session', config.credentials.API_ID, 
                        config.credentials.API_HASH).start(bot_token=config.credentials.BOT_TOKEN)
tgClient.start()
tgClient.parse_mode = 'html' 

async def postMedia(postJson, url_mode):
    mediaJson = postJson["media"]
    try:

        if mediaJson:
            if mediaJson["type"] == "video":
                mediaUrl = mediaJson["dashUrl"]
                return(await media.redditHost.video(mediaUrl, url_mode))

            if mediaJson["type"] == "gallery":
                return(await media.redditHost.gallery(mediaJson, url_mode))
                
            mediaUrl = mediaJson["content"]
            if mediaJson["type"] in ["image", "gifvideo"]:
                try:
                    return(await media.redditHost.reddit(mediaUrl, url_mode))
                except aiohttp.client_exceptions.InvalidURL:
                    mediaUrl = postJson["source"]["url"]
                    return(await media.embed.imgur(mediaUrl, url_mode))

            if mediaJson["type"] == "embed":
                if mediaJson["provider"] == "Gfycat":
                    return(await media.embed.gfycat(mediaUrl, url_mode))
                if mediaJson["provider"] == "RedGIFs":
                    return(await media.embed.redgifs(mediaUrl, url_mode))
            else:
                print(f"{mediaJson['provider']} | {mediaJson['type']} | {mediaUrl}")
                return
            
        else:
            sourceJson = postJson["source"]
            return(await media.noEmbed(sourceJson, url_mode))

    except Exception as e:
        print(e)
        return

async def postParse(postParsed):
    print("NORMAL | ", end="") 
    print(f"https://redd.it/{postParsed['id'][3:]} | {postParsed['title'].ljust(20)[0:20]} | ", end="")

    async with aiohttp.ClientSession() as session:
        if postParsed["crosspost"]:
            postParsed["id"] = postParsed["crosspost"]
        async with session.get(constants.api.POST_URL.format(postParsed["id"])) as response:
                postJson = (await response.json())["posts"][postParsed["id"]]

    message = config.telegram.MESSAGE_STRUCTURE.format(postParsed["title"], postParsed["author"], 
                                            postParsed["link"], postParsed["link"].split("/")[-5])

    if config.reddit.COMPRESSED:
        media = await postMedia(postJson, True)

        try:
            await tgClient.send_message(config.telegram.GROUP_ID, message, 
                                        file=media, force_document=False, link_preview=False)
        except Exception:
            print("TRYING | UNCOMP | ", end="")
            media = await postMedia(postJson, False)
            await tgClient.send_message(config.telegram.GROUP_ID, message, 
                            file=media, force_document=False, link_preview=False)

    else:

        media = await postMedia(postJson, False)
        await tgClient.send_file(config.telegram.GROUP_ID, 
                            file=media, force_document=True)
        await tgClient.send_message(config.telegram.GROUP_ID, 
                                message, link_preview=False)