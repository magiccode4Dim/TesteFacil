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
#Verifica se o user  esta autorizado a realizar/ver a prova
def alunoIsAutorized(teacherUserName, aluno, token):
    #pega os dados da prova
    try:
        req = getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/'+str(token)+'/dadosProva.json')["user_requis"]
    except FileNotFoundError:
        return False
    #pega o conjunto de turmas em que aquela prova foi alocada
    turmaProva = req["turma"].split(",")
    for t in turmaProva:
        #pega a turma e verifica se aquele nome de usuario consta
        alunosTur = getJSON('./data/Users/Teacher/'+teacherUserName+'/turmas/'+t.replace(" ","_")+".json")["alunos"]
        if( aluno in alunosTur):
            return True
    return False
#Verifica se o teste ainda esta disponivel ou nao    
def verificaTeste(token,teacherUserName):
    testesCanselados = getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/canselados.json')
    for x in testesCanselados:
        if(x['id']==token):
            return True
    return False
#---METODOS DA VERSAO 2
#validacao do userName
def userNameIsAcept(userName):
    if(' ' in userName or "/" in userName or '\\' in userName or "'" in userName or "`" in userName or '"' in userName ):
        return False
    else:
        return True
#Valida o Imput do utilizador
def inputIsValid(inputtData):
    if(len(inputtData)<100):
        return True
    else:
        return False