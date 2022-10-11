import re
import aiohttp
import aiofiles
import requests
import subprocess
from io import BytesIO
from bs4 import BeautifulSoup as bs

async def gallery(metadataJson):
    mediaList = []
    async with aiohttp.ClientSession() as session:
        for mediaSource in metadataJson:
            if "u" in metadataJson[mediaSource]["s"].keys():
                mediaUrl = metadataJson[mediaSource]["s"]["u"]
            if "gif" in metadataJson[mediaSource]["s"].keys():
                mediaUrl = metadataJson[mediaSource]["s"]["gif"]
            async with session.get(mediaUrl) as response:
                media = BytesIO(await response.read())
            media.name = mediaUrl.split("/")[-1].split("?")[0]
            mediaList.append(media)
        print("Gallery hosted on Reddit.")
    return(mediaList)

async def gfycat(mediaUrl):
    async with aiohttp.ClientSession() as session:
        async with session.get(mediaUrl) as response:
            gyfcatEmbed = requests.utils.unquote(re.search(r'\?src=(.*)&display_name=Gfycat', str(await response.read())).group(1))
        async with session.get(gyfcatEmbed) as response:
            gyfcatEmbed = requests.utils.unquote(re.search(r'"video":{"@type":"VideoObject","author":"anonymous","contentUrl":"(.*)","creator":"anonymous",', str(await response.read())).group(1))
        async with session.get(gyfcatEmbed) as response:
            media = BytesIO(await response.read())
    media.name = gyfcatEmbed.split("/")[-1].split("?")[0]
    print(gyfcatEmbed[0:36])
    return(media)

async def imgur(mediaUrl):
    async with aiohttp.ClientSession() as session:
        async with session.get(mediaUrl) as response:
            media = BytesIO(await response.read())
    media.name = mediaUrl.split("/")[-1].split("?")[0]
    print(mediaUrl[0:36])
    return(media)

async def reddit(mediaUrl):
    async with aiohttp.ClientSession() as session:
        async with session.get(mediaUrl) as response:
            media = BytesIO(await response.read())
    media.name = mediaUrl.split("/")[-1].split("?")[0]
    print(mediaUrl[0:36])
    return(media)

async def redditvideo(mediaUrl):
    async with aiohttp.ClientSession() as session:
        async with session.get(mediaUrl) as response:
            parsedResponse = bs(await response.read(), "lxml")
    try:
        audioList = [(i.baseurl.text) for i in parsedResponse.find("adaptationset", contenttype="audio").find_all("representation")]
        audioUrl = mediaUrl.split("DASHPlaylist.mpd")[0] + audioList[-1]
    except AttributeError:
        videoList = [(i.baseurl.text) for i in parsedResponse.find("adaptationset").find_all("representation")]
        videoUrl = mediaUrl.split("DASHPlaylist.mpd")[0] + videoList[-1]
        extension = videoUrl.split(".")[-1].split("?")[0]
        async with aiohttp.ClientSession() as session:
            async with session.get(videoUrl) as response:
                media = BytesIO(await response.read())
                media.name = videoUrl.split("/")[-2] + "." + extension
        print(videoUrl[0:36]) 
        return(media)
    else:
        videoList = [(i.baseurl.text) for i in parsedResponse.find("adaptationset", contenttype="video").find_all("representation")]
        videoUrl = mediaUrl.split("DASHPlaylist.mpd")[0] + videoList[-1]
        extension = videoUrl.split(".")[-1].split("?")[0]
        async with aiohttp.ClientSession() as session:
            async with session.get(videoUrl) as videoResponse:
                video = await videoResponse.read()
            async with session.get(audioUrl) as audioResponse:
                audio = await audioResponse.read()                    
            async with aiofiles.open("temp/" + videoUrl.split("/")[-2] + "-vid." + extension, "wb") as f:
                await f.write(video)
            async with aiofiles.open("temp/" + videoUrl.split("/")[-2] + "-aud." + extension, "wb") as f:
                await f.write(audio)    
        print(videoUrl[0:36])
        subprocess.call(["ffmpeg", "-i", "temp/" + videoUrl.split("/")[-2] + "-vid." + extension, "-i", "temp/" + videoUrl.split("/")[-2] + "-aud." + extension, "-map", "0", "-map", "1", "-c", "copy", videoUrl.split("/")[-2] + "." + extension], stdout=subprocess.DEVNULL)
        async with aiofiles.open(videoUrl.split("/")[-2] + "." + extension, "rb") as f:
            media = BytesIO(await f.read())
            media.name = videoUrl.split("/")[-2] + "." + extension
        return(media)        

async def redgifs(mediaUrl):
    async with aiohttp.ClientSession() as session:
        async with session.get(mediaUrl) as response:
            redgifsEmbed = requests.utils.unquote(re.search(r'<iframe src="(.*)" frameborder="0"', str(await response.read())).group(1))
        async with session.get(redgifsEmbed) as response:
            redgifsEmbed = requests.utils.unquote(re.search(r'<meta property="og:video" content="(.*?)"><meta property="og:video:type" content="video/mp4">', str(await response.read())).group(1).replace("&amp;", "&"))
        async with session.get(redgifsEmbed) as response:
            media = BytesIO(await response.read())
            media.name = redgifsEmbed.split("/")[-1].split("?")[0]
            print(redgifsEmbed[0:36])
            return(media)

async def noEmbed(mediaUrl):
    print("not embed? get fucked")        