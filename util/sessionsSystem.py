from .json_Save import *
from datetime import datetime

#Adiciona uma nova sessao
def addSession(user, cookie):
    sessiosn =  getJSON('data/sessions.json')
    da = datetime.now().strftime('%D - %H:%M:%S')
    newSession = {
        'userName':user,
        'cookie': cookie,
        'data': da
    }
    sessiosn.append(newSession)
    saveJSON('data/sessions.json',sessiosn)
#Remove uma sessao
def removeSession(user):
    sessiosn =  getJSON('data/sessions.json')
    for s in sessiosn:
        if(s['userName']==user):
            sessiosn.remove(s)
    saveJSON('data/sessions.json',sessiosn)
#Verifica se uma sessao existe
def verfiySession(cookie):
    sessiosn =  getJSON('data/sessions.json')
    for s in sessiosn:
        if(s['cookie']==cookie):
            return s["userName"]
    return None

#retorna os usernames dos usuarios com sessoes activas
def getActiveSessionsUsers():
    sessiosn =  getJSON('data/sessions.json')
    active = list()
    for s in sessiosn:
            active.append(s["userName"])
    return active

    