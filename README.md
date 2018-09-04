# multi-threaded-downloader
A downloader to download whole tv series from index of * movie name * servers
to Install
(i would recommend you to use virtualenv)
clone the repo and cd into directory
1)pip install -r requirements.txt
2)open python shell
3)from tv_download import *

Features
1)download_restricted(url) #downloads videos from urls like youtube etc
2)download(url) #downloads any url even the youtube ones
3)download_1_loop(url) #starts from current url and downloads everything upto 1 level of current url(to download 1 season)
4)recursive_download(url) #starts with current url and downloads everything downloadable with current url as parent(used for downloading whole tv shows from index of websites)
5)resume_download(url,start=0,end=0) #resumes any url download 
6)fast_multi_thread_download(url) #downloads any file by downloading the file in parts and stiching them back together
7)stram_online(url) #can stream any media url directly without downloading
8)download_playlist(youtube_playlist_url) #downloads youtube playlist
9)stich_parts(filename) #stich parts of files together , where parts are named filename.part1,filename.part2


To Do:
1) make the code object oriented
2)better interface for online streaming 
3)performance comparision to traditional download managers like IDM
4)determine if the speed of download depends on number of threads it is broken down into
5)if 4 is True,write an algorithm to find optimal number of parts the download must be broken down into in order to maximise the speed
6)genre clasification using neural nets

