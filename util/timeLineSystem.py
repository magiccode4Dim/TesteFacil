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
def getTimeLineUser(userName):
    try:
        return getJSON('./data/Users/SimpleUser/'+userName+"/timeLine.json")
    except FileNotFoundError as e:
            return list()
#getTeacher TimeLine
def getTimeLineTeacher(userName):
    try:
        return getJSON('./data/Users/Teacher/'+userName+'/timeLine.json')
    except FileNotFoundError as e:
            return list()