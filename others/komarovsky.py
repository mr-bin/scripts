#!/usr/bin/python
import urllib2
import re
import os

links = ('http://video.komarovskiy.net/category/shkola-doktora-komarovskogo', 
#         'http://video.komarovskiy.net/category/shkola-doktora-komarovskogo/page,2',
#         'http://video.komarovskiy.net/category/shkola-doktora-komarovskogo/page,3',
#         'http://video.komarovskiy.net/category/shkola-doktora-komarovskogo/page,4',
#         'http://video.komarovskiy.net/category/shkola-doktora-komarovskogo/page,5'
         )

print "start"

post_links = []
for link in links:
    page = urllib2.urlopen(link)    
    page_content = page.read()
    url = re.compile("http\://video\.komarovskiy\.net\/[a-zA-Z0-9\-\.]+html")
    post_links.append(url.findall(page_content))
 
print "main pages downloaded" 
        
cleared_post_links = []
for links in post_links:
    for link in links:
        if link in cleared_post_links:
            continue
        else:
            cleared_post_links.append(link)

print "post links cleared"

i = 1
video_links = []
for link in cleared_post_links:    
    page = urllib2.urlopen(link)    
    page_content = page.read()    
    url = re.compile("\/media\/video\/[a-zA-Z0-9\-\._]+mp4")
    video_links.append(url.findall(page_content))
    print "downloaded ",i," video page"
    i = i+1
    
print "downloaded all video pages"
    
cleared_video_links = []
for links in video_links:
    for link in links:
        if link in cleared_video_links:
            continue
        else:
            cleared_video_links.append(link)

print "video links cleared"

full_video_links = []
for link in cleared_video_links:
    full_video_links.append("http://v4.komarovskiy.net"+link)

print "full video links created"
    
for link in full_video_links:
    cmd = "wget -N "+link
    os.system(cmd)
