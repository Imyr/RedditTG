import modules.media as media
import config
import constants.constants as constants

import aiohttp
import asyncio
from telethon import TelegramClient, errors

tgClient = TelegramClient('reddiditbot-session', config.credentials.API_ID, 
                        config.credentials.API_HASH).start(bot_token=config.credentials.BOT_TOKEN)
tgClient.start()
tgClient.parse_mode = 'html' 

async def postMedia(postJson, url_mode):
    mediaJson = postJson["media"]
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
                return(await media.embed.misc(mediaUrl, url_mode))

        if mediaJson["type"] == "embed":
            mediaUrl = postJson["source"]["url"]
            if mediaJson["provider"] == "Gfycat":
                return(await media.embed.gfycat(mediaUrl, url_mode))
            if mediaJson["provider"] == "RedGIFs":
                return(await media.embed.redgifs(mediaUrl, url_mode))
            if mediaJson["provider"] == "Imgur":
                return(await media.embed.imgur(mediaUrl, url_mode))                    
        else:
            print(f"{mediaJson['provider']} | {mediaJson['type']} | {mediaUrl}")
            return
        
    else:
        sourceJson = postJson["source"]
        return(await media.noEmbed(sourceJson, url_mode))

async def postParse(postParsed):

    async with aiohttp.ClientSession() as session:
        if not postParsed["crosspost"]:
            async with session.get(constants.api.POST_URL.format(postParsed["id"])) as response:
                    postJson = (await response.json())["posts"][postParsed["id"]]
        else:
            async with session.get(constants.api.POST_URL.format(postParsed["crosspost"]  )) as response:
                    postJson = (await response.json())["posts"][postParsed["crosspost"]]


    message = config.telegram.MESSAGE_STRUCTURE.format(postParsed["title"], postParsed["author"], 
                                            postParsed["link"], postParsed["link"].split("/")[-5])
    
    try:
        if config.reddit.COMPRESSED:
            media = await postMedia(postJson, True)
            if type(media) == list:
                messageList = (["" for i in media])
                messageList[-1] = message
                message = tuple(messageList)

            try:
                await tgClient.send_file(config.telegram.GROUP_ID, file=media, 
                                        caption=message, force_document=False)
            except errors.rpcerrorlist.WebpageCurlFailedError:
                media = await postMedia(postJson, False)
                await tgClient.send_file(config.telegram.GROUP_ID, file=media, 
                                        caption=message, force_document=False)
            except errors.rpcerrorlist.MediaEmptyError:
                if type(media) == list:
                    for file in media:
                        file.seek(0)
                    await tgClient.send_file(config.telegram.GROUP_ID, file=media, 
                            caption=message, force_document=True)
                elif type(media) == str:
                    media = await postMedia(postJson, False)
                    await tgClient.send_file(config.telegram.GROUP_ID, file=media, 
                            caption=message, force_document=True)
                else:
                    media.seek(0)
                    await tgClient.send_file(config.telegram.GROUP_ID, file=media, 
                            caption=message, force_document=True)

        else:
            media = await postMedia(postJson, False)
            if type(media) == list:
                messageList = (["" for i in media])
                messageList[-1] = message
                message = tuple(messageList)
            await tgClient.send_file(config.telegram.GROUP_ID, file=media, 
                                caption=message, force_document=True)

        print(config.telegram.LOG_STRUCTURE.format("NORMAL", postParsed['id'][3:], postParsed['title'].ljust(20)[0:20], postParsed["link"].split("/")[-5]))
    
    except ValueError as e:
        print(config.telegram.LOG_STRUCTURE.format("VALERR", postParsed['id'][3:], postParsed['title'].ljust(20)[0:20], postParsed["link"].split("/")[-5]))
        await asyncio.sleep(10)
    except Exception as e:
        print(config.telegram.LOG_STRUCTURE.format("---ERR", postParsed['id'][3:], postParsed['title'].ljust(20)[0:20], postParsed["link"].split("/")[-5]))
        print(e)