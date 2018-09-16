# multi-threaded-downloader
**A downloader to download whole tv series**

to Install
(i would recommend you to use virtualenv)

**_clone the repo and cd into directory_**

1)`pip install -r requirements.txt`

2)open python shell

3)`from tv_download import *`

For command line usage 
if you have a virtualenv for this project
* `alias d="workon $YOURVIRTUALENV;python $PATH_TO_tv_download.py"`
else 
* `alias d=python $PATH_TO_tv_download.py`

### Features
>downloads videos from urls like youtube etc
* `download_restricted(url)` 
>downloads any url even the youtube ones
* `download(url)` 
>starts from current url and downloads everything upto 1 level of current url(to download 1 season)
* `download_1_loop(url)` 
>starts with current url and downloads everything downloadable with current url as parent(used for downloading whole tv shows from index of websites)
* `recursive_download(url)`
>resumes any url download 
* `resume_download(url,start=0,end=0)` 
>downloads any file by downloading the file in parts and stiching them back together
* `fast_multi_thread_download(url)` 
>can stream any media url directly without downloading
* `stream_online(url)` 
>downloads youtube playlist
* `download_playlist(youtube_playlist_url)` 
>stich parts of files together , where parts are named filename.part1,filename.part2
* `stich_parts(filename)`
>classify a video as Music or Movie based on its name
* `classify(videoname)`
>download whole tv show just by entering its name
* `download_complete_series(videoname)`

### To Do:
* make the code object oriented
* better interface for online streaming 
* performance comparision to traditional download managers like IDM
* determine if the speed of download depends on number of threads it is broken down into
* if above point is True,write an algorithm to find optimal number of parts the download must be broken down into in order to maximise the speed
* genre clasification using neural nets
