import json
#guarda como um ficheiro  json  
def saveJSON(nomeFile,jsonOb):
    with open(nomeFile, 'w') as json_file:
        json.dump(jsonOb, json_file, indent=4)

#Busca a prova com o nome do ficheirp
def getJSON(nomeFile):
    with open(nomeFile, 'r') as json_file:
        jsonOb = json.load(json_file)
    return jsonOb