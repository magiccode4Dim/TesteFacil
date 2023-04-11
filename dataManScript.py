from util import json_Save
import pandas as pd
from datetime import datetime
import time
import random
from util import validation
import os
import secrets
import hashlib

#=========================== METODOS DA VERSAO 1
#Obtem os ficheiros de configuracao de todas as provas
def getAllDadosProva():
    t = json_Save.getJSON('data/tokenList.json')
    confList = list()
    for x in t:
        try:
            confList.append(json_Save.getJSON('provas/'+str(x)+'/dadosProva.json'))
        except Exception as e:
            pass
    return confList

#Obtem a nota do aluno pelo numero
def getNotaAluno(numero,token):
    notas = json_Save.getJSON('provas/'+token+"/notas.json")
    for n in notas:
        if(n["numero"]==numero):
            return n["Nota"]
    return None

#guarda o token
def saveToken(token):
    t = json_Save.getJSON('data/tokenList.json')
    t.append(token)
    json_Save.saveJSON('data/tokenList.json',t)


#Gera numeros de estudantes aleatorios
def tokenNumberRandom(file, lista =  None):
    if lista == None:
        t = json_Save.getJSON(file)
    else:
        t =  lista
    if len(t)==0:
        return random.randint(1,1000000) 
    while True:
        newNumber = random.randint(1,1000000)
        if(newNumber in t):
            continue
        else:
            return newNumber   

#Pega todas os ficheiros de configuracao das provas disponiveis para um usuario
def getAvaliableTesteForUser(userName):
    tokenList = json_Save.getJSON('data/tokenList.json')
    available = list()
    u = getUserByUserName(userName)
    for t in tokenList:
        if(validation.alunoIsAutorized(u,t)):
            available.append(json_Save.getJSON('provas/'+str(t)+'/dadosProva.json'))
    return available
            

#Gera numeros de estudantes aleatorios
def estudantNumberRandom():
    alunos = json_Save.getJSON('data/alunos.json')
    if len(alunos)==0:
        return random.randint(1,1000000) 
    allstudentNumbers = list()
    for a in alunos:
        allstudentNumbers.append(a["numeroEst"])     
    while True:
        newNumber = random.randint(1,1000000)
        if(newNumber in allstudentNumbers):
            continue
        else:
            return newNumber   

#Validar estudante
def validateUserToAluno(userName, number):
    users = json_Save.getJSON('data/users.json')
    #Muda de nao aprovado para aprovado
    for u in users:
        if(u["userName"]==userName):
            us = u
            users.remove(u)
            us["isAproved"] = 1
            users.append(us)
            break
    json_Save.saveJSON('data/users.json',users)
    try:
        alunos = json_Save.getJSON('data/alunos.json')
    except FileNotFoundError as e:
        alunos = list()
    user = getUserByUserName(userName)
    newAluno = {
                'numeroEst':number,
                'nome':user["fullname"],
                'turma':user["turma"],
                'classe':user["classe"],
                "userName": user["userName"]
            }
    alunos.append(newAluno)
    json_Save.saveJSON('data/alunos.json',alunos)  
    
#Obter o usuario pelo nome 
def getUserByUserName(userName):
    users =  json_Save.getJSON('data/users.json')
    for u in users:
        if(u['userName']==userName):
            return u
    return None

#obter aluno pelo user name
def getAlunoByUserName(name):
    alunos =  json_Save.getJSON('data/alunos.json')
    for u in alunos:
        if(u["userName"]==name):
            return u
    return None


#Inserir dados Prova
def insertDadosProva(Data,Escola,Professor,Titulo,fim,requisitos, token):
    dadosProva = {
        'Data':Data,
        'Escola':Escola,
        'Professor':Professor,
        'Titulo':Titulo,
        'fim':fim,
        'user_requis':requisitos
    }
    json_Save.saveJSON('provas/'+token+"/dadosProva.json")

#Verifica se o teste ainda esta disponivel
def testeDisponivel(token):
    testesCanselados = json_Save.getJSON('data/canselados.json')
    for x in testesCanselados:
        if(x['id']==token):
            return False
    return True


#Para um determinadoi teste
def stopp(token):
    testesCanselados = json_Save.getJSON('data/canselados.json')
    can  = {'id':token}
    if can not in testesCanselados:
        testesCanselados.append(can)
        json_Save.saveJSON('data/canselados.json',testesCanselados)
#Retormar a realizacao do teste cancelado
def iniciarTeste(token):
    testesCanselados = json_Save.getJSON('data/canselados.json')
    for can in testesCanselados:
        if(can['id']==token):
            testesCanselados.remove(can)
            break
    json_Save.saveJSON('data/canselados.json',testesCanselados)    
#Ele controla se um teste terminou ou nao
def timmer(token):
    try:
        dados = json_Save.getJSON('provas/'+token+"/dadosProva.json")
        tempo =  dados["fim"]        
    except FileNotFoundError as e:
        return None
    while True:
        time.sleep(2)
        s = datetime.now()
        print("Tempo Actual: "+s.strftime('%H:%M:%S'))
        if(s.strftime('%H:%M:%S') in tempo):
            stopp(token)
            return True

#Salva as notas em um ficheiro excel
def saveDataFrameExcel(fileName,token):
    try:
        notas = json_Save.getJSON('provas/'+token+"/notas.json")
    except FileNotFoundError as e:
        return None
    dataExcel = pd.DataFrame(notas)
    dataExcel.to_excel('download/'+fileName)
    return True

#Salva a nota no ficheiro de Notas
def salvarNota(num,nomeEst,nota, token):
    try:
        notas = json_Save.getJSON('provas/'+token+"/notas.json")
    except FileNotFoundError as e:
        notas = list()
    newTupla = {
        'numero':num,
        'nome':nomeEst,
        'Nota':nota
    }
    notas.append(newTupla)
    json_Save.saveJSON('provas/'+token+"/notas.json",notas)
#Verifica se a Nota ja existe
def notaExists(num,nomeEst,token):
    notas = json_Save.getJSON('provas/'+token+"/notas.json")
    for a in notas:
        if(a['numero']==num and a['nome']==nomeEst):
            return True
    return  False
#Retorna o estudante com um deternminado ID
def getAlunoById(id):
    alunos = json_Save.getJSON('data/alunos.json')
    for a in alunos:
        if(a['numeroEst']==id):
            return a
    return None
#insere alunos
def inserirAlunos(turma = None,classe = None, numeroBool = False, n = 1, randonCodes = False):
    try:
        alunos = json_Save.getJSON('data/alunos.json')
    except FileNotFoundError as e:
        alunos = list()
    while True:
        try:
            if(numeroBool==False):
                n = int(input("#Numero "))
            if(turma==None):
                turma = input("#Turma :")
            if(classe==None):
                classe = int(input("#Classe :"))
            nome = input("#Nome :")
            newAluno = {
                'numeroEst':n,
                'nome':nome,
                'turma':turma,
                'classe':classe
            }
            alunos.append(newAluno)
            n+=1
        except KeyboardInterrupt as e:
            break
    json_Save.saveJSON('data/alunos.json',alunos)  
#create new user
def createNewUser(userName,fullname,turma,classe,password, isAdmin = 0):
    try:
        users = json_Save.getJSON('data/users.json')
    except FileNotFoundError as e:
        users = list()
    newUser = {
                'userName':userName,
                'fullname':fullname,
                'turma':turma,
                'classe':classe,
                'password':password,
                'isAproved':0
            }
    if(isAdmin==1):
        newUser["isAdmin"]=1
        newUser["permissions"]="CRUD"
    users.append(newUser)
    json_Save.saveJSON('data/users.json',users)

#=========================== METODOS DA VERSAO 2
#gera novos tokens teacher
def generateTokenTeacher(numbers =  1, typeT = "Normal"):
    try:
        tokensTeacher = json_Save.getJSON('./data/Users/Teacher/tokensTeacher.json')
    except FileNotFoundError as e:
        tokensTeacher = list()
    i =  0
    listToken = list()
    for t  in tokensTeacher:
        listToken.append(t["token"])        
    while i<numbers:
        newToken = str(tokenNumberRandom('None', lista = listToken))+str(secrets.token_hex(16))
        dictToken = {
             "userName":"--",
             "token":newToken,
             "type": typeT
         }
        tokensTeacher.append(dictToken)
        i+=1
    json_Save.saveJSON('./data/Users/Teacher/tokensTeacher.json',tokensTeacher)

#verifica se o token que o professor esta usar para abrir a conta 'e valido ou nao
def tokenTeacherIsValid(token):
    try:
        tokensTeacher = json_Save.getJSON('./data/Users/Teacher/tokensTeacher.json')
    except FileNotFoundError as e:
        return False
    for t in tokensTeacher:
        if(t["userName"]=="--" and t["token"]== token):
            return True
    return False

#Salvar professor
def saveTeacher(teacher):
    try:
        teachers = json_Save.getJSON('./data/Users/Teacher/teachers.json')
    except FileNotFoundError as e:
        teachers = list()
    teachers.append(teacher)
    json_Save.saveJSON('./data/Users/Teacher/teachers.json',teachers)

#Usar o Token para um determinado professor
def useTokenForTeacher(userName,token):
    tokensTeacher = json_Save.getJSON('./data/Users/Teacher/tokensTeacher.json')
    for t in tokensTeacher:
        if(t["userName"]=="--" and t["token"]== token):
            tokensTeacher.remove(t)
            dictToken = {
             "userName":userName,
             "token":token
             }
            tokensTeacher.append(dictToken)
            json_Save.saveJSON('./data/Users/Teacher/tokensTeacher.json',tokensTeacher)
            break
#Actualiza o Token do professor (Para casos de upgrade de conta)     
def updateToken(userName,newToken):
    tokensTeacher = json_Save.getJSON('./data/Users/Teacher/tokensTeacher.json')
    for t in tokensTeacher:
        if(t["userName"]==userName):
            tokensTeacher.remove(t)
            t["token"] = newToken
            tokensTeacher.append(t)
            json_Save.saveJSON('./data/Users/Teacher/tokensTeacher.json',tokensTeacher)
            break
#Cria uma nova conta Teacher
def createTeacher(userName, email, senha, nome, token):
    if tokenTeacherIsValid(token) == False:
        return "Invalid Token"
    if validation.userNameExists(userName):
        return "UserName Alread Exist"
    result = hashlib.md5(senha.encode())
    teacher = {
            "userName":userName,
            "email":email,
            "fullName": nome 
        }
    createNewUser(userName,nome,"--","--",str(result.hexdigest()),isAdmin=1)
    saveTeacher(teacher)
    os.makedirs("./data/Users/Teacher/"+userName+"/alunos")
    os.makedirs("./data/Users/Teacher/"+userName+"/download")
    os.makedirs("./data/Users/Teacher/"+userName+"/provas")
    os.makedirs("./data/Users/Teacher/"+userName+"/turmas")
    #Usar o token
    useTokenForTeacher(userName,token)
    return "Sucess"

    
if __name__ == "__main__":
    #print(createTeacher("Nany","na@gmail.com","nany","Narciso Cadeado","159693424ed5f4ea5905b098e8703253d1bdbf"))
    updateToken("Nany","3930697a67c119686f8b5066f2b64f54f4040f")