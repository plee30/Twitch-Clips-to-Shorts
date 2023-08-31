from twitchAPI.twitch import Twitch
from twitchAPI.helper import first, limit
from moviepy.editor import VideoFileClip, clips_array, vfx
import asyncio
import os
import datetime
import aiohttp

client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")

# Insert name of streamer
# TODO: Change from hard-coded string to argument
broadcaster = 'heokong98'

# For date, example format is start/end_date = datetime.datetime(2023, 8, 16)
# started_at (Optional[datetime]) – Starting date/time for returned clips
# ended_at (Optional[datetime]) – Ending date/time for returned clips
# TODO: Change from hard-coded datetime to argument
start_date = datetime.datetime(2023, 8, 17)
end_date = datetime.datetime.today()

async def get_clips():
    # initialize the twitch instance, this will by default also create a app authentication
    twitch = await Twitch(client_id, client_secret)
    # call the API for the data of twitch user
    id = await first(twitch.get_users(logins=broadcaster))
    # get list of clips
    clip_list = twitch.get_clips(broadcaster_id = id.id, started_at = start_date, ended_at = end_date)
    await twitch.close()
    return clip_list

async def test_func():
    clip_list = await get_clips()
    async for clips in limit(clip_list, 5):
        print(clips.id)
        
async def download_clip(clip_url, output_filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(clip_url) as response:
            with open(output_filename, "wb") as f:
                while True:
                    chunk = await response.content.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)

async def edit_clip(input_filename, output_filename):
    edited_cam_clip = (VideoFileClip(input_filename)
                        # TODO hard coded coordinates to arguments
                        .fx( vfx.resize, width=1920)
                        # Joeyyy .fx( vfx.crop, x1=1226, x2=1576, y1=802, y2=1079)
                        .fx( vfx.crop, x1=1277, x2=1614, y1=826, y2=1079)
                        .fx( vfx.resize, width=1080))
    edited_gameplay_clip = (VideoFileClip(input_filename)
                        .fx( vfx.resize, height=1280))
    arranged_clips = clips_array([[edited_cam_clip], [edited_gameplay_clip]])
    cropped_video = arranged_clips.crop(width=1080, height=1920, x2=(arranged_clips.w/2+540), y2=arranged_clips.h)
    cropped_video.write_videofile(output_filename, codec="libx264", threads=8, fps=24)

async def main():
    # TODO Change to allow multiple downloads & edits at once
    clip_list = await get_clips()
    async for clips in limit(clip_list, 1):
        clip_url = clips.thumbnail_url.replace("-preview-480x272.jpg", ".mp4")
        downloaded_filename = clips.id + ".mp4"
        edited_filename = "edited_" + clips.id + ".mp4"
        await download_clip(clip_url, downloaded_filename)
        await edit_clip(downloaded_filename, edited_filename)

if __name__ == "__main__":
    asyncio.run(main())
