import os
import re
import shutil
import aiohttp
import aiofiles
import requests
import subprocess
from io import BytesIO
from bs4 import BeautifulSoup as bs

class embed:
    async def gfycat(mediaUrl, url_mode):
        async with aiohttp.ClientSession() as session:
            async with session.get(mediaUrl) as response:
                gyfcatEmbed = requests.utils.unquote(re.search(r'\?src=(.*)&display_name=Gfycat', str(await response.read())).group(1))
            async with session.get(gyfcatEmbed) as response:
                mediaUrl = requests.utils.unquote(re.search(r'"video":{"@type":"VideoObject","author":"anonymous","contentUrl":"(.*)","creator":"anonymous",', str(await response.read())).group(1))
            if url_mode:
                return(mediaUrl)
            async with session.get(gyfcatEmbed) as response:
                media = BytesIO(await response.read())
        media.name = mediaUrl.split("/")[-1].split("?")[0]
        return(media)

    async def imgur(mediaUrl, url_mode):
        async with aiohttp.ClientSession() as session:
            async with session.get(mediaUrl) as response:
                gyfcatEmbed = requests.utils.unquote(re.search(r'\?src=(.*)&display_name=Gfycat', str(await response.read())).group(1))
            async with session.get(gyfcatEmbed) as response:
                mediaUrl = requests.utils.unquote(re.search(r'"video":{"@type":"VideoObject","author":"anonymous","contentUrl":"(.*)","creator":"anonymous",', str(await response.read())).group(1))
            if url_mode:
                return(mediaUrl)
            async with session.get(gyfcatEmbed) as response:
                media = BytesIO(await response.read())
        media.name = mediaUrl.split("/")[-1].split("?")[0]
        return(media)

    async def misc(mediaUrl, url_mode):
        if url_mode:
            return(mediaUrl)
        async with aiohttp.ClientSession() as session:
            async with session.get(mediaUrl) as response:
                media = BytesIO(await response.read())
        media.name = mediaUrl.split("/")[-1].split("?")[0]
        return(media)
    
    async def redgifs(mediaUrl, url_mode):
        async with aiohttp.ClientSession() as session:
            async with session.get(mediaUrl) as response:
                redgifsEmbed = requests.utils.unquote(re.search(r'<iframe src="(.*)" frameborder="0"', str(await response.read())).group(1))
            async with session.get(redgifsEmbed) as response:
                mediaUrl = requests.utils.unquote(re.search(r'<meta property="og:video" content="(.*?)"><meta property="og:video:type" content="video/mp4">', str(await response.read())).group(1).replace("&amp;", "&"))
            async with session.get(redgifsEmbed) as response:
                media = BytesIO(await response.read())
                media.name = redgifsEmbed.split("/")[-1].split("?")[0]             
        return(media)

class redditHost:
    async def reddit(mediaUrl, url_mode):
        if url_mode:
            return(mediaUrl)
        async with aiohttp.ClientSession() as session:
            async with session.get(mediaUrl) as response:
                media = BytesIO(await response.read())
        media.name = mediaUrl.split("/")[-1].split("?")[0]
        return(media)

    async def video(mediaUrl, url_mode):
        async with aiohttp.ClientSession() as session:
            async with session.get(mediaUrl) as response:
                parsedResponse = bs(await response.read(), "lxml")
        width = 0
        try:
            for i in parsedResponse.find("adaptationset", contenttype="video").find_all("representation"):
                if int(i.attrs["width"]) > width:
                    videoUrl = mediaUrl.split("DASHPlaylist.mpd")[0] + i.baseurl.text
                    width = int(i.attrs["width"])           
            extension = videoUrl.split(".")[-1].split("?")[0]
        except AttributeError:
            for i in parsedResponse.find("adaptationset").find_all("representation"):
                if int(i.attrs["width"]) > width:
                    videoUrl = mediaUrl.split("DASHPlaylist.mpd")[0] + i.baseurl.text
                    extension = f'{i.attrs["mimetype"].split("/")[-1]}'
                    width = int(i.attrs["width"])
        try:
            audioList = [(i.baseurl.text) for i in parsedResponse.find("adaptationset", contenttype="audio").find_all("representation")]
            audioUrl = mediaUrl.split("DASHPlaylist.mpd")[0] + audioList[-1]
        except AttributeError: 
            if url_mode:
                return(mediaUrl)
            async with aiohttp.ClientSession() as session:
                async with session.get(videoUrl) as response:
                    media = BytesIO(await response.read())
                    media.name = videoUrl.split("/")[-2] + "." + extension
            return(media)
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(videoUrl) as videoResponse:
                    video = await videoResponse.read()
                async with session.get(audioUrl) as audioResponse:
                    audio = await audioResponse.read()                    
                async with aiofiles.open("temp/" + videoUrl.split("/")[-2] + "-vid." + extension, "wb") as f:
                    await f.write(video)
                async with aiofiles.open("temp/" + videoUrl.split("/")[-2] + "-aud." + extension, "wb") as f:
                    await f.write(audio)
            subprocess.call(["ffmpeg", "-i", "temp/" + videoUrl.split("/")[-2] + "-vid." + extension, "-i", "temp/" + videoUrl.split("/")[-2] + "-aud." + extension, "-map", "0", "-map", "1", "-c", "copy", "temp/" + videoUrl.split("/")[-2] + "." + extension], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            async with aiofiles.open("temp/" + videoUrl.split("/")[-2] + "." + extension, "rb") as f:
                media = BytesIO(await f.read())
                media.name = videoUrl.split("/")[-2] + "." + extension
            shutil.rmtree("temp")
            os.mkdir("temp")                
            return(media) 

    async def gallery(mediaJson, url_mode):
        mediaID = []
        for i in mediaJson["gallery"]["items"]:
            mediaID.append(i["mediaId"])
        metadataJson = mediaJson["mediaMetadata"]
        mediaUrlList = []
        mediaList = []
        for mediaSource in mediaID:
            if "u" in metadataJson[mediaSource]["s"].keys():
                mediaUrl = metadataJson[mediaSource]["s"]["u"]
            if "gif" in metadataJson[mediaSource]["s"].keys():
                mediaUrl = metadataJson[mediaSource]["s"]["gif"]
            mediaUrlList.append(mediaUrl)
        #if url_mode:
        #    return(tuple(mediaUrlList))                
        async with aiohttp.ClientSession() as session:
            for mediaUrl in mediaUrlList:
                async with session.get(mediaUrl) as response:
                    media = BytesIO(await response.read())
                media.name = mediaUrl.split("/")[-1].split("?")[0]
                mediaList.append(media)
        return(mediaList)

async def noEmbed(sourceJson, url_mode):
    if "imgur" in sourceJson["url"]:
        mediaUrl = sourceJson["url"].replace("gifv", "mp4")
        if url_mode:
            return(mediaUrl)
        async with aiohttp.ClientSession() as session:
            async with session.get(mediaUrl) as response:
                media = BytesIO(await response.read())
        media.name = mediaUrl.split("/")[-1].split("?")[0]
        return(media)
    else:
        print("NO EMBED?")
        return("https://i.redd.it/hrxpk4vjj4z41.jpg")