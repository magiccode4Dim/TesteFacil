#PAINEL DE CONTROLE DE ADMINISTRADOR
from flask import Flask,request,render_template, url_for, redirect, make_response,send_file
from util import json_Save, bussness,validation,sessionsSystem
from dataManScript import validateUserToAluno,estudantNumberRandom, tokenNumberRandom,saveToken,getAllDadosProva,stopp,saveDataFrameExcel,iniciarTeste,getUserByUserName,getTokenTeacher
import os
import random
import time

app = Flask(__name__, template_folder="admin_Templates")

#ok
@app.route("/",methods=['GET']) 
def index():
    #Deve verificar se a pessoa esta logada e tudo mais
    #Pega os ficheiros de configuracao de todas as provas
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('login'))
            provasConf = getAllDadosProva(s)
            return render_template("dashboardAdmin.html", provas = provasConf)
    return redirect(url_for('login'))
#Ver prova
#ok
@app.route("/ver/<token>",methods=['GET']) 
def verProva(token):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('login'))
            #Deve verificar se a pessoa esta logada e tudo mais
            try:
                p = json_Save.getJSON('./data/Users/Teacher/'+s+'/provas/'+token+"/prova.json")
            except Exception as e:
                return redirect(url_for('index'))
            return render_template("verProva.html", messages= p)
    return redirect(url_for('login'))

#Terminar prova
#ok
@app.route("/terminar/<token>",methods=['GET']) 
def terminarProva(token):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('login'))
            #Deve verificar se a pessoa esta logada e tudo mais
            try:
                stopp(token,s)
            except Exception as e:
                pass
            return redirect(url_for('index'))
    return redirect(url_for('login')) 
#Retormar Prova
#ok
@app.route("/retomar/<token>",methods=['GET']) 
def retomarProva(token):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('login')) 
            #Deve verificar se a pessoa esta logada e tudo mais
            try:
                iniciarTeste(token,s)
            except Exception as e:
                pass
            return redirect(url_for('index'))
    return redirect(url_for('login')) 

#Baixar os Resultados Excel
#Enviando ficheiros
#ok 
@app.route('/download/<token>')
def downloadFile(token):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('login')) 
            try:
                saveDataFrameExcel(str(token)+".xlsx",token,s)
                return send_file('./data/Users/Teacher/'+s+'/download/'+str(token)+".xlsx", as_attachment=True)
            except Exception as e:
                return redirect(url_for('index'))
    return redirect(url_for('login')) 


#Login
@app.route("/login",methods=['GET']) 
def login():
    #Se o utilizador entrar na pagina de login enquanto tem os cookies de sessao activos, esses cookies devem ser apagados
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            sessionsSystem.removeSession(s)
    return render_template('login.html')
#post Login
#ok
@app.route("/autenticar",methods=['GET','POST']) 
def autenticar():
    if(request.method=='GET'):
        return redirect(url_for('login'))
    if(request.form.get("username") != None and request.form.get("pass") != None):
        if(validation.verifyLoginData(request.form.get("username"),request.form.get("pass"))):
            #Se for administrador cancela
            us = getUserByUserName(request.form.get("username"))
            try:
                #Vai tentar aceder a essa chave... se ele for administ nao pode aceder
                chave = us["isAdmin"]
            except Exception as e:
                return redirect(url_for('login'))
            #Se chegar nessa fase 'e porque trata-se de um admin
            #Apaga qualquer cookie anterior do utilizador se existir
            sessionsSystem.removeSession(request.form.get("username"))
            #cria uma nova sessao
            cookie = str(request.form.get("username").__hash__())+str(random.random())
            sessionsSystem.addSession(request.form.get("username"),cookie)
            provasConf = getAllDadosProva(request.form.get("username"))
            resposta = make_response(render_template("dashboardAdmin.html",provas = provasConf))
            resposta.set_cookie("SessionID",cookie)
            return resposta
    return redirect(url_for('login')) 

#Users
@app.route("/users",methods=['GET']) 
def users():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('login')) 
            #Deve verificar se a pessoa esta logada e tudo mais
            allUsers =  json_Save.getJSON('./data/Users/Teacher/'+s+'/alunos/users.json')
            atributs = ["userName","fullname","turma","classe","Verificado"]
            return render_template("users.html",allusers =  allUsers, atributs=atributs)
    return redirect(url_for('login'))
#ok 
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
                return redirect(url_for('login'))
            try:
                validateUserToAluno(username,estudantNumberRandom(s),s)
            except Exception as e:
                return redirect(url_for('users'))
            return redirect(url_for('users'))
    return redirect(url_for('login')) 
#Studentes
#ok
@app.route("/students",methods=['GET']) 
def students():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('login'))
            #Deve verificar se a pessoa esta logada e tudo mais
            allUsers =  json_Save.getJSON('./data/Users/Teacher/'+s+'/alunos/alunos.json')
            atributs = ["numeroEst","userName","fullname","turma","classe","Activo"]
            return render_template("students.html",allusers =  allUsers, atributs=atributs)
    return redirect(url_for('login'))
#criacao e manipulacao de provas
#sem alteracoes
@app.route("/prova",methods=['GET']) 
def prova():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('login'))
            #Deve verificar se a pessoa esta logada e tudo mais
            return render_template('createTest.html')
    return redirect(url_for('login'))
#ok
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
                return redirect(url_for('login'))
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
        user_requis["classe"] = int(request.form.get('classe'))
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
                    #'e porque foi feita alguma alteracao nos parametros hiddenn e a pessoa aumentou entao cancela
            return redirect(url_for('prova'))
        questions = list()
        opcao = dict()
        for op in range(maxper):
            op=op+1
            opcao["id"] = op
            opcao["ques"]=request.form.get('per'+str(quest)+'_'+str(op)).replace('"',"'")
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
                    
            #cria um pasta em 'provas' com o nome daquele token
    os.makedirs('./data/Users/Teacher/'+s+'/provas/'+str(t))
    #time.sleep(2)
    json_Save.saveJSON('./data/Users/Teacher/'+s+"/provas/"+str(t)+"/prova.json",newtest)
            
            #cria o ficheiro de configuracao
    json_Save.saveJSON('./data/Users/Teacher/'+s+'/provas/'+str(t)+"/dadosProva.json",dadosProva)
            #salva o token
    json_Save.saveJSON('./data/Users/Teacher/'+s+'/provas/'+str(t)+"/notas.json",list())
    saveToken(t,s)
                  
    return redirect(url_for('index'))
    
             
#sem alteracoes
@app.route("/prova/editor",methods=['GET','POST']) 
def createEditor():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #verifica se a pessoa 'e admin
            if(validation.isAdmin(getUserByUserName(s))==False):
                return redirect(url_for('login'))
            #Deve verificar se a pessoa esta logada e tudo mais
            try:
                maxquest = int(request.form.get('maxquest'))
                maxper = int(request.form.get('maxper'))
            except Exception as e:
                #se acontecer qualquer excessao na tentava de conversao
                return redirect(url_for('prova'))
            
            return render_template('editor.html',maxquest=maxquest,maxper=maxper)
    return redirect(url_for('login'))
        

if __name__== "__main__":
    app.run(host="0.0.0.0",port=7373,debug=True)