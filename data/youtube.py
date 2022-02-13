from urllib import request as rqst
import re


class Youtube:

    def getListVideos(self):
        resp=rqst.urlopen("https://www.youtube.com/results?search_query=cancer+du+sein&sp=CAASAhgB")
        #from bite type to str type
        htmlSTR=resp.read().decode()
        #fiding the id of videos
        videos_ids=re.findall(r"watch\?v=(\S{11})",htmlSTR)
        return set(map(lambda id:" https://www.youtube.com/embed/"+id,videos_ids[0:16]))

