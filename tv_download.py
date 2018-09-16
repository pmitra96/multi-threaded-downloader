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
import nltk
from nltk.stem.lancaster import LancasterStemmer
import json
import numpy as np
from pydub import AudioSegment
from pydub.utils import which
import scraper as sc
from datetime import datetime, time
from difflib import SequenceMatcher
import jellyfish


pafy.BACK_END = "internal"

DOWNLOAD_PATH = os.path.dirname(os.path.realpath(__file__))

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

def download_restricted(url,pref_format="mp3"):
    print "youtube download started"
    video = pafy.new(url, gdata=True)
    video_format = video.getbest()
    path = Path(DOWNLOAD_PATH+"/"+"youtube")
    if Path.exists(path):
        category_path = DOWNLOAD_PATH+"/"+"youtube/"+str(video.category)
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
        if Path.exists(Path(category_path)):
            file = video_format.download(filepath = DOWNLOAD_PATH+"/"+"youtube/"+str(video.category))
            if pref_format=="mp3":
                AudioSegment.from_file(file).export(file.split("webm")[0]+".mp3", format="mp3")
            
        else:
            os.makedirs(category_path)
            file = video_format.download(filepath = DOWNLOAD_PATH+"/"+"youtube/"+str(video.category))
            if pref_format=="mp3":
                AudioSegment.from_file(file).export(file.split("webm")[0]+".mp3", format="mp3")
    
    else:
        os.makedirs(category_path)
        file = video_format.download(filepath = DOWNLOAD_PATH+"/"+"youtube/"+str(video.category))
        if pref_format=="mp3":
                AudioSegment.from_file(file).export(file.split("webm")[0]+".mp3", format="mp3")
    os.remove(file)        

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


def download(url,download_path=DOWNLOAD_PATH):
    if "list" in url:
        download_playlist(url)
    else:
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
            

def recursive_download(url,download_path= DOWNLOAD_PATH,in_parts = 0):
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
    
    print "sa"
        
            

    

def get_current_size(filename):
    path = Path(DOWNLOAD_PATH+"/"+filename)
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
        path = Path(DOWNLOAD_PATH+"/"+"youtube")
        if Path.exists(path):
            category_path = DOWNLOAD_PATH+"/"+"youtube/"+"Music"
            print "looks like you are trying to download a music video, so downloading only audio"
            if Path.exists(Path(category_path)):
                file = video_format.download(filepath = DOWNLOAD_PATH+"/"+"youtube/"+"Music")
                if is_audio == 1:
                    AudioSegment.from_file(file).export(file.split("webm")[0]+".mp3", format="mp3")
            else:
                os.makedirs(category_path)
                file = video_format.download(filepath = DOWNLOAD_PATH+"/"+"youtube/"+"Music")
                if is_audio == 1:
                    AudioSegment.from_file(file).export(file.split("webm")[0]+".mp3", format="mp3")
        else:
            os.makedirs(category_path)
            file = video_format.download(filepath = DOWNLOAD_PATH+"/"+"youtube/"+"Music")
            if is_audio == 1:
                AudioSegment.from_file(file).export(file.split(".webm")[0]+".mp3", format="mp3")
        os.remove(file)




def sort_util_generate_key(filename):
    return int(filename.split("part")[-1])


def stitch_parts(filename):
    files = os.listdir(DOWNLOAD_PATH)
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
                os.remove(req_file)


def download_complete_series(tv_series):
    base_url =get_base_url(tv_series,get_best_mirror(tv_series))
    print "download from "+str(base_url)
    recursive_download(base_url)




def get_best_mirror(query):
    speed_dict = {}
    gresults = sc.g_search(query)[0:5]
    for result in gresults:
        print result.url 
        try:
            print get_first_downloadable_link_speed(result.url,query)
            speed_dict[result.url] = get_first_downloadable_link_speed(result.url,query)
        except Exception as e:
            print e
            speed_dict[result.url] = 99999
        print speed_dict
    return min(speed_dict, key=speed_dict.get)



def get_related_links(query,anchor_list):
        return filter(lambda x: similar(x,urllib2.quote(query)) >= 0.5 , anchor_list)



def get_first_downloadable_link_speed(url,query,download_path= os.getcwd(),in_parts = 0,count = 0,fail =0):
    if is_downloadable(url):
        start = datetime.now()
        print "downloading " + url
        resume_download(url,0,512)
        end = datetime.now()
        print "start is " + str(start)
        print "end is " + str(end)
        return get_time_diff(start,end)
    else:
        if count >= 3:
            return 99999
        try:
            req = urllib2.Request(url)
        except Exception as e:
            if fail <=1 :
                ssl._DEFAULT_CIPHERS = ('DES-CBC3-SHA')
                return get_first_downloadable_link_speed(url,query,download_path= os.getcwd(),in_parts = 0,count = 0,fail+1)
            else:
                pass
        req.add_header('User-agent', 'Mozilla 5.10')
        page = urllib2.urlopen(req).read()
        soup = BeautifulSoup(page)
        soup.prettify()
        anchor_list = soup.findAll('a', href=True)[1::]
        anchor = get_related_links(query,anchor_list)[0]
        return get_first_downloadable_link_speed(url + anchor['href'],query,download_path,in_parts,count+1)
            

def get_time_diff(start,end):
    diff = end - start
    return diff.seconds

def similar(a, b):
    return jellyfish.jaro_distance(unicode(a), unicode(b))

def get_base_url(query_string,url):
    url_list = url.split("/")
    res_list = []
    for c,i in enumerate(url_list[::-1]):
        if similar(i,query_string) > 0.5:
            res_list = url_list[0:len(url_list)-c]
    base_url = "/".join(res_list)+"/"
    return base_url            


############################################
# Classifier Functions using Weights.JSON
############################################


def sigmoid(x):
    output = 1/(1+np.exp(-x))
    return output

def cleanup_sentence(sentence):
    # tokenize the pattern
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words

def bag_of_words(sentence,words,show_details=False):
    # tokenize the pattern
    sentence_words = cleanup_sentence(sentence)
    # bag of words
    bag = [0]*len(words)
    for s in sentence_words:
        for i,w in enumerate(words):
            if w==s:
                bag[i]=1
                if show_details:
                    print("Found in bag %s" % w)
    return(np.array(bag))

def think(sentence, show_details=False):
    x = bag_of_words(sentence.lower(), words, show_details)
    if show_details:
        print ("sentence:", sentence, "\n bag_of_words:", x)
    # input layer is our bag of words
    l0 = x
    # matrix multiplication of input and hidden layer
    l1 = sigmoid(np.dot(l0, synapse_0))
    # output layer
    l2 = sigmoid(np.dot(l1, synapse_1))
    return l2

ERROR_THRESHOLD = 0.2
def classify(sentence, show_details=False):
    data_file = DOWNLOAD_PATH+'/weights.json'
    stemmer = LancasterStemmer()
    with open(data_file, 'r') as f:
        raw = json.load(f)

    words = raw['words']
    synapse_0 = np.array(raw['synapse0'])
    synapse_1 = np.array(raw['synapse1'])
    classes = raw['classes']
    print("Classifier between Movies and Music is running....")
    results = think(sentence, show_details)

    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD ] 
    results.sort(key=lambda x: x[1], reverse=True) 
    return_results =[[classes[r[0]],r[1]] for r in results]
    print ("%s \n classification: %s" % (sentence, return_results))
    return return_results

if __name__ == "__main__":
    print os.path.dirname(os.path.realpath(__file__))
    download(sys.argv[1])

    
