#APLICACAO PRINCIPAL
from flask import Flask,request,render_template, url_for, redirect, make_response,send_file,jsonify
from util import json_Save, bussness,validation,sessionsSystem,timeLineSystem,dataAnalise
from dataManScript import *
import os
import random
import time
import secrets
from datetime import datetime

app = Flask(__name__, template_folder="templates")

@app.route("/",methods=['GET']) 
def defaultUrl():
     return redirect(url_for('index'))
#DashBoard 
#GENERAL
@app.route("/dashboard",methods=['GET']) 
def index():
    #Deve verificar se a pessoa esta logada e tudo mais
    #Pega os ficheiros de configuracao de todas as provas
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            try:
                #verifica se a pessoa 'e admin
                if(validation.isAdmin(getUserByUserName(s))==False):
                    #Pega os dados do usuario e lhe lanca para a DashBoard
                    availableTestes = getAvaliableTesteForUser(s)
                    #retorna somente as provas que podem ser visiveis pelo user
                    availableTestes = apenasProvasDisponiveis(availableTestes)
                    turmas  = getAlTurmas(s,availableTestes)
                    if(len(availableTestes)==0):
                        return render_template('dashboardUser.html',user=s, turmas = turmas, notifications = notificationSystem.getUserNotification(s))
                    else:
                        #vai pegar todas as notas do aluno com base em dados do teste
                        return render_template('dashboardUser.html',da=availableTestes,user=s , turmas = turmas, notifications = notificationSystem.getUserNotification(s))
                provasConf = getAllDadosProva(s)
                t= getAllTurmasOfTeacher(s)
                return render_template("dashboardAdmin.html", provas = provasConf, turmas = t, user =  s, notifications = notificationSystem.getProfNotification(s))
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")
    return redirect(url_for('login'))
#LOGIN
#GENERAL
@app.route("/login",methods=['GET']) 
def login():
    #Se o utilizador entrar na pagina de login enquanto tem os cookies de sessao activos, esses cookies devem ser apagados
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            if(validation.isAdmin(getUserByUserName(s))==False):
                timeLineSystem.addEventToUserTimeLine(timeLineSystem.createEvent("Conf","Log Out","O User Saiu do Sistema"),s)
            else:
                timeLineSystem.addEventToTeacherTimeLine(timeLineSystem.createEvent("Conf","Log Out","O User Saiu do Sistema"),s)
            sessionsSystem.removeSession(s)
    return render_template('login.html')
#AUTENTICATION
#GENERAL
@app.route("/autentication",methods=['GET','POST']) 
def autenticar():
    if(request.method=='GET'):
        return redirect(url_for('login'))
    try:
        #caso a pessoa colocar um username invalido na autenticacao
        a = request.form.get("username")
        if not validation.userNameIsAcept(a) or not validation.inputIsValid(a):
                    return render_template("Error.html",erro = "O UserName 'e Invalido")
        if(request.form.get("username") != None and request.form.get("pass") != None):
            if(validation.verifyLoginData(request.form.get("username"),request.form.get("pass"))):
                #Apaga qualquer cookie anterior do utilizador se existir
                sessionsSystem.removeSession(request.form.get("username"))
                #cria uma nova sessao
                cookie = str(request.form.get("username").__hash__())+str(random.random())+str(secrets.token_hex(16))
                sessionsSystem.addSession(request.form.get("username"),cookie)
                #print("Guardando Cookie")
                if(validation.isAdmin(getUserByUserName(request.form.get("username")))==False):
                    #Adiciona o Evento de Login
                    timeLineSystem.addEventToUserTimeLine(timeLineSystem.createEvent("Conf","Login","Novo Inicio de Sessão"),
                                                        request.form.get("username"))
                    #se a pessoa nao for administradora
                    #cria uma nova resposta
                    availableTestes = getAvaliableTesteForUser(request.form.get("username"))
                    #retorna somente as provas que podem ser visiveis pelo user
                    availableTestes = apenasProvasDisponiveis(availableTestes)
                    turmas  = getAlTurmas(request.form.get("username"),availableTestes)
                    if(len(availableTestes)==0):
                        resposta = make_response(render_template('dashboardUser.html',user=request.form.get("username"), turmas = turmas, notifications = notificationSystem.getUserNotification(request.form.get("username"))))
                    else:
                        resposta = make_response(render_template('dashboardUser.html',da=availableTestes,user=request.form.get("username"), turmas = turmas, notifications = notificationSystem.getUserNotification(request.form.get("username"))))
                else:
                    timeLineSystem.addEventToTeacherTimeLine(timeLineSystem.createEvent("Conf","Login","Novo Inicio de Sessão"),
                                                        request.form.get("username"))
                    #se a pessoa for administradora
                    t= getAllTurmasOfTeacher(request.form.get("username"))
                    provasConf = getAllDadosProva(request.form.get("username"))
                    resposta = make_response(render_template("dashboardAdmin.html",provas = provasConf,turmas = t, user =  request.form.get("username"),notifications = notificationSystem.getProfNotification(request.form.get("username"))))
                resposta.set_cookie("SessionID",cookie)
                return resposta
    except Exception as e:
                timeLineSystem.addError(str(e),"desconhecido")
                return render_template("Error.html",erro = "Erro do Sistema")
    return redirect(url_for('login')) 
#cadastrar novos usuarios
#GENERAL
@app.route("/createaccount",methods=['GET']) 
def createAccont():
    #Se o utilizador entrar na pagina de criar conta enquanto tem os cookies de sessao activos, esses cookies devem ser apagados
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            if(validation.isAdmin(getUserByUserName(s))==False):
                timeLineSystem.addEventToUserTimeLine(timeLineSystem.createEvent("Conf","Log Out","O User Saiu do Sistema"),s)
                #SE A PESSOA NAO 'E ADMINISTRADORA, O COOKIE DE SESSAO 'E REMOVIDO
                sessionsSystem.removeSession(s)
    return render_template('register.html',accountType="student")
#Escolher que tipo de conta se pretende criar
#GENERAL
@app.route("/choosecounttype",methods=['GET','POST']) 
def countType():
    if(request.method=='GET'):
        return render_template("chooseTypeCount.html")
    elif (request.method=='POST'):
        option = request.form.get('options')
        #print(option)
        if(option==None):
             return render_template("chooseTypeCount.html")
        else:
            if option == "teacher":
                return render_template('register.html',accountType="teacher")
            elif option == "student":
                return render_template('register.html',accountType="student")
    return redirect(url_for('login'))

#ENVIAR OS DADOS VIA POST PARA O CADASTRO
#GENERAL
@app.route("/cadastrar",methods=['GET','POST']) 
def cadastrar():
    if(request.method=='GET'):
        return redirect(url_for('createAccont'))
    try:
        if(len(request.form.get("fullname"))>1 and len(request.form.get("pass"))>1 and len(request.form.get("pass"))==len(request.form.get("pass2")) ):
            if(validation.userNameExists(request.form.get("username"))):
                return render_template("Error.html",erro = "O UserName Introduzido Já Existe, Tente Outro")
            else:
                a = request.form.get("username")
                if not validation.userNameIsAcept(a) or  not validation.inputIsValid(a):
                    return render_template("Error.html",erro = "O UserName 'e Invalido")
                #a=a[:len(a)-1]
                #caso for um admin sendo criado
                if(request.form.get('token') != None):
                    res = createTeacher(a,request.form.get("email"),request.form.get("pass2"),request.form.get("fullname"),request.form.get('token'), request.form.get("descr") )
                    if(res=="Sucess"):
                        return render_template("Sucess.html",title= "Perfil Criado Com Sucesso!!", desc ="O seu Perfil Foi Criado com Sucesso")
                    else:
                        return render_template("Error.html",erro = res)
                createNewUser(a,request.form.get("fullname"),request.form.get("pass2"),request.form.get("email"))
            
                return redirect(url_for('login')) 
        else:
            return render_template("Error.html",erro = "Algum Dado esta Incorrecto, Verifique e Tente Novamente",emoji='triste.gif')
    except Exception as e:
                timeLineSystem.addError(str(e),"desconhecido")
                return render_template("Error.html",erro = "Erro do Sistema")
#Admim vendo uma prova
#ADMIN
@app.route("/ver/<token>",methods=['GET']) 
def verProva(token):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('index'))
            #Deve verificar se a pessoa esta logada e tudo mais
            try:
                p = json_Save.getJSON('./data/Users/Teacher/'+s+'/provas/'+token+"/prova.json")
                dadosProva =  json_Save.getJSON('./data/Users/Teacher/'+s+'/provas/'+token+"/dadosProva.json")
                t= getAllTurmasOfTeacher(s)
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")
            return render_template("verProva.html", messages= p, dadosProva = dadosProva, turmas = t, user = s,notifications = notificationSystem.getProfNotification(s))
    return redirect(url_for('index'))
#Admin terminando prova
#ADMIN
@app.route("/terminar/<token>",methods=['GET']) 
def terminarProva(token):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('index'))
            #Deve verificar se a pessoa esta logada e tudo mais
            try:
                stopp(token,s)
                timeLineSystem.addEventToTeacherTimeLine(timeLineSystem.createEvent("UnConf","Terminou a prova "+str(token),"O professor Pausou o teste"),s)
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")
            return redirect('/ver/'+str(token))
    return redirect(url_for('index'))
#Admim retomando teste
#ADMIN
@app.route("/retomar/<token>",methods=['GET']) 
def retomarProva(token):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('index')) 
            #Deve verificar se a pessoa esta logada e tudo mais
            try:
                iniciarTeste(token,s)
                timeLineSystem.addEventToTeacherTimeLine(timeLineSystem.createEvent("UnConf","Inicio da Prova "+str(token),"O professor Iniciou o teste"),s)
            except Exception as e:
                timeLineSystem.addError(str(e),s)
            return redirect('/ver/'+str(token))
    return redirect(url_for('index'))
#Apagar um Aluno
@app.route("/delet/<teacher>/<turma>/<aluno>",methods=['GET']) 
def apagaUmAluno(teacher,turma,aluno):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False or s!=teacher):
                return redirect(url_for('index')) 
            #Deve verificar se a pessoa esta logada e tudo mais
            try:
                #Apaga o Aluno
                deletAluno(aluno,turma,s)
                timeLineSystem.addEventToTeacherTimeLine(timeLineSystem.createEvent("Conf","Apagou o Aluno "+str(aluno),"O professor apagou um Aluno"),s)
            except Exception as e:
                timeLineSystem.addError(str(e),s)
            return redirect('/turma/'+str(s)+'/'+str(turma))
    return redirect(url_for('index'))


#o ADmin faz download dos resultados da prova
#ADMIN
@app.route('/download/<token>')
def downloadFile(token):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('index'))
            try:
                saveDataFrameExcel(str(token)+".xlsx",token,s)
                timeLineSystem.addEventToTeacherTimeLine(timeLineSystem.createEvent("Conf","Download da Prova "+str(token),"O professor Fez download do teste"),s)
                return send_file('./data/Users/Teacher/'+s+'/download/'+str(token)+".xlsx", as_attachment=True)
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return redirect(url_for('index'))
    return redirect(url_for('login')) 

#O admin vendo seus utilizadores
#ADMIN
@app.route("/users",methods=['GET']) 
def users():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('index'))
            try:
                #Deve verificar se a pessoa esta logada e tudo mais
                allUsers =  json_Save.getJSON('./data/Users/Teacher/'+s+'/alunos/users.json')
                t= getAllTurmasOfTeacher(s)
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")
            return render_template("users.html",allusers =  allUsers,turmas = t, user = s,notifications = notificationSystem.getProfNotification(s))
    return redirect(url_for('index'))
#Admin verificando seus users
#ADMIN
@app.route("/users/verify/<username>/<turma>",methods=['GET']) 
def verificar(username,turma):
    #Deve verificar se a pessoa esta logada e tudo mais
    #Funcao que Gera numeros aleatorios sem repeticao
    #estou aqui
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('index'))
            try:
                validateUserToAluno(username,estudantNumberRandom(s),s,turma)
                timeLineSystem.addEventToTeacherTimeLine(timeLineSystem.createEvent("Conf","Verificação do Aluno "+str(username),"O professor Verificou o Aluno para turma "+str(turma)),s)
                dadosProvas = getAllDadosProva(s)
                for d in dadosProvas:
                    if(validation.alunoIsAutorized(s,username,d["token"])):
                        makeTestAvailableForUser(s,d["token"],username,turma)
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")  
            return redirect('/turma/'+str(s)+'/'+str(turma))
    return redirect(url_for('index'))

#ADMIN CRIANDO UMA PROVA
#ADMIN
@app.route("/prova",methods=['GET']) 
def prova():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('index'))
            #Deve verificar se a pessoa esta logada e tudo mais
            t= getAllTurmasOfTeacher(s)
            return render_template('createTest.html',turmas = t, user = s, notifications = notificationSystem.getProfNotification(s))
    return redirect(url_for('index'))
#ADMIN GUARDANDO A PROVA
#ADMIN
@app.route("/prova/create",methods=['GET','POST']) 
def createTeste():
    if(request.method=='GET'):
        return redirect(url_for('index'))
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('index'))
            #Deve verificar se a pessoa esta logada e tudo mais
    dadosProva = dict()
    try:
        maxquest = int(request.form.get('maxquest'))
        maxper = int(request.form.get('maxper'))
                #Isso so esta aqui em cima para aproveitar o try catch
        user_requis = dict()
        user_requis["turma"] = request.form.get('turma')[:len(request.form.get('turma'))-1]
        data =  request.form.get('data')
        fim  =  request.form.get('fim')
        if(len(data)!=20 and len(fim)!=20):
            return render_template("Error.html",erro = "Dados Invalidos, as Datas são invalidas")
        dadosProva["Data"] = validation.formatData(data)
        dadosProva["fim"] = validation.formatData(fim)
    except Exception as e:
                #se acontecer qualquer excessao na tentava de conversao
        timeLineSystem.addError(str(e),s)
        return render_template("Error.html",erro = "Dados Inválidos")
        #return redirect(url_for('prova'))
    try:
        newtest = list()
        per=dict()
        for quest in range(maxquest):
            quest=quest+1
            per['id'] = quest
            per['title'] = request.form.get('per'+str(quest)).replace('"',"'")
            if(per['title'] == None):
                per['title'] = "---------"
                        #'e porque foi feita alguma alteracao nos parametros hiddenn e a pessoa aumentou entao cancela
                #return redirect(url_for('prova'))
            questions = list()
            opcao = dict()
            for op in range(maxper):
                op=op+1
                opcao["id"] = op
                opcao["ques"]=request.form.get('per'+str(quest)+'_'+str(op)).replace('"',"'")
                if(opcao["ques"] == None):
                    opcao["ques"] = "---------"
                questions.append(opcao)
                opcao = dict()
            per["questions"] =  questions
            #print(per["questions"])
            try:
                per["cotacao"] = int(request.form.get('cota'+str(quest)))
                per["correcta"] = int(request.form.get('per'+str(quest)+'_corr'))
            except Exception as e:
                    #se acontecer qualquer excessao na tentava de conversao
                    return render_template("Error.html",erro = "Dados Inválidos")
            #print(per)
            newtest.append(per)
            per=dict()
                #gera um novo token
        t = str(tokenNumberRandom('data/Users/Teacher/'+s+'/provas/tokenList.json', acres=getTokenTeacher(s)))
                #Criacao do ficheiro de configuracao
        
        dadosProva["token"] = t
        parans =  ["Titulo"]
        for p in parans:
                    dadosProva[p] =  request.form.get(p)
                    if(dadosProva[p]== None):
                        #Se algum dado da prova for nulo entao cancela tudo
                        return render_template("Error.html",erro = "Algum dado Obrigatório Não foi Preechido")
        teac =  getTeacherByUserName(s)
        dadosProva['Professor'] =teac["fullname"]
        dadosProva['user_requis']=user_requis
        
                        
        #guarda a descricao  do teste
        if(request.form.get('descri')!=None):
            dadosProva["descri"]=request.form.get('descri').replace('"',"'")
        else:
            dadosProva["descri"] = "---"
                #cria um pasta em 'provas' com o nome daquele token
        os.makedirs('./data/Users/Teacher/'+s+'/provas/'+str(t))
        os.makedirs('./data/Users/Teacher/'+s+'/provas/'+str(t)+'/resultadosAlunos')
        #time.sleep(2)
        json_Save.saveJSON('./data/Users/Teacher/'+s+"/provas/"+str(t)+"/prova.json",newtest)
                
                #cria o ficheiro de configuracao
        json_Save.saveJSON('./data/Users/Teacher/'+s+'/provas/'+str(t)+"/dadosProva.json",dadosProva)
                #salva o token
        json_Save.saveJSON('./data/Users/Teacher/'+s+'/provas/'+str(t)+"/notas.json",list())
        saveToken(t,s)
        
        #Fazer com que o teste fique disponivel para os alunos autorizados de todas as turmas
        tur = user_requis['turma'].split(",")
        for tt in tur:
            #pega os alunos dessa turma
            try:
                alunosTur = json_Save.getJSON('./data/Users/Teacher/'+s+'/turmas/'+tt.replace(" ","_")+".json")["alunos"]
            except FileNotFoundError as e:
                #Caso a Turma nao existir, ela sera criada automaticamente
                criarTurma(s,tt,tt)
                alunosTur = list()
            for a in alunosTur:
                makeTestAvailableForUser(s,t,a,tt)
        timeLineSystem.addEventToTeacherTimeLine(timeLineSystem.createEvent("UnConf","Criação e Publicação da Prova "+str(t),"O professor Criou uma Nova Prova."),s)
        return redirect('/ver/'+str(t))
    except Exception as e:
        timeLineSystem.addError(str(e),s)
        return render_template("Error.html",erro = "Erro do Sistema")
#ADMIN ADITANTO O TESTE
#ADMIN
@app.route("/prova/editor",methods=['GET','POST']) 
def createEditor():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('index'))
            #Deve verificar se a pessoa esta logada e tudo mais
            try:
                maxquest = int(request.form.get('maxquest'))
                maxper = int(request.form.get('maxper'))
                t= getAllTurmasOfTeacher(s)
                turmas = ""
                for tur in t:
                    if(request.form.get(tur['nome']) == tur['nome']): 
                            turmas+= tur['nome']+","
                data =  request.form.get('data')
                fim  =  request.form.get('fim')
                print(fim)
                if(len(data)!=20 and len(fim)!=20):
                    return render_template("Error.html",erro = "Dados Invalidos, as Datas são invalidas")
            except Exception as e:
                #se acontecer qualquer excessao na tentava de conversao
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Dados Invalidos")
            
            return render_template('editor.html',maxquest=maxquest,maxper=maxper, turmas =  t,turma = turmas,user=s, data=data,fim=fim , notifications = notificationSystem.getProfNotification(s))
    return redirect(url_for('index'))

#Carrega a prova com um determinado ID
#USER
@app.route("/load/<teacher>/<id>",methods=['GET']) 
def carregarProva(teacher,id):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            if(validation.isAdmin(getUserByUserName(s))):
                #SE A PESSOA 'E ADMINISTRADORA, NAO PODE CARREGAR PROVAS COM ESSE LINK
                return redirect(url_for('index'))
            #verifica se o aluno foi autorizado a realizar a ver o teste
            try:
                if(validation.alunoIsAutorized(teacher,s,id)==False):
                    return render_template("Error.html",erro = "Sem autorização Para Ver o Documento.")
            except FileNotFoundError as e:
                timeLineSystem.addError(str(e),s)
                return redirect(url_for('error404'))
            #Verifica se o teste ainda esta disponivel
            if(validation.verificaTeste(id,teacher)):
                return render_template("Error.html",erro = "Este teste Já terminou") 
            try:
                dadosProva =  json_Save.getJSON('./data/Users/Teacher/'+teacher+'/provas/'+id+'/dadosProva.json')
                dadosProva["teacher"]= teacher
                messages = json_Save.getJSON('./data/Users/Teacher/'+teacher+'/provas/'+id+'/prova.json')
            except FileNotFoundError as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Documento não encontrado")
            #user = getUserByUserName(s)
            user = getTeacherUserByUserName(s,teacher)
            if(not validation.isAdmin(user) ):
                        imagem = 'images/magiccodeicon.png'
                        availableTestes = getAvaliableTesteForUser(s)
                        turmas  = getAlTurmas(s,availableTestes)
                        #return render_template('about.html', user=s,turmas = turmas, imagem=imagem)
                        return render_template('index.html', messages=messages, dadosProva = dadosProva, tokenProva = id,u=user,user=s,turmas = turmas, imagem=imagem, notifications = notificationSystem.getUserNotification(s))
            else:
                        #quando for um adminstrador a pesquisar
                        pass  
    return redirect(url_for('index'))

#Submete a prova
#USER
@app.route("/submit/<teacher>",methods=['GET','POST']) 
def onSubmit(teacher):
    token = request.form.get("tokenProva")
    #Deve se verificar se o Usuario pode ou não efectuar a submissão
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            if(validation.isAdmin(getUserByUserName(s))):
                #SE A PESSOA 'E ADMINISTRADORA, NAO PODE SUBMETER PROVA COM ESSE LINK
                return redirect(url_for('index'))
            #verifica se o aluno foi autorizado a realizar a ver o teste
            try:
                if(validation.alunoIsAutorized(teacher,s,token)==False):
                    return render_template("Error.html",erro = "Sem autorização Para Submeter.",emoji='gifs/no.gif')
            except FileNotFoundError as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Prova Nao Existe.",emoji='gifs/no.gif')
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro na Submissao.",emoji='gifs/no.gif')
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    try:
        if(validation.verificaTeste(token,teacher)):
            return render_template("Error.html",erro = "Este teste Já terminou",emoji='gifs/triste.gif') 
        perguntas = json_Save.getJSON('./data/Users/Teacher/'+teacher+'/provas/'+token+'/prova.json')
        numeroDeQuest = len(perguntas)
        #print(numeroDeQuest)
        respostas = list()
        x=1
        while x <= numeroDeQuest:
            try:
                respostas.append((x,int(request.form.get("q"+str(x)))))
            except TypeError as e:
                timeLineSystem.addError(str(e),s)
                pass
            finally:
                x+=1
        #print(respostas)
        aL = getAlunoByUserName(s,teacher)
        if(notaExists(aL["numeroEst"],aL["nome"],token,teacher)):
            return render_template("Error.html",erro = "Submissão Invalida! A Submissão já foi feita Pelo Utilizador",emoji='gifs/no3.gif')
        #Calcula e salva a nota
        nota = bussness.calcularNota(perguntas,respostas)
        resulAl = {
                "userName":s,
                "results":respostas,
                "nota":nota   
            }
        json_Save.saveJSON('./data/Users/Teacher/'+teacher+'/provas/'+token+'/resultadosAlunos/'+s+".json",resulAl) 
        salvarNota(aL["numeroEst"],aL["nome"],nota,token,teacher)
        try:
            dadosProva =  json_Save.getJSON('./data/Users/Teacher/'+teacher+'/provas/'+token+'/dadosProva.json')
            dadosProva["teacher"]= teacher
            messages = json_Save.getJSON('./data/Users/Teacher/'+teacher+'/provas/'+token+'/prova.json')
        except FileNotFoundError as e:
            timeLineSystem.addError(str(e),s)
            return render_template("Error.html",erro = "Documento não encontrado",emoji='gifs/triste.gif')
        user = getTeacherUserByUserName(s,teacher)
        imagem = 'images/magiccodeicon.png'
        availableTestes = getAvaliableTesteForUser(s)
        turmas  = getAlTurmas(s,availableTestes)
        prova =  getProva(s,teacher,token)
                #une os dois resultados
        timeLineSystem.addEventToUserTimeLine(timeLineSystem.createEvent("Conf","Submissão da Prova "+str(token),"O User Submeteu uma prova do professor "+str(teacher)),s)
        try:
            messages = unionProvaAndResult(messages,prova["results"])
        except Exception as e:
            #erro ira acontecer quando o estudante nao submeter nada
            pass
        if(testeDisponivel(token,teacher)):
            return render_template("result.html", resultado=-1,u=user,user=s,turmas = turmas, imagem=imagem,notifications = notificationSystem.getUserNotification(s))
        return render_template("result.html", resultado=nota,aL=aL,messages=messages, dadosProva = dadosProva, tokenProva = id,u=user,user=s,turmas = turmas, imagem=imagem,notifications = notificationSystem.getUserNotification(s))
    except Exception as e:
                #se acontecer qualquer excessao na tentava de conversao
                timeLineSystem.addError(str(e),s)
                #print(e)
                return render_template("Error.html",erro = "Erro do Sistema")  
#Ver Resultado
#USER
@app.route("/resultado/<teacher>/<token>",methods=['GET','POST']) 
def verResultado(teacher,token):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            if(validation.isAdmin(getUserByUserName(s))):
                #SE A PESSOA 'E ADMINISTRADORA, NAO PODE VER PROVA COM ESSE LINK
                return redirect(url_for('index'))
            aL = getAlunoByUserName(s,teacher)
            try:
                nota = getNotaAluno(aL["numeroEst"],token,teacher)
            except FileNotFoundError as e:
                timeLineSystem.addError(str(e),s)
                return redirect(url_for('error404'))
            except TypeError as e:
                timeLineSystem.addError(str(e),s)
                return redirect(url_for('error404'))
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro ao ver A nota",emoji='gifs/no3.gif')
            try:
                dadosProva =  json_Save.getJSON('./data/Users/Teacher/'+teacher+'/provas/'+token+'/dadosProva.json')
                dadosProva["teacher"]= teacher
                messages = json_Save.getJSON('./data/Users/Teacher/'+teacher+'/provas/'+token+'/prova.json')
            except FileNotFoundError as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Documento não encontrado",emoji='gifs/triste.gif')
            try:
                user = getTeacherUserByUserName(s,teacher)
                imagem = 'images/magiccodeicon.png'
                availableTestes = getAvaliableTesteForUser(s)
                turmas  = getAlTurmas(s,availableTestes)
                prova =  getProva(s,teacher,token)
                #une os dois resultados
                try:
                    messages = unionProvaAndResult(messages,prova["results"])
                except Exception as e:
                    #quando a lista de resultados estiver vazia
                    pass
                if(testeDisponivel(token,teacher)):
                    return render_template("result.html", resultado=-1,u=user,user=s,turmas = turmas, imagem=imagem,notifications = notificationSystem.getUserNotification(s))
                return render_template("result.html", resultado=nota,aL=aL,messages=messages, dadosProva = dadosProva, tokenProva = id,u=user,user=s,turmas = turmas, imagem=imagem,notifications = notificationSystem.getUserNotification(s))
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")               
    return redirect(url_for('index'))
#Fazer pedido para engrassar na turma de um docente
#USER
@app.route("/engressar/<teacher>/<turma>",methods=['GET']) 
def engressar(teacher,turma):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            if(validation.isAdmin(getUserByUserName(s))):
                #SE A PESSOA 'E ADMINISTRADORA, NAO PODE INGRESSAR EM NENHUMA TURMA
                return redirect(url_for('index'))
            try:
                incressarEmTurma(s,teacher,turma)
                timeLineSystem.addEventToUserTimeLine(timeLineSystem.createEvent("Conf","Pedido de Engresso a Turma "+str(turma),"O User Requisitou o engresso a turma  "+str(turma)+" do professor "+str(teacher)),s)
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Ocorreu um erro ao tentar ingressar nesta Turma",emoji='gifs/no3.gif')
            return redirect('/turma/'+teacher+'/'+turma)
    return redirect(url_for('login'))
 #ABOUT
 #USER
#sem alteracoes
@app.route("/about",methods=['GET']) 
def sobre():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            try:
                uu = getUserByUserName(s)
                if(request.method == "GET"):
                    imagem = 'images/magiccodeicon.png'
                    if(not validation.isAdmin(uu) ):     
                            availableTestes = getAvaliableTesteForUser(s)
                            turmas  = getAlTurmas(s,availableTestes)
                            return render_template('about.html', user=s,turmas = turmas, imagem=imagem, istTeacher=False,notifications = notificationSystem.getUserNotification(s) )
                    else:
                            #quando for um adminstrador a pesquisar
                            t= getAllTurmasOfTeacher(s)
                            return render_template('about.html', user=s,turmas = t, istTeacher = True, imagem=imagem,notifications = notificationSystem.getProfNotification(s))
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")
    return redirect(url_for('index'))

#USER
@app.route("/error_404",methods=['GET']) 
def error404():
    return render_template('404.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# Pesquisa alguma coisa no Painel de user        
@app.route("/search",methods=['GET','POST']) 
def search():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            try:
                uu = getUserByUserName(s)
                if(request.form.get("keytosearch")!=None):
                    fullSeach = request.form.get("keytosearch")
                    if(len(fullSeach)>0):
                        teachers,tur  = searchData(fullSeach)
                        if(not validation.isAdmin(uu) ):
                            imagem = 'images/magiccodeicon.png'
                            availableTestes = getAvaliableTesteForUser(s)
                            turmas  = getAlTurmas(s,availableTestes)
                            return render_template('resultadosPesquisa.html', teachers = teachers , teachersSize = len(teachers),
                                                turmas2 = tur,turmas2Size = len(tur), user=s,turmas = turmas, imagem=imagem , pesquisa = fullSeach, istTeacher=False,notifications = notificationSystem.getUserNotification(s))
                        else:
                            imagem = 'images/magiccodeicon.png'
                            t= getAllTurmasOfTeacher(s)
                            return render_template('resultadosPesquisa.html', teachers = teachers , teachersSize = len(teachers),
                                                turmas2 = tur,turmas2Size = len(tur), user=s,turmas = t, imagem=imagem , pesquisa = fullSeach, istTeacher = True,notifications = notificationSystem.getProfNotification(s))
                            #quando for um adminstrador a pesquisar
                            pass
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")
    return redirect(url_for('index'))

#ver perfil de uma certa pessoa
@app.route("/profile/<username>",methods=['GET']) 
def perfil(username):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            # A pessoa só pode ver um perfil se for o seu o se ele for um administrador
            #if(validation.isAdmin(getUserByUserName(s)) or s==username):
            try:
                uu = getUserByUserName(s)
                if(s==username and validation.isAdmin(uu)):
                    user= getTeacherByUserName(s)
                    t= getAllTurmasOfTeacher(s)
                    stat = "PROFESSOR"
                    imagem = 'images/magiccodeicon.png'
                    timeLine = timeLineSystem.getTimeLineTeacher(s)
                    turmas2 = getAllTurmasOfTeacher(username)
                    return render_template("profile.html",turmas = t,timeLine = timeLine, u =  user, user = s,
                                           editable=True,isTeacher=True, stat = stat, imagem=imagem,turmas2 = turmas2, istTeacher = True,notifications = notificationSystem.getProfNotification(s))
                if(s==username  and not validation.isAdmin(uu) ):
                    #se for um simple user
                    stat = "ESTUDANTE"
                    availableTestes = getAvaliableTesteForUser(s)
                    timeLine = timeLineSystem.getTimeLineUser(s)
                    turmas  = getAlTurmas(s,availableTestes)
                    user = getUserByUserName(s)
                    imagem = 'images/magiccodeicon.png'
                    return render_template("profile.html",timeLine = timeLine, u =  user, editable=True,
                                           isTeacher=False,user=s ,
                                           turmas = turmas, stat = stat, imagem=imagem, istTeacher = False,notifications = notificationSystem.getUserNotification(s))
                if(validation.isAdmin(getUserByUserName(username)) and s!=username ):
                    #se o perfil que se pretende ver for de administrador e nao for ele pode se ver mas nao editar
                    stat = "PROFESSOR"
                    timeLine = timeLineSystem.getTimeLineTeacher(username)
                    user = getTeacherByUserName(username)
                    turmas2 = getAllTurmasOfTeacher(username)
                    imagem = 'images/magiccodeicon.png'
                    if(validation.isAdmin(uu)):
                        t= getAllTurmasOfTeacher(s)
                        return render_template("profile.html",timeLine = timeLine, u =  user, editable=False,
                                            isTeacher=True,user=s ,
                                            turmas = t,turmas2 = turmas2, stat = stat, imagem=imagem, istTeacher = True,notifications = notificationSystem.getProfNotification(s))
                    else:
                        availableTestes = getAvaliableTesteForUser(s)
                        turmas  = getAlTurmas(s,availableTestes)
                        availableTestes = getAvaliableTesteForUser(s)
                        turmas  = getAlTurmas(s,availableTestes)
                        return render_template("profile.html",timeLine = timeLine, u =  user, editable=False,
                                            isTeacher=True,user=s ,
                                            turmas = turmas,turmas2 = turmas2, stat = stat, imagem=imagem, istTeacher = False,notifications = notificationSystem.getUserNotification(s))
                if(s!=username and validation.isAdmin(uu)):
                    #se for administrador que quer ver um perfil simples
                    stat = "ESTUDANTE"
                    t= getAllTurmasOfTeacher(s)
                    user = getUserByUserName(username)
                    timeLine = timeLineSystem.getTimeLineUser(username)
                    imagem = 'images/magiccodeicon.png'
                    return render_template("profile.html",timeLine = timeLine, u =  user,user = s, editable=False,
                                           isTeacher=False, stat = stat, imagem=imagem, turmas = t, istTeacher = True, notifications = notificationSystem.getProfNotification(s))
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")              
    return redirect(url_for('index'))
    
#ver perfil de uma certa pessoa
@app.route("/turma/<teacher>/<turma>",methods=['GET']) 
def verturma(teacher,turma):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            try:
                tur = getTurma(teacher,turma)
                if(tur==None):
                    timeLineSystem.addError("Turma não encontrada",s)
                    return redirect(url_for('error404'))
                uu = getUserByUserName(s)
                #se for user simples
                alunos =  json_Save.getJSON('./data/Users/Teacher/'+teacher+'/alunos/alunos.json')
                if(not validation.isAdmin(uu) ):
                        #se for um simple user
                        availableTestes = getAvaliableTesteForUser(s)
                        turmas  = getAlTurmas(s,availableTestes)
                        notInturma = True
                        if(turmaIsRequested(s,turma,teacher)):
                            notInturma = False
                        if(s in tur["alunos"]):
                            canSeeStudents = True
                            alunos = getOnlyStudentsOfClass(alunos,turma)
                        else:
                            alunos = list()
                            canSeeStudents = False
                        imagem = 'images/magiccodeicon.png'
                        return render_template("turma.html",da=availableTestes,user=s ,
                                            turmas = turmas, imagem=imagem,  t=tur, teacher=teacher,
                                            notInturma=notInturma, canSeeStudents=canSeeStudents , alunos = alunos, isTurmaTeacher  = False,
                                            isTeacher = False, istTeacher = False, notifications = notificationSystem.getUserNotification(s))
                #se a pessoa for administrador mas a turma nao ser sua
                if(validation.isAdmin(uu) and s!=teacher):
                        t= getAllTurmasOfTeacher(s)
                        imagem = 'images/magiccodeicon.png'
                        return render_template("turma.html",user = s,turmas = t,
                                            notInturma=False, imagem=imagem, t=tur, 
                                            teacher=teacher, canSeeStudents = False, isTurmaTeacher  = False, alunos = list(), isTeacher = True, 
                                            istTeacher = True, notifications = notificationSystem.getProfNotification(s))
                #quando a pessoa 'e admin e a turma 'e sua
                if(validation.isAdmin(uu) and s==teacher ):
                        t= getAllTurmasOfTeacher(s)
                        alunos = getOnlyStudentsOfClass(alunos,turma)
                        alunosToAprov = getTeacherUsersUnaprovad(s,turma)
                        imagem = 'images/magiccodeicon.png'
                        return render_template("turma.html",user = s,turmas = t,
                                            notInturma=False, imagem=imagem, t=tur, 
                                            teacher=teacher, canSeeStudents = True , alunos = alunos, 
                                            isTurmaTeacher = True, isTeacher = True,
                                            alunosToAcept=alunosToAprov, istTeacher = True,notifications = notificationSystem.getProfNotification(s))
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")
    return redirect(url_for('index'))
#ajuda
@app.route("/help",methods=['GET']) 
def helpPage():
    return "Pagina de Ajuda"
#desempenho academico
@app.route("/desempenho",methods=['GET']) 
def desempenhoDoEstudante():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            try:
                uu = getUserByUserName(s)
                if(not validation.isAdmin(uu) ):
                    imagem = 'images/magiccodeicon.png'
                    availableTestes = getAvaliableTesteForUser(s)
                    turmas  = getAlTurmas(s,availableTestes)
                    return render_template("desempenho.html", user=s,turmas = turmas, imagem=imagem,notifications = notificationSystem.getUserNotification(s))
                else:
                    return redirect(url_for('index'))
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")
    redirect(url_for('index'))
#desempenho academico para docentes
@app.route("/desempenhoacademico",methods=['GET']) 
def desempenhoGeralDosEstudantes():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            try:
                imagem = 'images/magiccodeicon.png'
                uu = getUserByUserName(s)
                if(validation.isAdmin(uu) ):
                    t= getAllTurmasOfTeacher(s)
                    return render_template("desempenhoestudantes.html", user=s,turmas = t, imagem=imagem,notifications = notificationSystem.getProfNotification(s))
                else:
                    return redirect(url_for('index'))
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")
    redirect(url_for('index'))
    
    
#fale connosco
@app.route("/faleconnosco",methods=['GET',"POST"]) 
def talktous():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            try:
                uu = getUserByUserName(s)
                if(request.method == "GET"):
                    if(not validation.isAdmin(uu) ):
                            imagem = 'images/magiccodeicon.png'
                            availableTestes = getAvaliableTesteForUser(s)
                            turmas  = getAlTurmas(s,availableTestes)
                            return render_template("talkwithus.html", user=s,turmas = turmas,
                                                   imagem=imagem, istTeacher = False,notifications = notificationSystem.getUserNotification(s))
                    else:
                             t= getAllTurmasOfTeacher(s)
                             return render_template("talkwithus.html", user=s,turmas = t, istTeacher = True,
                                                    notifications = notificationSystem.getProfNotification(s))
                            #quando for um adminstrador a pesquisar      
                elif (request.method == "POST") :
                    if(request.form.get("contact")!=None and request.form.get("comen") ):
                        da = datetime.now().strftime('%D - %H:%M:%S')
                        contact = {
                                "userName":s,
                                "data": da,
                                "contacto":request.form.get("contact"),
                                "comentario":request.form.get("comen"),
                                "anexo":"--"
                            }
                        commenList  =  json_Save.getJSON("./data/Users/SystemData/talkWithUs.json")
                        commenList.append(contact)
                        json_Save.saveJSON("./data/Users/SystemData/talkWithUs.json", commenList)
                        #,    
                        return render_template("Sucess.html",title= "Mensagem Enviada!!", desc ="Muito Obrigado Por ter Nos enviado uma Mensagem!! A nossa equipa entrará em contacto consigo dentro de algum tempo.")
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema") 
    return redirect(url_for('index'))

#actualizar informações de Perfil
@app.route("/updateinformation",methods=['GET','POST']) 
def updateInfor():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None): 
          try:
            user = getUserByUserName(s)
            #Actualizando UserName ou Email
            att = ["fullname","email"]
            for at in att:
                if(request.form.get(at)!=None):
                    if(len(request.form.get(at))>0):
                        user[at] = request.form.get(at)
            #Actualizando a senha
            if(request.form.get("pass")!=None and request.form.get("pass2")):
                if(len(request.form.get("pass"))>0 and len(request.form.get("pass2"))>0):
                    if (validation.verifyLoginData(s,request.form.get("pass"))):
                        result = hashlib.md5(request.form.get("pass2").encode())
                        user["password"] = str(result.hexdigest())
                    else:
                        return render_template("Error.html",erro = "A Senha Anterior é Invalida.",emoji='gifs/no3.gif')
            #actualizando o token
            if(validation.isAdmin(user)):
                if(request.form.get("token")!=None):
                   if(len(request.form.get("token"))>0): 
                    if (tokenTeacherIsValid(request.form.get("token"))):
                        updateToken(s,request.form.get("token"))
                    else:
                        return render_template("Error.html",erro = "Token Invalido",emoji='gifs/no3.gif')
                if(request.form.get('bio')!=None):
                   if(len(request.form.get("bio"))>0):
                    timeLineSystem.addEventToTeacherTimeLine(timeLineSystem.createEvent("UnConf","Actualização de Dados","O professor actualizou a BIO"),s)  
                    user['bio'] = request.form.get('bio')
                user2 =  user
                user2.pop("password")
                updateUser(user2,'./data/Users/Teacher/teachers.json')
            updateUser(user,"./data/users.json")
            timeLineSystem.addEventToUserTimeLine(timeLineSystem.createEvent("UnConf","Actualização de Dados ","O User Actualizou alguns dados do Perfil"),s)
            return redirect('/profile/'+s)
          except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")     
    return redirect(url_for('index'))

#getNotas do estudante e dadas de testes em Json
@app.route("/user/getnotasedadastese",methods=['GET']) 
def getNotasJson():
    cookie = request.cookies.get('SessionID')
    #print(cookie)
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            try:
                uu = getUserByUserName(s)
                if(not validation.isAdmin(uu) ): 
                    dados = getNotaAndData(s)
                    #print(dados)
                    return jsonify(dados)
                else:
                    return  jsonify(dict())
            except Exception as e:
                timeLineSystem.addError(str(e),s)
    return  jsonify(dict())
#pega todas perguntas nao respondidad erradas e certas e nao respond de todas as provas
@app.route("/teacher/getcenr",methods=['GET']) 
def getcenr():
    cookie = request.cookies.get('SessionID')
    #print(cookie)
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            try:
                uu = getUserByUserName(s)
                if(validation.isAdmin(uu) ): 
                    dados = getAllQuantErradasCertasNRes(s)
                    #print(dados)
                    return jsonify(dados)
                else:
                    return  jsonify(dict())
            except Exception as e:
                timeLineSystem.addError(str(e),s)
    return  jsonify(dict())
#criar um turma
@app.route("/createturma",methods=['GET','POST']) 
def createTurma():
    cookie = request.cookies.get('SessionID')
    #print(cookie)
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            try:
                uu = getUserByUserName(s)
                if(validation.isAdmin(uu) ):
                    if(request.method == 'GET'):
                        provasConf = getAllDadosProva(s)
                        t= getAllTurmasOfTeacher(s)
                        return render_template("criarTurma.html",provas = provasConf, turmas = t, user =  s)
                    elif (request.method == 'POST'):
                        nome = request.form.get('nome')
                        descri =  request.form.get('descri')
                        criarTurma(s,nome,descri)
                        return redirect('/turma/'+s+'/'+nome)  
            except Exception as e:
                timeLineSystem.addError(str(e),s)
                return render_template("Error.html",erro = "Erro do Sistema")
    return redirect(url_for('index'))



#getNotas do estudante e dadas de testes em Json
@app.route("/user/perguntasqunt",methods=['GET']) 
def getperguntasqunt():
    cookie = request.cookies.get('SessionID')
    #print(cookie)
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            try:
                uu = getUserByUserName(s)
                if(not validation.isAdmin(uu) ): 
                    dados = getPerguntasQuntAENR(s)
                    #print(dados)
                    return jsonify(dados)
                else:
                    return  jsonify(dict())
            except Exception as e:
                timeLineSystem.addError(str(e),s)
    return  jsonify(dict())



#Assim que uma notificacao 'e enviada,
# ela deve ser primeiro tratada neste link e so depois 'e que deve ser redirecionada
#abri a notificacao
@app.route("/notification",methods=['GET']) 
def openNotification():
    cookie = request.cookies.get('SessionID')
    #print(cookie)
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        link =  request.args.get('link')
        try:
            id =  int(request.args.get("id"))
            notificationSystem.removeNotification(id,getUserByUserName(s))
            return redirect(link)
        except Exception as e:
           return redirect(url_for('index'))
        #apaga a notificacao 
    return redirect(url_for('index'))


if __name__== "__main__":
    app.run(host="0.0.0.0",port=80,debug=True)