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
def getAllDadosProva(teacherUserName):
    t = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/tokenList.json')
    confList = list()
    for x in t:
        try:
            confList.append(json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/'+str(x)+'/dadosProva.json'))
        except Exception as e:
            pass
    return confList
#retorna a prova em si
def getTeacherProva(teacherUserName, token):
    try:
         return json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/'+str(token)+'/prova.json')
    except FileNotFoundError as e:
        return list()
   

#Obtem a nota do aluno pelo numero
def getNotaAluno(numero,token,teacherUserName):
    notas = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/'+token+"/notas.json")
    for n in notas:
        if(n["numero"]==numero):
            return n["Nota"]
    return None

#guarda o token
def saveToken(token,teacherUserName):
    t = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/tokenList.json')
    t.append(token)
    json_Save.saveJSON('./data/Users/Teacher/'+teacherUserName+'/provas/tokenList.json',t)


#Gera numeros de estudantes aleatorios
def tokenNumberRandom(file, lista =  None, acres = None):
    if lista == None:
        t = json_Save.getJSON(file)
    else:
        t =  lista
    if len(t)==0:
        if(acres!=None):
            return acres+str(random.randint(1,1000000))
        return random.randint(1,1000000) 
    while True:
        newNumber = random.randint(1,1000000)
        
        #Caso o token tenha algo afrente primeiro
        if(acres!=None):
            if(acres+str(newNumber) in t):
                continue
            else:
                return acres+str(newNumber)
        
        if(newNumber in t):
            continue
        else:
            return newNumber   

#Pega todas os ficheiros de configuracao das provas disponiveis para um usuario
def getAvaliableTesteForUser(userName):
    availableforUser = json_Save.getJSON('./data/Users/SimpleUser/'+userName+"/availableTestes.json")
    available = list()
    for t in availableforUser:
        if(validation.alunoIsAutorized(t["teacherUserName"],userName,t["token"])):
            try:
                av = json_Save.getJSON('./data/Users/Teacher/'+t["teacherUserName"]+'/provas/'+t["token"]+'/dadosProva.json')
            except FileNotFoundError as e:
                continue
            av["teacher"] = t["teacherUserName"]
            aluno = getAlunoByUserName(userName,av["teacher"])
            nota = getNotaAluno(aluno["numeroEst"],t["token"],av["teacher"])
            #pega tambem a nota do teste se ela existir
            if (testeDisponivel(t["token"],av["teacher"])):
                av["nota"] = -2    
            elif(nota!=None):
                av["nota"] = nota
            else:
                av["nota"] = -1
            available.append(av)
    return available
            

#Gera numeros de estudantes aleatorios
def estudantNumberRandom(teacherUserName):
    alunos = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/alunos.json')
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
def validateUserToAluno(userName, number,teacherUserName, turma):
    users = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/users.json')
    #Muda de nao aprovado para aprovado
    user = getTeacherUserByUserName(userName,teacherUserName, turma=turma)
    if(user==None):
        return
    users.remove(user)
    user["isAproved"] = 1
    users.append(user)
    json_Save.saveJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/users.json',users)
    try:
        alunos = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/alunos.json')
    except FileNotFoundError as e:
        alunos = list()
    newAluno = {
                'numeroEst':number,
                'nome':user["fullname"],
                'turma':user["turma"],
                "userName": user["userName"]
            }
    #Adiciona o estudante a turma
    if addAlunoToTurma(user["userName"],teacherUserName,user["turma"]) != "ok":
        return "Nao foi possivel salvar porque a turma nao existe"
    alunos.append(newAluno)
    #remove a request do aluno
    #removeRequest(user["userName"],user["turma"],teacherUserName)
    json_Save.saveJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/alunos.json',alunos)
    return "ok"  
    
#Obter o usuario pelo nome 
def getUserByUserName(userName):
    users =  json_Save.getJSON('data/users.json')
    for u in users:
        if(u['userName']==userName):
            return u
    return None
#obtem o usuario que adastrou-se para um professor
def getTeacherUserByUserName(name,teacherUserName , turma = None):
    try:
        alunos =  json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/users.json')
    except FileNotFoundError as e:
        return None
    for u in alunos:
        if(turma!=None):
            if(u["userName"]==name and turma== u["turma"]):
                return u
            continue
        if(u["userName"]==name):
            return u
    return None

#obterm todos os users do professor que nao foram verificados e que foram verificados
def getTeacherUsersUnaprovad(teacherUserName,turma):
    users = list()
    try:
        alunos =  json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/users.json')
    except FileNotFoundError as e:
        return None
    for a in alunos:
        try:
            if(a["turma"]==turma):
                key = a["isAproved"]
        except KeyError as e:
            users.append(a)
            continue
    return users

#obter aluno pelo user name
def getAlunoByUserName(name,teacherUserName, turma = None):
    try:
        alunos =  json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/alunos.json')
    except FileNotFoundError as e:
        return None
    for u in alunos:
        if(turma!=None):
            if(u["userName"]==name and turma== u["turma"]):
                return u
            continue
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
def testeDisponivel(token,teacherUserName):
    testesCanselados = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/canselados.json')
    for x in testesCanselados:
        if(x['id']==token):
            return False
    return True


#Para um determinadoi teste
def stopp(token,teacherUserName):
    #Verificar se o professor nao esta tentar cancelar um teste que nao 'e seu
    if token not in json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/tokenList.json'):
        return
    testesCanselados = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/canselados.json')
    can  = {'id':token}
    if can not in testesCanselados:
        testesCanselados.append(can)
        json_Save.saveJSON('./data/Users/Teacher/'+teacherUserName+'/provas/canselados.json',testesCanselados)
#Retormar a realizacao do teste cancelado
def iniciarTeste(token,teacherUserName):
    #Verificar se o professor nao esta tentar iniciar um teste que nao 'e seu
    if token not in json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/tokenList.json'):
        return
    testesCanselados = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/canselados.json')
    for can in testesCanselados:
        if(can['id']==token):
            testesCanselados.remove(can)
            break
    json_Save.saveJSON('./data/Users/Teacher/'+teacherUserName+'/provas/canselados.json',testesCanselados)    
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
            stopp(token,"")
            return True

#Salva as notas em um ficheiro excel
def saveDataFrameExcel(fileName,token,teacherUserName):
    try:
        notas = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/'+token+"/notas.json")
    except FileNotFoundError as e:
        return None
    dataExcel = pd.DataFrame(notas)
    dataExcel.to_excel('./data/Users/Teacher/'+teacherUserName+'/download/'+fileName)
    return True

#Salva a nota no ficheiro de Notas
def salvarNota(num,nomeEst,nota, token,teacherUserName):
    try:
        notas = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/'+token+"/notas.json")
    except FileNotFoundError as e:
        notas = list()
    newTupla = {
        'numero':num,
        'nome':nomeEst,
        'Nota':nota
    }
    notas.append(newTupla)
    json_Save.saveJSON('./data/Users/Teacher/'+teacherUserName+'/provas/'+token+"/notas.json",notas)
#Verifica se a Nota ja existe
def notaExists(num,nomeEst,token,teacherUserName):
    notas = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/'+token+"/notas.json")
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
def createNewUser(userName,fullname,password,email, isAdmin = 0):
    try:
        users = json_Save.getJSON('data/users.json')
    except FileNotFoundError as e:
        users = list()
    result = hashlib.md5(password.encode())
    newUser = {
                'userName':userName,
                'fullname':fullname,
                'password':str(result.hexdigest()),
                'email':email
            }
    if(isAdmin==1):
        newUser["isAdmin"]=1
        newUser["permissions"]="CRUD"
    else:
        #Caso seja um usuario simples, ele vai criar uma pasta com nome do usuario
        os.makedirs("./data/Users/SimpleUser/"+userName)
        #cria tambem um arquivo com as provas disponiveis para aquele user
        json_Save.saveJSON('./data/Users/SimpleUser/'+userName+"/availableTestes.json",list())
        #ficheiro onde seram armazenados os pedidos de ingresso
        json_Save.saveJSON('./data/Users/SimpleUser/'+userName+"/requests.json",list())
        #Cria a TimeLine
        json_Save.saveJSON('./data/Users/SimpleUser/'+userName+"/timeLine.json",list())
    users.append(newUser)
    json_Save.saveJSON('data/users.json',users)

#=========================== METODOS DA VERSAO 2
#gera novos tokens teacher
def generateTokenTeacher(numbers =  1, typeT = "Normal", validade = "unlimited"):
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
             "type": typeT,
             "validade":validade
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
#get teacher By Name
def getTeacherByUserName(userName):
    try:
        teachers = json_Save.getJSON('./data/Users/Teacher/teachers.json')
    except FileNotFoundError as e:
        return None
    for t in teachers:
        if(t["userName"]==userName):
            return t
    return None

#Usar o Token para um determinado professor
def useTokenForTeacher(userName,token):
    tokensTeacher = json_Save.getJSON('./data/Users/Teacher/tokensTeacher.json')
    for t in tokensTeacher:
        if(t["userName"]=="--" and t["token"]== token):
            tokensTeacher.remove(t)
            t["userName"] = userName
            tokensTeacher.append(t)
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
def createTeacher(userName, email, senha, nome, token, descri):
    if tokenTeacherIsValid(token) == False:
        return "Invalid Token"
    if validation.userNameExists(userName):
        return "UserName Alread Exist"
    
    teacher = {
            "userName":userName,
            "email":email,
            "fullname": nome,
            "bio":descri 
        }
    createNewUser(userName,nome,senha,email,isAdmin=1)
    saveTeacher(teacher)
    os.makedirs("./data/Users/Teacher/"+userName+"/alunos")
    json_Save.saveJSON('./data/Users/Teacher/'+userName+'/alunos/users.json',list())
    json_Save.saveJSON('./data/Users/Teacher/'+userName+'/alunos/alunos.json',list())
    os.makedirs("./data/Users/Teacher/"+userName+"/download")
    os.makedirs("./data/Users/Teacher/"+userName+"/provas")
    json_Save.saveJSON('./data/Users/Teacher/'+userName+'/provas/tokenList.json',list())
    json_Save.saveJSON('./data/Users/Teacher/'+userName+'/provas/canselados.json',list())
    os.makedirs("./data/Users/Teacher/"+userName+"/turmas")
    #cria a timeLine do teacher
    #timeLine.json
    json_Save.saveJSON('./data/Users/Teacher/'+userName+'/timeLine.json',list())
    #Usar o token
    useTokenForTeacher(userName,token)
    return "Sucess"
#Criar Turma
def criarTurma(userNameProfessor,nome,descricao):
    newTurma = {
        "nome":nome,
        "descricao": descricao,
        "alunos":[]
    }
    json_Save.saveJSON("./data/Users/Teacher/"+userNameProfessor+"/turmas/"+nome.replace(" ","_")+".json",newTurma)
#retorna a turma
def getTurma(userNameProfessor,nome):
    try:
        return json_Save.getJSON("./data/Users/Teacher/"+userNameProfessor+"/turmas/"+nome.replace(" ","_")+".json")
    except FileNotFoundError as e:
        return None
    except Exception as e:
        return None
#adicionar alunos a turmas
def addAlunoToTurma(userNameAluno, userNameProfessor,nome):
    try:
        turma = json_Save.getJSON("./data/Users/Teacher/"+userNameProfessor+"/turmas/"+nome.replace(" ","_")+".json")
        turmaArray = turma["alunos"]
    except FileNotFoundError as e:
        return "Turma Not found"
    if userNameAluno not in turmaArray:
        turmaArray.append(userNameAluno)
        turma["alunos"] =  turmaArray
        json_Save.saveJSON("./data/Users/Teacher/"+userNameProfessor+"/turmas/"+nome.replace(" ","_")+".json",turma)
    return "ok"
#Retorna o Token do professor
def getTokenTeacher(userName):
    tokensTeacher = json_Save.getJSON('./data/Users/Teacher/tokensTeacher.json')
    for t in tokensTeacher:
        if(t["userName"]==userName):
            return t["token"]
 
 #Deixa o teste diponivel para o utilizador
def makeTestAvailableForUser(teacherUserName,tokenTest, userName,turma):
    availableforUser = json_Save.getJSON('./data/Users/SimpleUser/'+userName+"/availableTestes.json")
    ob =  {
            "token":tokenTest,
            "teacherUserName":teacherUserName,
            "turma":turma  
        }
    if(ob in availableforUser):
        return
    availableforUser.append(ob)
    json_Save.saveJSON('./data/Users/SimpleUser/'+userName+"/availableTestes.json",availableforUser)
 
 #pedir adesao a uma turma
def incressarEmTurma(userName,teacherUserName, nomeTurma):
    user =  getUserByUserName(userName)
    user["turma"] = nomeTurma
    users =  json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/users.json')
    if(user in users):
        return
    users.append(user)
    json_Save.saveJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/users.json',users)
    requestsIn = json_Save.getJSON('./data/Users/SimpleUser/'+userName+"/requests.json")
    requestsIn.append(
        {
          "teacherUserName":teacherUserName,
          "nomeTurma":nomeTurma 
        }
    )
    json_Save.saveJSON('./data/Users/SimpleUser/'+userName+"/requests.json",requestsIn)
#remove request, remove o pedido de adesao a turma
def removeRequest(userName,turma,teacherUserName):
    requestsIn = json_Save.getJSON('./data/Users/SimpleUser/'+userName+"/requests.json")
    for p in requestsIn:
        if(p["teacherUserName"]==teacherUserName and turma==p["nomeTurma"]):
            requestsIn.remove(p)
            break
    json_Save.saveJSON('./data/Users/SimpleUser/'+userName+"/requests.json",requestsIn)
#verifica se uma turma ja foi requistada pelo usuario
def turmaIsRequested(userName,turma, professor):
    resq = json_Save.getJSON('./data/Users/SimpleUser/'+userName+"/requests.json")
    for r in resq:
        if(r["nomeTurma"]==turma and r["teacherUserName"]==professor):
            return True
    return False    
#retorna todas as turmas em que o utilizador esta
def getAlTurmas(userName, dadosProva):
    turn =  list()
    for d in dadosProva:
        #pega o utilizador como estudante daquela turma
        es =  getAlunoByUserName(userName,d["teacher"])
        t = {
            "turma":es["turma"],
            "teacher":d["teacher"]
            }
        if t not in turn:
            turn.append(t)
    return turn
#actualizar usuario
def updateUser(user, listt):
    users = json_Save.getJSON(listt)
    for u in users:
        if u['userName'] == user['userName']:
            users.remove(u)
            users.append(user)
            json_Save.saveJSON(listt,users)
            return
#pega todas as turmas de um determinado professor
def getAllTurmasOfTeacher(teacher):
    turmas  =  list()
    pasta = "./data/Users/Teacher/"+teacher+"/turmas"
    for dirr , subfol, arqus in os.walk(pasta):
        for ar in arqus:
            t = json_Save.getJSON(dirr+"/"+ar)
            t['teacher'] = teacher
            turmas.append(t)
    return turmas
#pesquisa professor com alguma coisa haver com a chave
def searchData(key):
    res = list()
    turmas = list()
    try:
        teachers = json_Save.getJSON('./data/Users/Teacher/teachers.json')
    except FileNotFoundError as e:
        return None
    for t in teachers:
        if(key in t["userName"] or key in t["email"] or key in t["fullname"] or key in t["bio"] ):
            res.append(t)
        allT = getAllTurmasOfTeacher(t["userName"])
        for tur in allT:
            if (key in tur["nome"] or key in tur["descricao"]):
                turmas.append(tur)
        #
    return (res,turmas)          
#get user prova
def getProva(user,teacher,token):
    try:
        prova = json_Save.getJSON('./data/Users/Teacher/'+teacher+'/provas/'+token+'/resultadosAlunos/'+user+".json")
    except FileNotFoundError as e:
        return None
    return prova

#junta a prova e os resultados
def unionProvaAndResult(prova,result):
    newList = list()
    pp = 0
    for p in prova:
        p["res"]=(result[pp])[1]
        pp+=1
        newList.append(p)
    return newList

#retorna as notas e dadas dos testes
def getNotaAndData(userName):
    testes =  getAvaliableTesteForUser(userName)
    notas = []
    datas =  []
    categories = [(2,'Feb'), (3,'Mar'), (4,'Apr'), (5,'May'), (6,'Jun'), (7,'Jul'), (8,'Aug'), (9,'Sep'), (10,'Oct'),(11,'Nov'),(12,'Dec')]
    for t in testes:
        if(t["nota"]>=0):
            notas.append(t["nota"])
            dad = t["Data"].split("/")   
            for c in categories:
                if(c[0]==int(dad[1])):
                    datas.append(c[1])
        else:
            continue
    return {
        "datas" : datas,
        "notas"  : notas
    }
    
#retorna a quantidade de perguntas acertadas, erradas e nao respondidas do estudante AENR - Acertada Errada e Nao respondida
def getPerguntasQuntAENR(userName, teacher = None, token = None):
    testes =  getAvaliableTesteForUser(userName)
    erradas  = 0
    correctas = 0
    naoRespondidas = 0
    for t in testes:
        if teacher != None:
            #se passarmos o teacher como parametro
            if(t["teacher"]!=teacher):
                continue
        if token != None:
            if(t["token"]!=token):
                continue
        tt = getProva(userName,t["teacher"],t["token"])
        if(tt==None):
            continue
        results  = tt["results"]
        prova = getTeacherProva(t["teacher"],t["token"])
        #para saber a quantidade de perguntas nao respondidas 'e so somar a diferença entre as perguntas da prova do aluno com as da prova original
        naoRespondidas+=len(prova)-len(results)
        #sabendo quantidade de perguntas certas e erradas
        for i in range(len(prova)):
            try:
                if ((prova[i])["id"]==(results[i])[0]):
                    if((results[i])[1]==(prova[i])["correcta"]):
                        correctas+=1
                    elif ((results[i])[1]!=(prova[i])["correcta"]):
                        erradas+=1
            except Exception as e:
                #essa excessao vai acontecer nas vezes em que haverao perguntas nao respondidas
                continue
    return {
        'Erradas': erradas,
		'NRespondidas': naoRespondidas,
		'Certas': correctas
    }
#pega apenas os estudantes de uma determinada Turma
def getOnlyStudentsOfClass(alunos,turma):
    l = list()
    for x in alunos:
        if(x["turma"]==turma):
            l.append(x)
    return l

#apaga um determinado aluno
def deletAluno(userName,tur,teacherUserName):
    try:
        #remove o user da lista de users
        users =  json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/users.json')
        user = getTeacherUserByUserName(userName,teacherUserName,turma=tur)
        users.remove(user)
        
        #remove o aluno da lista de alunos
        alunos  = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/alunos.json')
        aluno = getAlunoByUserName(userName,teacherUserName,turma=tur)
        alunos.remove(aluno)
        
        #remove o aluno da turma
        turma  = json_Save.getJSON('./data/Users/Teacher/'+teacherUserName+'/turmas/'+(tur.replace(" ","_"))+".json")
        turma['alunos'].remove(userName)
        
        #Removo os testes daquela turma da disponibilidade do aluno
        availableforUser = json_Save.getJSON('./data/Users/SimpleUser/'+userName+"/availableTestes.json")
        #print(len(availableforUser))
        availableforUser2 = list()
        for av in availableforUser:
            if(av["turma"] !=  tur):
                availableforUser2.append(av)
        #apaga a requeste o estudante fez para aquela turma
        removeRequest(userName,tur,teacherUserName)
        print("bugg")
    except Exception as e:
        print(e)
        return False
    
    #Começa a salvar os ficheiros
    json_Save.saveJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/users.json',users)
    json_Save.saveJSON('./data/Users/Teacher/'+teacherUserName+'/alunos/alunos.json',alunos)
    json_Save.saveJSON('./data/Users/Teacher/'+teacherUserName+'/turmas/'+(tur.replace(" ","_"))+".json",turma)
    json_Save.saveJSON('./data/Users/SimpleUser/'+userName+"/availableTestes.json",availableforUser2)
    return True

#Pega a quantidade de perguntas Certas, Erradas e Nao respondidas de cada estudante em cada teste
def getAllQuantErradasCertasNRes(teacher):
    dadosProvas = getAllDadosProva(teacher)
    alunos  = json_Save.getJSON('./data/Users/Teacher/'+teacher+'/alunos/alunos.json')
    provaNome = []
    erradas = []
    naoRespond = []
    certasA  = []
    allData = list()
    for a in alunos:
        for d in dadosProvas:
            #certas, erradas e nao respondidas de um determinado teste
            res  = getPerguntasQuntAENR(a['userName'],teacher=teacher,token=d["token"])
            if (res['Erradas']==0  and res['NRespondidas']==0 and res['Certas'] == 0):
                #qundo isso acontece quer dizer que o estudante nao fez o teste
                continue
            res['Titulo'] = d["Titulo"]
            res['userName'] = a['userName']   
            allData.append(res)
    #guarda so os titulos das provas
    titulos = list()
    for a in allData:
         titulos.append(a['Titulo'])
    #para cada titulo
    for t in titulos:
        pos = -1
        if t in provaNome:
            pos =  provaNome.index(t)
        else:
            provaNome.append(t)
        certast= 0
        erradast = 0
        naoRespondt = 0
        for a in allData:
            if(a['Titulo']==t):
                certast+= a['Certas']
                erradast+= a['Erradas']
                naoRespondt+= a['NRespondidas']
                allData.remove(a)
        if(pos!=-1):
            erradas[pos] = erradas[pos]+erradast
            certasA[pos] = certasA[pos]+certast
            naoRespond[pos] = naoRespond[pos]+naoRespondt
            #pos = -1
        else:      
            erradas.append(erradast)
            certasA.append(certast)
            naoRespond.append(naoRespondt)
        #reduz a lista para nao demorar muito tempo nas proximas vezes
    return {
        "testes":provaNome,
        "erradas":erradas,
        "certas":certasA,
        "nrespond":naoRespond
    }
    
            
                
                 


if __name__ == "__main__":
    #print(createTeacher("pascoal","p@gmail.com","2001","NanyNilson","996198a8c84f17c43ee758e170a7de3d12d292"))
    #updateToken("Nany","3930697a67c119686f8b5066f2b64f54f4040f")
    #criarTurma("narciso","B","Povo no Partido")
    #addAlunoToTurma("paxA","Nany","B1 12")
    generateTokenTeacher(numbers=10)
    #incressarEmTurma("@nanilsin","romeu","A")
    #print(validateUserToAluno("@nanilsin",3444,"romeu"))
    #print(getAllDadosProva("romeu"))
    #print(getAvaliableTesteForUser("pax"))
    #a, b  = searchData("A")
    
    #print(a)
    #user = getTeacherUserByUserName('bubufilho','romeu', turma='P122')
    #print(user)
    
    #print(getAllQuantErradasCertasNRes('narciso'))