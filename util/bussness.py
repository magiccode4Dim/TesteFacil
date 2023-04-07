
def getPerguntaById(id, perguntas):
    for p in perguntas:
        if p['id'] == id:
            return p
    return None


#Calcula a nota da pessoa com base nas respostas
def calcularNota(prova, respostas):
    cont = 0
    for res in respostas:
        per = getPerguntaById(res[0],prova)
        if(per!= None):
            if(per["correcta"] == res[1]):
                cont+=per["cotacao"]
    return cont    