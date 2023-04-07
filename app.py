from flask import Flask,request,render_template, url_for, redirect, make_response
from util import json_Save, bussness,validation,sessionsSystem
import time
import random
from dataManScript import salvarNota,createNewUser,getUserByUserName,getAlunoByUserName,notaExists,getAvaliableTesteForUser,testeDisponivel, getNotaAluno
app = Flask(__name__, template_folder="user_Templates")


@app.route("/",methods=['GET']) 
def index():
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #Pega os dados do usuario e lhe lanca para a DashBoard
            availableTestes = getAvaliableTesteForUser(s)
            if(len(availableTestes)==0):
                return render_template('dashboard.html',user=s)
            else:
                return render_template('dashboard.html',da=availableTestes,user=s)
    return redirect(url_for('login'))  
#Autenticacao e Cadastro
@app.route("/login",methods=['GET']) 
def login():
    #Se o utilizador entrar na pagina de login enquanto tem os cookies de sessao activos, esses cookies devem ser apagados
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            sessionsSystem.removeSession(s)
    return render_template('login.html')
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
                return redirect(url_for('login'))
            except Exception as e:
                pass
            #Apaga qualquer cookie anterior do utilizador se existir
            sessionsSystem.removeSession(request.form.get("username"))
            #cria uma nova sessao
            cookie = str(request.form.get("username").__hash__())+str(random.random())
            sessionsSystem.addSession(request.form.get("username"),cookie)
            #cria uma nova resposta
            availableTestes = getAvaliableTesteForUser(request.form.get("username"))
            if(len(availableTestes)==0):
                resposta = make_response(render_template('dashboard.html',user=request.form.get("username")))
            else:
                resposta = make_response(render_template('dashboard.html',da=availableTestes,user=request.form.get("username")))
            resposta.set_cookie("SessionID",cookie)
            return resposta
    return redirect(url_for('login'))  
@app.route("/createaccount",methods=['GET']) 
def createAccont():
    #Se o utilizador entrar na pagina de criar conta enquanto tem os cookies de sessao activos, esses cookies devem ser apagados
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            sessionsSystem.removeSession(s)
    try:
        turmas = json_Save.getJSON("./config.json")["turmas"]
        classes = json_Save.getJSON("./config.json")["classes"]
    except Exception as e:
        return redirect(url_for('error404'))
    return render_template('cadastrar.html', turmas=turmas, classes = classes)
@app.route("/cadastrar",methods=['GET','POST']) 
def cadastrar():
    if(request.method=='GET'):
        return redirect(url_for('createAccont'))
    if(len(request.form.get("fullname"))>1 and len(request.form.get("pass"))>1 and len(request.form.get("pass"))==len(request.form.get("pass2")) ):
        if(validation.userNameExists(request.form.get("username"))):
            return render_template("Error.html",erro = "O UserName Introduzido Já Existe, Tente Outro",emoji='gifs/triste.gif')
        else:
            a = request.form.get("username")
            #a=a[:len(a)-1]
            if a[len(a)-1] == ' ':
                a=a[:len(a)-1]
            createNewUser(a,request.form.get("fullname"),request.form.get("turma"),int(request.form.get("classe")),request.form.get("pass2"))
            return redirect(url_for('login')) 
    else:
        return render_template("Error.html",erro = "Algum Dado esta Incorrecto, Verifique e Tente Novamente",emoji='triste.gif') 

@app.route("/about",methods=['GET']) 
def sobre():
    return render_template('about.html')
#Carrega a prova com um determinado ID
@app.route("/<id>",methods=['GET']) 
def carregarProva(id):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #Nessa parte pode pegar os dados do usuario
            #Vefica se user esta aprovado
            user =  getUserByUserName(s)
            if(user["isAproved"]==0):
                return render_template("Error.html",erro = "O utilizador ainda não foi aprovado como Estudante.",emoji='gifs/calmdown.gif')
            #verifica se o aluno foi autorizado a realizar a ver o teste
            try:
                if(validation.alunoIsAutorized(user,id)==False):
                    return render_template("Error.html",erro = "Sem autorização Para Ver o Documento.",emoji='gifs/no.gif')
            except FileNotFoundError as e:
                return redirect(url_for('error404'))
            #Verifica se o teste ainda esta disponivel
            if(validation.verificaTeste(id)):
                return render_template("Error.html",erro = "Este teste Já terminou",emoji='gifs/calmdown.gif') 
            try:
                dadosProva =  json_Save.getJSON('provas/'+id+'/dadosProva.json')
                messages = json_Save.getJSON('provas/'+id+'/prova.json')
            except FileNotFoundError as e:
                return render_template("Error.html",erro = "Documento não encontrado",emoji='gifs/triste.gif')  
            return render_template('index.html', messages=messages, dadosProva = dadosProva, tokenProva = id,user=user)
    return redirect(url_for('login'))

#Submete a prova
@app.route("/submeter",methods=['GET','POST']) 
def onSubmit():
    token = request.form.get("tokenProva")
    #Deve se verificar se o Usuario pode ou não efectuar a submissão
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            #Nessa parte pode pegar os dados do usuario
            #Vefica se user esta aprovado
            user =  getUserByUserName(s)
            if(user["isAproved"]==0):
                return render_template("Error.html",erro = "O utilizador ainda não foi aprovado como Estudante.",emoji='gifs/triste.gif')
            #verifica se o aluno foi autorizado a realizar a ver o teste
            try:
                if(validation.alunoIsAutorized(user,token)==False):
                    return render_template("Error.html",erro = "Sem autorização Para Submeter.",emoji='gifs/no.gif')
            except FileNotFoundError as e:
                return render_template("Error.html",erro = "Sem autorização Para Submeter.",emoji='gifs/no.gif')
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))
    if(validation.verificaTeste(token)):
         return render_template("Error.html",erro = "Este teste Já terminou",emoji='gifs/triste.gif') 
    perguntas = json_Save.getJSON('provas/'+token+'/prova.json')
    numeroDeQuest = len(perguntas)
    #print(numeroDeQuest)
    respostas = list()
    x=1
    try:
        while x <= numeroDeQuest:
            respostas.append((x,int(request.form.get("q"+str(x)))))
            x+=1
    except TypeError as e:
        return render_template("Error.html",erro = "Submissão Invalida, Porque nem todas as questões foram preenchidas",emoji='gifs/no2.gif') 
    #print(respostas)
    nota = bussness.calcularNota(perguntas,respostas)
    aL = getAlunoByUserName(user["userName"])
    if(notaExists(aL["numeroEst"],aL["nome"],token)):
        return render_template("Error.html",erro = "Submissão Invalida! A Submissão já foi feita Pelo Utilizador",emoji='gifs/no3.gif') 
    salvarNota(aL["numeroEst"],aL["nome"],nota,token)
    if(testeDisponivel(token)):
        return render_template("result.html", resultado="Nota Estará Disponivel Assim que o Teste Terminar",aL=aL,emoji='gifs/calmdown.gif')
    return render_template("result.html", resultado=nota,aL=aL,emoji='gifs/congrats.gif')
    """Ja se sabe qual 'e o Aluno, as suas respostas e de qual prova se trata"""

#Ver Resultado
@app.route("/resultado/<token>",methods=['GET','POST']) 
def verResultado(token):
    cookie = request.cookies.get('SessionID')
    if(cookie!=None):
        s = sessionsSystem.verfiySession(cookie)
        if(s!=None):
            aL = getAlunoByUserName(s)
            try:
                nota = getNotaAluno(aL["numeroEst"],token)
            except FileNotFoundError as e:
                return redirect(url_for('error404'))
            except TypeError as e:
                return redirect(url_for('error404'))
            if(testeDisponivel(token)):
                return render_template("result.html", resultado="Nota Estará Disponivel Assim que o Teste Terminar",aL=aL,emoji='gifs/calmdown.gif')
            return render_template("result.html", resultado=nota,aL=aL,emoji='gifs/congrats.gif')
    else:
        return redirect(url_for('login'))

@app.route("/error_404",methods=['GET']) 
def error404():
    return render_template('404.html')

@app.route("/tes",methods=['GET']) 
def teste():
    return render_template('teste.html')

if __name__== "__main__":
    app.run(host="0.0.0.0",debug=True)