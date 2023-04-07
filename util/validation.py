from .json_Save import *

#Verifica se o usuario 'e administrador
def isAdmin(user):
    try:
                #Vai tentar aceder a essa chave... se ele for administ nao pode aceder
        chave = user["isAdmin"]
    except Exception as e:  
        return False
    return True

#Verifica se um determinado username existe
def userNameExists(userName):
    users =  getJSON('data/users.json')
    for u in users:
        if u['userName'] == userName:
            return True
    return False
#Verifica os dados do Login
def verifyLoginData(user, pAss):
    users =  getJSON('data/users.json')
    for u in users:
        if u['userName'] == user and u['password'] == pAss:
            return True
    return False
#Verifica se o user  esta autorizado a realizar a prova
def alunoIsAutorized(aluno, token):
    req = getJSON('provas/'+str(token)+'/dadosProva.json')["user_requis"]
    if aluno["turma"] in req["turma"] and aluno["classe"] == req["classe"]:
        return True
    return False
#Verifica se o teste ainda esta disponivel ou nao    
def verificaTeste(token):
    testesCanselados = getJSON('data/canselados.json')
    for x in testesCanselados:
        if(x['id']==token):
            return True
    return False  
