#SISTEMA DE NOTIFICAÇÕES
from .json_Save import *
from .validation import isAdmin
 
 #adiciona uma notificacao  a um aluno
def addUserNotificaTion(title, descri, user, link):
    notfic =  getJSON('./data/Users/SimpleUser/'+user+"/notifications.json")
    notfic.append({
        "title":title,
        "descri":descri,
        "link":link
    })
    saveJSON('./data/Users/SimpleUser/'+user+"/notifications.json",notfic)
    

#adiciona um a notificacao a um professor
def addTeacherNotification(title , descri, teacher, link):
    notfic =  getJSON('./data/Users/Teacher/'+teacher+'/notifications.json')
    notfic.append({
        "title":title,
        "descri":descri,
        "link":link
    })
    saveJSON('./data/Users/Teacher/'+teacher+'/notifications.json',notfic)
#retorna as notificacoes do utilizador
def getUserNotification(user):
    try:
        #retorna somente as ultimas 10 notificacoes
        notif = getJSON('./data/Users/SimpleUser/'+user+"/notifications.json")
        lastTen = list()
        for n in range(10):
                try:
                    nll = notif[n]
                except Exception as e:
                    break
                nll["id"] = n
                lastTen.append(nll)
        return lastTen
    except FileNotFoundError as e:
        return list()

#retorna as notificacoes do professor
def getProfNotification(teacher):
    try:
        notif = getJSON('./data/Users/Teacher/'+teacher+'/notifications.json')
        lastTen = list()
        for n in range(10):
            try:
                nll = notif[n]
            except Exception as e:
                break
            nll["id"] = n
            lastTen.append(nll)
        return lastTen

    except FileNotFoundError as e:
        return list()

#remove a notificacao com determina ID
def removeNotification(id, user):
    if(isAdmin(user)):
        path = './data/Users/Teacher/'+user['userName']+'/notifications.json'
        notif = getJSON(path)
        notif.remove(notif[id])
    else:
        path = './data/Users/SimpleUser/'+user['userName']+"/notifications.json"
        notif = getJSON(path)
        notif.remove(notif[id])
    saveJSON(path,notif)
        