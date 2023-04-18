#APLICACAO PRINCIPAL
from flask import Flask,request,render_template, url_for, redirect, make_response,send_file
from util import json_Save, bussness,validation,sessionsSystem
from dataManScript import *
import os
import random
import time
import secrets

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
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                #Pega os dados do usuario e lhe lanca para a DashBoard
                availableTestes = getAvaliableTesteForUser(s)
                turmas  = getAlTurmas(s,availableTestes)
                if(len(availableTestes)==0):
                    return render_template('dashboardUser.html',user=s, turmas = turmas)
                else:
                    #vai pegar todas as notas do aluno com base em dados do teste
                    return render_template('dashboardUser.html',da=availableTestes,user=s , turmas = turmas)
            provasConf = getAllDadosProva(s)
            return render_template("dashboardAdmin.html", provas = provasConf)
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
            sessionsSystem.removeSession(s)
    return render_template('login.html')
#AUTENTICATION
#GENERAL
@app.route("/autentication",methods=['GET','POST']) 
def autenticar():
    if(request.method=='GET'):
        return redirect(url_for('login'))
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
            if(validation.isAdmin(getUserByUserName(request.form.get("username")))==False):
                #se a pessoa nao for administradora
                #cria uma nova resposta
                availableTestes = getAvaliableTesteForUser(request.form.get("username"))
                turmas  = getAlTurmas(request.form.get("username"),availableTestes)
                if(len(availableTestes)==0):
                    resposta = make_response(render_template('dashboardUser.html',user=request.form.get("username"), turmas = turmas))
                else:
                    resposta = make_response(render_template('dashboardUser.html',da=availableTestes,user=request.form.get("username"), turmas = turmas))
            else:
                #se a pessoa for administradora
                provasConf = getAllDadosProva(request.form.get("username"))
                resposta = make_response(render_template("dashboardAdmin.html",provas = provasConf))
            resposta.set_cookie("SessionID",cookie)
            return resposta
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
                    return render_template("Error.html",erro = "Criado Com Sucesso")
                else:
                    return render_template("Error.html",erro = res)
            createNewUser(a,request.form.get("fullname"),request.form.get("pass2"),request.form.get("email"))
           
            return redirect(url_for('login')) 
    else:
        return render_template("Error.html",erro = "Algum Dado esta Incorrecto, Verifique e Tente Novamente",emoji='triste.gif')
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
            except Exception as e:
                return redirect(url_for('index'))
            return render_template("verProva.html", messages= p)
    return redirect(url_for('login'))
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
            except Exception as e:
                pass
            return redirect(url_for('index'))
    return redirect(url_for('login'))
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
            except Exception as e:
                pass
            return redirect(url_for('index'))
    return redirect(url_for('login'))
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
                return send_file('./data/Users/Teacher/'+s+'/download/'+str(token)+".xlsx", as_attachment=True)
            except Exception as e:
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
            #Deve verificar se a pessoa esta logada e tudo mais
            allUsers =  json_Save.getJSON('./data/Users/Teacher/'+s+'/alunos/users.json')
            atributs = ["userName","fullname","email","turma","Verificado"]
            return render_template("users.html",allusers =  allUsers, atributs=atributs)
    return redirect(url_for('login'))
#Admin verificando seus users
#ADMIN
@app.route("/users/verify/<username>",methods=['GET']) 
def verificar(username):
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
                validateUserToAluno(username,estudantNumberRandom(s),s)
                dadosProvas = getAllDadosProva(s)
                for d in dadosProvas:
                    if(validation.alunoIsAutorized(s,username,d["token"])):
                        makeTestAvailableForUser(s,d["token"],username)
            except Exception as e:
                return redirect(url_for('users'))
            return redirect(url_for('users'))
    return redirect(url_for('login'))
#o ADMINISTRADOR VENDO SEUS ESTUDANTES
#ADMIN
@app.route("/students",methods=['GET']) 
def students():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('index'))
            #Deve verificar se a pessoa esta logada e tudo mais
            allUsers =  json_Save.getJSON('./data/Users/Teacher/'+s+'/alunos/alunos.json')
            atributs = ["numeroEst","userName","fullname","turma"]
            return render_template("students.html",allusers =  allUsers, atributs=atributs)
    return redirect(url_for('login'))
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
            return render_template('createTest.html')
    return redirect(url_for('login'))
#ADMIN GUARDANDO A PROVA
#ADMIN
@app.route("/prova/create",methods=['GET','POST']) 
def createTeste():
    if(request.method=='GET'):
        return redirect(url_for('login'))
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
        return redirect(url_for('login'))
            #Deve verificar se a pessoa esta logada e tudo mais
    try:
        maxquest = int(request.form.get('maxquest'))
        maxper = int(request.form.get('maxper'))
                #Isso so esta aqui em cima para aproveitar o try catch
        user_requis = dict()
        user_requis["turma"] = request.form.get('turma')
    except Exception as e:
                #se acontecer qualquer excessao na tentava de conversao
        return redirect(url_for('prova'))
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
                return redirect(url_for('prova'))
        #print(per)
        newtest.append(per)
        per=dict()
            #gera um novo token
    t = str(tokenNumberRandom('data/Users/Teacher/'+s+'/provas/tokenList.json', acres=getTokenTeacher(s)))
            #Criacao do ficheiro de configuracao
    dadosProva = dict()
    dadosProva["token"] = t
    parans =  ["Data","Escola","Professor","Titulo","fim"]
    for p in parans:
                dadosProva[p] =  request.form.get(p)
                if(dadosProva[p]== None):
                    #Se algum dado da prova for nulo entao cancela tudo
                    return redirect(url_for('prova'))
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
        for a in alunosTur:
            makeTestAvailableForUser(s,t,a)
                  
    return redirect(url_for('index'))
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
            except Exception as e:
                #se acontecer qualquer excessao na tentava de conversao
                return redirect(url_for('prova'))
            
            return render_template('editor.html',maxquest=maxquest,maxper=maxper)
    return redirect(url_for('login'))

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
                    return render_template("Error.html",erro = "Sem autorização Para Ver o Documento.",emoji='gifs/no.gif')
            except FileNotFoundError as e:
                return redirect(url_for('error404'))
            #Verifica se o teste ainda esta disponivel
            if(validation.verificaTeste(id,teacher)):
                return render_template("Error.html",erro = "Este teste Já terminou",emoji='gifs/calmdown.gif') 
            try:
                dadosProva =  json_Save.getJSON('./data/Users/Teacher/'+teacher+'/provas/'+id+'/dadosProva.json')
                dadosProva["teacher"]= teacher
                messages = json_Save.getJSON('./data/Users/Teacher/'+teacher+'/provas/'+id+'/prova.json')
            except FileNotFoundError as e:
                return render_template("Error.html",erro = "Documento não encontrado",emoji='gifs/triste.gif')
            user = getUserByUserName(s)  
            return render_template('index.html', messages=messages, dadosProva = dadosProva, tokenProva = id,user=user)
    return redirect(url_for('login'))

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
                return render_template("Error.html",erro = "Prova Nao Existe.",emoji='gifs/no.gif')
            except Exception as e:
                return render_template("Error.html",erro = "Erro na Submissao.",emoji='gifs/no.gif')
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
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
    if(testeDisponivel(token,teacher)):
        return render_template("result.html", resultado="Nota Estará Disponivel Assim que o Teste Terminar",aL=aL,emoji='gifs/calmdown.gif')
    return render_template("result.html", resultado=nota,aL=aL,emoji='gifs/congrats.gif')
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
                return redirect(url_for('error404'))
            except TypeError as e:
                return redirect(url_for('error404'))
            except Exception as e:
                return render_template("Error.html",erro = "Erro ao ver A nota",emoji='gifs/no3.gif')
            if(testeDisponivel(token,teacher)):
                return render_template("result.html", resultado="Nota Estará Disponivel Assim que o Teste Terminar",aL=aL,emoji='gifs/calmdown.gif')
            return render_template("result.html", resultado=nota,aL=aL,emoji='gifs/congrats.gif')
    else:
        return redirect(url_for('login'))
    return redirect(url_for('login'))
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
            except Exception as e:
                return render_template("Error.html",erro = "Ocorreu um erro ao tentar ingressar nesta Turma",emoji='gifs/no3.gif')
            return redirect(url_for('index'))
    return redirect(url_for('login'))
 #ABOUT
 #USER
#sem alteracoes
@app.route("/about",methods=['GET']) 
def sobre():
    return render_template('about.html')

#USER
@app.route("/error_404",methods=['GET']) 
def error404():
    return render_template('404.html')

# Pesquisa alguma coisa no Painel de user        
@app.route("/search",methods=['GET','POST']) 
def search():
    return "Results to search"

#ver perfil de uma certa pessoa
@app.route("/profile/<username>",methods=['GET']) 
def perfil(username):
    return "Results to search"
#ver perfil de uma certa pessoa
@app.route("/turma/<teacher>/<turma>",methods=['GET']) 
def verturma(teacher,turma):
    return "Results to search"
#ajuda
@app.route("/help",methods=['GET']) 
def helpPage():
    return "Pagina de Ajuda"
@app.route("/desempenho",methods=['GET']) 
def desempenhoDoEstudante():
    return "retorna o desempenho do estudante"
@app.route("/faleconnosco",methods=['GET']) 
def talktous():
    return "fala cmigo"




if __name__== "__main__":
    app.run(host="0.0.0.0",port=80,debug=True)