from .json_Save import *
import hashlib
from datetime import datetime

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
#Retorna true e o teste nao estiver disponivel   
def verificaTeste(token,teacherUserName):
    #deve verificar se a data do teste esta enquadrada com a data do sistema
    #deve pegar os dados prova daquele teste
    recan= None
    testesCanselados = getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/canselados.json')
    for  x in testesCanselados:
        if(x["id"] == token):
            recan = x
            break
    try:
       dadosProva =  getJSON('./data/Users/Teacher/'+teacherUserName+'/provas/'+str(token)+'/dadosProva.json')
       #verifica se a data enquadra-se com o horario do sistema
       if(not dataInInterval(dadosProva["Data"],dadosProva["fim"],getSystemData())):
           #se o teste nao estiver enquadrado naquela data automaticamente Cancela
           can = {"id":token}
           if(can not in testesCanselados):
                testesCanselados.append(can)
                saveJSON('./data/Users/Teacher/'+teacherUserName+'/provas/canselados.json',testesCanselados)
           return True
       elif(recan!=None):
           testesCanselados.remove(recan)
           saveJSON('./data/Users/Teacher/'+teacherUserName+'/provas/canselados.json',testesCanselados)
           return False    
    except FileNotFoundError as e:
        return True
    
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
    
#formata a data de um modo padrao para o sistema
def formatData(data):
    dt = data
    categories = [(2,'Feb'), (3,'Mar'), (4,'Apr'), (5,'May'), (6,'Jun'), (7,'Jul'), (8,'Aug'), (9,'Sep'), (10,'Oct'),(11,'Nov'),(12,'Dec')]
    #Tenta converter o dia e o ano
    dataSplit = dt.split(' ')
    dia = int(dataSplit[0])
    ano = int(dataSplit[2])
    for catt in categories:
        if(catt[1] in  dataSplit[1]):
            mes = catt[0]
            break
    if(len(str(mes))==1):
        mes="0"+str(mes)
    return str(dia)+"/"+str(mes)+"/"+str(ano)+"|"+str(dataSplit[3])+" "+str(dataSplit[4]).upper()    
#retorna a data do sistema no mesmo formato que o anterior
def getSystemData():            
    s = datetime.now()
    dd = s.strftime("%d/%m/%Y|%I:%M %p")
    return dd

#verifica duas datas datas apenas
def verifydataInInterval(inicio,data):
    i = inicio.split('|')
    d =  data.split('|')
    i1 = i[0].split('/')
    d2 = d[0].split('/') 
    if(int(i1[0])<=int(d2[0]) and int(i1[1])<=int(d2[1]) and int(i1[2])<=int(d2[2])):
        if(int(i1[0])<int(d2[0]) or int(i1[1])<int(d2[1]) or int(i1[2])<int(d2[2])):
            #print("As datas enquadram-se portanto nem 'e preciso verificar as horas")
            return True
        #agora verifica as horas
        ih = i[1]
        dh = d[1]
        #verificando AM e PM
        #ou inicia de manha e a data actual 'e de tarde ou simplemente ou as duas sao de manha ou as duas sao de tarde
        if(ih.split(' ')[1] == 'AM' and dh.split(' ')[1] == 'PM') or (ih.split(' ')[1] == dh.split(' ')[1]) :
            #Verificando horas e minutos
            ihoramin = ih.split(' ')[0].split(':')
            dhoramin = dh.split(' ')[0].split(':')
            #PRIMEIRO VERFICA AS HORAS
            if(int(ihoramin[0])<=int(dhoramin[0])):
               #print("horas enquadram-se")
               #cuidando dos minutos com casos especificos
               #quando as horas forem iguais
               if(int(ihoramin[0])==int(dhoramin[0])):
                   #print("As horas iguais") 
                   if(int(ihoramin[1])<=int(dhoramin[1])):
                        #print("os minutos de inicio ja passaram")
                        return True
                   elif(int(ihoramin[1])>int(dhoramin[1])):
                        #print("os minutos ainda nao estao enquadrados")
                        return False
               elif(int(ihoramin[0])<int(dhoramin[0])):
                   #print("hora de inicio 'e menor portanto é valido")
                   return True                   
            else:
                #print("Horas nao enquadram-se")
                return False
        else:
            #print("as horas nao enquadram-se por causa do AM e PM")
            return False
    else:
        #print("As Dadas nao enquadram-se")
        return False
#Retorna true se a data estiver naquele intervalo
def dataInInterval(inicio,fim,data):
    #PRECISA SER REFEITO
    if(verifydataInInterval(inicio,data) and verifydataInInterval(data,fim) ):
        return True
    else:
        return False
    
        
    