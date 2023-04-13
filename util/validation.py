from .json_Save import *
import hashlib

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
    result = hashlib.md5(pAss.encode())
    pAss = str(result.hexdigest())
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
#---METODOS DA VERSAO 2

def userNameIsAcept(userName):
    if(' ' in userName or "/" in userName or '\\' in userName):
        return False
    else:
        return True
