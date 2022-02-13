from pprint import pprint
import re
import sys

import numpy as np
sys.path.insert(0, 'data')
sys.path.insert(0, 'chatbot')
import pickle


from dataBase import DataMed
from youtube import Youtube
import chat 
class Service(DataMed,Youtube):

    def __init__(self) :
        #self.driver=med.DataMed()
        self.gouvs=tuple(map(lambda x:x.strip(),open("gouvernorats.txt",'r').readlines()))[::-1]

    def gouvLow(self):
        return tuple(map(lambda x:x.lower(),self.gouvs))
    
    def getAllMedTab(self):
        with super().connection() as con:
            return super().show_all_tasks(con)

    def getMedVille(self,ville):
        with super().connection() as con:
            if 'toute la tunisie' in ville:
                return self.getAllMedTab()
            if len(ville)==1 or type(ville) is str:
                return super().show_data_condition(con,"select distinct * from med where lower(gouvernorat)=?",ville)
            else:
                rqst="select distinct * from med where lower(gouvernorat)="+" or lower(gouvernorat)=".join(list(map(lambda x:"?",ville)))
                return super().show_data_condition(con,rqst,ville)

    def getMedSpec(self,spec):
        specDict={"carc":"Carcinologie médicale","genyco":"Gynécologie obstétrique"}
        with super().connection() as con:
            if type(spec) is str:
                return super().show_data_condition(con,"select distinct * from med where specialite=?",specDict.get(spec))
            elif len(spec)==1 and type(spec) is list:
                return super().show_data_condition(con,"select distinct * from med where specialite=?",specDict.get(spec[0]))
            else:
                spec=list(map(lambda x:specDict.get(x),spec))
                rqst="select distinct * from med where specialite="+" or specialite=".join(list(map(lambda x:"?",spec)))
                return super().show_data_condition(con,rqst,spec)
    
    def getMedVilleSpec(self,ville,spec):
        idVilles=[elem['id'] for elem in self.getMedVille(ville)]
        return [elem for elem in self.getMedSpec(spec) if elem["id"] in idVilles]
    
    def youtubeLinks(self):
        links=list(super().getListVideos())
        return [links[x:x+4] for x in range(0, len(links), 4)]
    
    def chatBot(self,input):
        return chat.chatBotFlask(input)

    def predictBCC(self,x1,x2,x3,x4,x5,x6,x7,x8):
        clf=pickle.load(open("prediction/finalMode.pkl","rb"))
        return clf.predict(np.array([[x1,x2,x3,x4,x5,x6,x7,x8]]))[0]

if __name__=="__main__":
    
    s=Service()

    
