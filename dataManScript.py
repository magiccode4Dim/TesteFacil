from util import json_Save
import pandas as pd
from datetime import datetime
import time
import random
from util import validation

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
def tokenNumberRandom():
    t = json_Save.getJSON('data/tokenList.json')
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
def createNewUser(userName,fullname,turma,classe,password):
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
    users.append(newUser)
    json_Save.saveJSON('data/users.json',users)
  
    
if __name__ == "__main__":
    print("1. Inserir Alunos")
    print("2. Save To Excel")
    print("3. Controlar Tempo")
    print("4. Parar Teste")
    print("5. Inserir dados prova")
    print("6. Verificar utilizador")
    res =  int(input(">> "))
    if(res == 1):
        n = -1
        turma = None
        classe = None
        numeroBool = False
        try:
            turma = input("(default) Turma >> ")
        except KeyboardInterrupt as e:
            pass
        try:
            classe = int(input("(default) Classe >> "))
        except KeyboardInterrupt as e:
            pass
        try:
            n = int(input("(default) N >> "))
        except KeyboardInterrupt as e:
            pass
        if n!=-1:
            numeroBool = True
        inserirAlunos(turma = turma,classe = classe, numeroBool = numeroBool, n = n)
    if(res == 2):
        fileName = input(">File Name : ")
        token = input(">Token : ")
        saveDataFrameExcel(fileName+".xlsx",token)   
    if( res == 3):
        token = input(">Token : ")
        timmer(token)
    if( res == 4):
        token = input(">Token : ")
        stopp(token)
    if(res == 5):
        print("Nao programado ainda ")
    if(res == 6):
        userName = input(">User Name : ")
        number = int(input(">Numero : "))
        validateUserToAluno(userName,number)
            
            
            