import json
from pprint import pprint
import random
from nltk.util import pr

import torch

from model import NeuralNet
from nltk_utils import bag_of_word, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('chatbot/intents.json', 'r') as json_data:
    intents = json.load(json_data)

FILE = "data.pth"
data = torch.load(FILE)

input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

bot_name = "BCC"


def chatBot(sentence):
    sentence = tokenize(sentence)
    X = bag_of_word(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        for intent in intents['intents']:
            if tag == intent["tag"]:
                if tag!="myapp":
                    print(f"{bot_name}: {random.choice(intent['responses'])}")
                else:
                    print(f"{bot_name}: {'ok bb'}")
    else:
        print(f"{bot_name}: Je vous comprend pas...")


        

def chatBotFlask(sentence):
    sentence = tokenize(sentence)
    X = bag_of_word(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)
    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]
    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    print(prob.item())
    if prob.item() > 0.97:
        for intent in intents['intents']:
            if tag == intent["tag"]:
               return random.choice(intent['responses'])
                
    else:
        lgouvs,lspec,searchMed=[],[],0
        with open("chatbot/gouv_spec_intents.json") as fg:
            gouvJs=json.load(fg)
            for elem in sentence:
                for gouvPatt in gouvJs["gouvs"] :
                    if elem.lower() in gouvPatt.get("patterns"):
                        lgouvs.append(gouvPatt.get("responses"))
                for medPatt in gouvJs["spec"] :
                    if elem.lower() in medPatt.get("patterns"):
                        searchMed=1
                        if medPatt.get("tag") != "doc":
                            lspec.append(medPatt.get('responses'))
        
        gouvPath='/ville={}'.format("&".join(lgouvs)) if lgouvs else ""
        specPath= '/spec={}'.format("&".join(lspec)) if lspec else ""
        
        button= lambda x,y,z: """
            <div  style="word-wrap: break-word;font-size:14px;">
            <a   href="{}">
              Voir la liste des 
                {} {}.
            </a>   
            </div>   
            """.format(x,y,z)  
        

        if (not gouvPath and  specPath) or( gouvPath and  not specPath) or ( gouvPath and  specPath) :
            dMed={"carc":'cancérologues',"genyco":"génycologues"}
            href="/docteurs"+gouvPath+specPath
            docsName=" et ".join([dMed.get(elem,elem) for elem in lspec]) if lspec else "spécialistes"
            gouvName="à "+" et ".join(lgouvs) if lgouvs else " en Tunisie"
            return button(href,docsName,gouvName)
        elif not gouvPath and not specPath and searchMed:
            return button("/docteurs","spécialistes","en Tunisie")                   

        else:
            return "Je ne vous comprends pas"

            

if __name__=="__main__":
    print(chatBotFlask("docteur"))
    pass
    """print("Let's chat! (type 'quit' to exit)")
    while True:
        # sentence = "do you use credit cards?"
        sentence = input("You: ")
        if sentence == "quit":
            break
        chatBotFlask(sentence)"""
