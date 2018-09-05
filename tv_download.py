import requests
from clint.textui import progress
import urllib2
from bs4 import BeautifulSoup
import threading
import pafy
import time
import sys
from pathlib import Path
import os
import vlc



class DownloadThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
 
    def run(self):
        print "thread" + str(self._args) + "started"
        self._target(*self._args)
 
def is_restricted(url):
    if "youtube" in url:
        return True
    else:
        return False

def download_restricted(url):
    print "youtube download started"
    video = pafy.new(url, gdata=True)
    #print "got video object"
    video_format = video.getbest()
    path = Path(os.getcwd()+"/"+"youtube")
    #print path
    if Path.exists(path):
        category_path = Path(os.getcwd()+"/"+"youtube/"+str(video.category))
        if str(video.category) == "Music":
            print "looks like you are trying to download a music video"
            user_resp = raw_input("would you like to download only audio file ? (y or n) \n")
            if user_resp == "y":
                print "finding the best audio quality..."
                if video.getbestaudio(preftype="mp3") == None:
                    video_format = video.getbestaudio()
                else:
                    video_format = video.getbestaudio(preftype="mp3")


                print video_format
            else:
                pass
        #print category_path
        if Path.exists(category_path):
            video_format.download(filepath = os.getcwd()+"/"+"youtube/"+str(video.category))
        else:
            os.mkdir("youtube/"+video.category)
            #print "category directory created"
            video_format.download(filepath = os.getcwd()+"/"+"youtube/"+str(video.category))
    else:
        os.mkdir("youtube")
        os.mkdir("youtube/"+video.category)
        video_format.download(filepath = os.getcwd()+"/"+"youtube/"+str(video.category))

        

def is_downloadable(url):
    """
    Does the url contain a downloadable resource
    """
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    print content_type
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


def download(url,download_path=os.getcwd()):
    if is_downloadable(url):
        filename = url.split("/")[-1]
        start = get_current_size(filename)
        r = requests.get(url, stream=True)
        file_path = download_path+"/"+filename
        with open(file_path, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
                if chunk:
                    f.write(chunk)
                    
                    f.flush()
    else:
        if is_restricted(url):
            print "looks like a youtube url"
            download_restricted(url)
        else:
            print "the link is not downloadable"

## download season wise takes season url and starting episode as argument
def download_1_deep(pageurl,start=1):
    if is_restricted(pageurl):
        print "dowloading single youtube video"
        currentthread = DownloadThread(download_restricted,pageurl)
        currentthread.start()
        currentthread.join()
    else:
        page = urllib2.urlopen(pageurl).read()
        soup = BeautifulSoup(page)
        soup.prettify()
        threads = []
        for anchor in soup.findAll('a', href=True)[start::]:
            downloadableurl = pageurl + anchor['href']
            currentthread = DownloadThread(download,downloadableurl)
            threads.append(currentthread)
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
            

def recursive_download(url,download_path= os.getcwd(),in_parts = 0):
    if is_downloadable(url):
        print "downloading " + url
        if in_parts == 1:
            fast_multi_thread_download(url)
        else:
            currentthread = DownloadThread(download,url,download_path)
            currentthread.start()
            currentthread.join()
    else:
        if is_restricted(url):
            print "dowloading single youtube video"
            currentthread = DownloadThread(download_restricted,url)
            currentthread.start()
            currentthread.join()
        else:
            page = urllib2.urlopen(url).read()
            soup = BeautifulSoup(page)
            soup.prettify()
            for anchor in soup.findAll('a', href=True)[1::]:
                path = Path(download_path+"/"+str(anchor.text))
                if is_downloadable(url + anchor['href']):
                    recursive_download(url + anchor['href'],download_path,in_parts)
                else:
                    if Path.exists(path):
                        recursive_download(url + anchor['href'],download_path+"/"+str(anchor.text),in_parts)
                    else:
                        os.mkdir(download_path+"/"+str(anchor.text))
                        recursive_download(url + anchor['href'],download_path+"/"+str(anchor.text),in_parts)


def exp(url):
    page = urllib2.urlopen(url).read()
    soup = BeautifulSoup(page)
    soup.prettify()
    for anchor in soup.findAll('a', href=True)[1::]:
        print url+anchor["href"]
    

def get_current_size(filename):
    path = Path(os.getcwd()+"/"+filename)
    if Path.exists(path):
        return path.stat().st_size
    else:
        return 0

def resume_download(url,start=0,end=0,part=0):
    if is_downloadable(url):
        if end != 0 or start != 0:
            filename = url.split("/")[-1]+".part"+str(part)
            print filename
            rangestart = get_current_size(filename)
            resume_header = {'Range': 'bytes=%d-%d' % (rangestart,end)}
            r = requests.get(url,stream = True)
            total_length = end
        else: 
            filename = url.split("/")[-1]
            rangestart = get_current_size(filename)
            resume_header = {'Range': 'bytes=%d-' % rangestart}
            r = requests.get(url,stream = True)
            total_length = int(r.headers.get('content-length'))
        r = requests.get(url,headers=resume_header, stream=True,  verify=False, allow_redirects=True)
        with open(filename, 'ab') as f:
            for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1): 
                if chunk:
                    f.write(chunk)
                else:
                    print "downloadcomplete"
    else:
        if is_restricted(url):
            print "looks like a youtube url"
            download_restricted(url)
        else:
            print "the link is not downloadable"


def fast_multi_thread_download(url):
    r = requests.get(url,stream = True)
    total_length = int(r.headers.get('content-length'))
    part_size = total_length/12
    Parts = {}
    for i in range(0,12):
        start = i*part_size
        end = (i+1)*part_size
        filename = url.split("/")[-1]+".part"+str(i+1)
        currentthread = DownloadThread(resume_download,url,start,end,i+1)
        Parts.setdefault(filename,currentthread)
    
    for part,thread in Parts.iteritems():
        print "starting part "+ str(part)
        thread.start()
    for part,thread in Parts.iteritems():
        print "starting part "+ str(part)
        thread.join()
    complete_file = url.split("/")[-1]
    with open(complete_file,"ab") as f:
        for part,thread in Parts.iteritems():
            with open(part,"r") as pf:
                f.write(pf.read())
    for part,thread in Parts.iteritems():
        print "deleting "+ str(part)
        if os.path.exists(part):
            os.remove(part)
        else:
            print "no file " + part
        

def stream_online(playurl):
    Instance = vlc.Instance()
    player = Instance.media_player_new()
    Media = Instance.media_new(playurl)
    Media.get_mrl()
    player.set_media(Media)
    player.play()
    

def download_playlist(url,is_audio=1):
    playlist = pafy.get_playlist(url)
    
    for video in playlist['items']:
        video = video["pafy"]
        if is_audio == 1:
            video_format = video.getbestaudio()
        else:
            video_format = video.getbest()
        path = Path(os.getcwd()+"/"+"youtube")
        if Path.exists(path):
            category_path = Path(os.getcwd()+"/"+"youtube/"+"Music")
            print "looks like you are trying to download a music video downloading only audio"
            if Path.exists(category_path):
                video_format.download(filepath = os.getcwd()+"/"+"youtube/"+"Music")
            else:
                os.mkdir("youtube/"+"Music")
                #print "category directory created"
                video_format.download(filepath = os.getcwd()+"/"+"youtube/"+"Music")
        else:
            os.mkdir("youtube")
            os.mkdir("youtube/"+"Music")
            video_format.download(filepath = os.getcwd()+"/"+"youtube/"+"Music")




def sort_util_generate_key(filename):
    return int(filename.split("part")[-1])


def stitch_parts(filename):
    files = os.listdir(os.getcwd())
    if filename in files:
        print "file already exists"
    else:
        req_list =  [req_file for req_file in files if filename in req_file]
        req_list.sort(key=sort_util_generate_key)

        print req_list
        with open(filename,"ab") as f:
            for req_file in req_list:
                with open(req_file,"r") as pf:
                    f.write(pf.read())

    
if __name__ == "__main__":
    
    exp(sys.argv[1])

    
