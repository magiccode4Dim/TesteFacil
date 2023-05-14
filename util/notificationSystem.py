#SISTEMA DE NOTIFICAÇÕES
from .json_Save import *
 
 #adiciona uma notificacao  a um aluno
def addUserNotificaTion(title, descri, user, link):
    notfic =  getJSON('./data/Users/SimpleUser/'+user+"/notifications.json")
    if(len(notfic)==15):
        #se chegar no nomero maximo de notificacoes, deve reiniciar a lista
        notfic = list()
    notfic.append({
        "title":title,
        "descri":descri,
        "link":link
    })
    saveJSON('./data/Users/SimpleUser/'+user+"/notifications.json",notfic)
    

#adiciona um a notificacao a um professor
def addTeacherNotification(title , descri, teacher, link):
    notfic =  getJSON('./data/Users/Teacher/'+teacher+'/notifications.json')
    if(len(notfic)==15):
        #se chegar no nomero maximo de notificacoes, deve reiniciar a lista
        notfic = list()
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
        notif.reverse()
        lastTen = list()
        if(len(notif)>10):
            for n in range(10):
                lastTen.append(notif[n])
            return lastTen
        else:
            return notif
    except FileNotFoundError as e:
        return list()

#retorna as notificacoes do professor
def getProfNotification(teacher):
    try:
        notif = getJSON('./data/Users/Teacher/'+teacher+'/notifications.json')
        notif.reverse()
        lastTen = list()
        if(len(notif)>10):
            for n in range(10):
                lastTen.append(notif[n])
            return lastTen
        else:
            return notif
    except FileNotFoundError as e:
        return list()
