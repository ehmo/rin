# Tweet Media Extraction Summary

Source index: `resources/tweet_media_enriched_classified.tsv`
Downloaded files: `resources/media/images/`, `resources/media/videos/`

- Tweets processed: 29
- Content media tweets: 13
- Profile-avatar-only tweets: 16
- Downloaded videos: 6

## Content Media Tweets
- 004 | image: https://pbs.twimg.com/ext_tw_video_thumb/1546149141440475137/pu/img/CY4hug2s9o9wccDw.jpg | video: https://video.twimg.com/ext_tw_video/1546149141440475137/pu/vid/1280x720/8LvvsOPVMu16lzqa.mp4?tag=12 | image_file: resources/media/images/004.jpg | video_file: resources/media/videos/004.mp4
- 005 | image: https://pbs.twimg.com/media/DYoshziU0AAVnV3.jpg?name=orig | video: - | image_file: resources/media/images/005.jpg
- 007 | image: https://pbs.twimg.com/media/FxAWYgOXwAMzaqH.jpg?name=orig | video: - | image_file: resources/media/images/007.jpg
- 010 | image: https://pbs.twimg.com/ext_tw_video_thumb/1681762214234198016/pu/img/Bs_Y0f6CIL1Iw91v.jpg | video: https://video.twimg.com/ext_tw_video/1681762214234198016/pu/vid/720x1280/d4n6FVQsrKhzhTO-.mp4?tag=12 | image_file: resources/media/images/010.jpg | video_file: resources/media/videos/010.mp4
- 012 | image: https://pbs.twimg.com/ext_tw_video_thumb/1683856162779811842/pu/img/nTcXSy3wKcYt3lXk.jpg | video: https://video.twimg.com/ext_tw_video/1683856162779811842/pu/vid/720x866/fLWp2HaRAX22rqhE.mp4?tag=12 | image_file: resources/media/images/012.jpg | video_file: resources/media/videos/012.mp4
- 013 | image: https://pbs.twimg.com/ext_tw_video_thumb/1534593644325392385/pu/img/cjMQ69aX5IwKWDf2.jpg | video: https://video.twimg.com/ext_tw_video/1534593644325392385/pu/vid/1280x720/iMoKW00tmiAXO206.mp4?tag=12 | image_file: resources/media/images/013.jpg | video_file: resources/media/videos/013.mp4
- 015 | image: https://pbs.twimg.com/media/F4m9xbCXMAAFhup.jpg?name=orig | video: - | image_file: resources/media/images/015.jpg
- 018 | image: https://pbs.twimg.com/ext_tw_video_thumb/1712145448524480512/pu/img/LZnabL0smM1d9IrE.jpg | video: https://video.twimg.com/ext_tw_video/1712145448524480512/pu/vid/avc1/1080x1920/2wYJUzgVsgu9I7dh.mp4?tag=14 | image_file: resources/media/images/018.jpg | video_file: resources/media/videos/018.mp4
- 025 | image: https://pbs.twimg.com/media/Gbo1walbMAAa5cJ.jpg?name=orig | video: - | image_file: resources/media/images/025.jpg
- 028 | image: https://pbs.twimg.com/media/Gm-bCYQbQAA--jV.jpg?name=orig | video: - | image_file: resources/media/images/028.jpg
- 029 | image: https://pbs.twimg.com/media/Gqf9IP0XcAALy9j.jpg?name=orig | video: - | image_file: resources/media/images/029.jpg
- 033 | image: https://pbs.twimg.com/media/G_mvuM5W0AAd1E-.jpg?name=orig | video: - | image_file: resources/media/images/033.jpg
- 034 | image: https://pbs.twimg.com/amplify_video_thumb/2016924085306200064/img/b_v6P20J9bPYcCih.jpg | video: https://video.twimg.com/amplify_video/2016924085306200064/vid/avc1/1080x1080/Y8Um7xyPEOxWl-kC.mp4?tag=21 | image_file: resources/media/images/034.jpg | video_file: resources/media/videos/034.mp4

## Notes
- Some tweet links expose only profile/avatar media in metadata; these are preserved but lower value.
- 6 MP4 videos were recoverable directly from og:video links.
- The original ChatGPT share link (027) is still unavailable in-source, but PDF replacement was ingested as 036.
