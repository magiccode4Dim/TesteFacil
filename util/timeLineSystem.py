from .json_Save import *
from datetime import datetime

#criar um evento
def createEvent(nivel,titulo, descricao):
    da = datetime.now().strftime('%D - %H:%M:%S')
    return {
        "nivel":nivel,
        "titulo":titulo,
        "descricao":descricao,
        'data': da
    }

#adiciona evento a timeLine de um determindo User
def addEventToUserTimeLine(event,userName):
    try:
        events  = getJSON('./data/Users/SimpleUser/'+userName+"/timeLine.json")
    except FileNotFoundError as e:
        events = list()
    events.append(event)
    saveJSON('./data/Users/SimpleUser/'+userName+"/timeLine.json",events)
#adiciona o evento na timeLine de um determinado professor
def addEventToTeacherTimeLine(event,userName):
    try:
        events  = getJSON('./data/Users/Teacher/'+userName+'/timeLine.json')
    except FileNotFoundError as e:
        events = list()
    events.append(event)
    saveJSON('./data/Users/Teacher/'+userName+'/timeLine.json',events)
#getTime Line User
#retorna os 10 eventos mais recentes da conta
def getTimeLineUser(userName):
    try:
        timeline =  getJSON('./data/Users/SimpleUser/'+userName+"/timeLine.json")
        l =  list()
        timeline.reverse()
        for x in timeline:
            l.append(x)
            if(len(l)==15):
                break
        return l  
    except FileNotFoundError as e:
            return list()
#getTeacher TimeLine
def getTimeLineTeacher(userName):
    try:
        timeline =  getJSON('./data/Users/Teacher/'+userName+'/timeLine.json')
        l =  list()
        timeline.reverse()
        for x in timeline:
            l.append(x)
            if(len(l)==15):
                break
        return l  
    except FileNotFoundError as e:
            return list()
#retorna os 10 eventos mais recentes da conta        
#Registra erros durante execucao do sistema
def addError(e, userName):
    da = datetime.now().strftime('%D - %H:%M:%S')
    error =  {
        "userName":userName,
        "descricao":e,
        'data': da
    }
    try:
        events  = getJSON('./data/Users/SystemData/erros.json')
    except FileNotFoundError as e:
        events = list()
    events.append(error)
    saveJSON('./data/Users/SystemData/erros.json',events)

#Retorna os erros que surgiram durante a execução do sistema
def getAllErros():
    try:
        return getJSON('./data/Users/SystemData/erros.json')
    except FileNotFoundError as e:
        return list()