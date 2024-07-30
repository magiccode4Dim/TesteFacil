## Sobre o TesteFacil
O TesteFacil é um sistema desenvolvido para ser utilizado em instituições de ensino, cujo propósito é a realização provas de escolha múltipla com correção automática. O sistema tem um funcionamento simples, e pode se adequar facilmente para os modelos de ensino da maioria das instituições.
No sistema, alunos e professores podem cadastrar-se em poucos passos. 
O testeFacil é bastante optimizado, ágil e não precisa de um sistema de gestão de base de dados. O armazenamento dos dados é feito no sistema de ficheiro do servidor ou em um volume conectado a um Servidor FTP, utilizando a arquitetura de uma base de dados orientada a documentos. Este facto possibilita que o testefacil seja facilmente instalado em servidores pequenos, com pelo menos 1 núcleo de CPU e 500MB de memória RAM.

## Instalação
O testefacil foi desenvolvido em Python Flask, que é um framework bastante leve. Para instalar basta seguir os seguintes Passos:
1. git clone https://github.com/magiccode4Dim/TesteFacil.git
2. cd TesteFacil
3. pip3 install -r requeriments.txt
4. python TesteFacilApp.py (Iniciar o servidor Flask).

**NOTA**: Todos os dados gerados durante a utilização do Sistema, estão armazenados no directorio /data

## Configuração iniciais
No directorio do projecto, existe o ficheiro dataManScript.py, que contém algumas funções para a execução de tarefas administrativas. Uma das tarefas administrativas que devem ser executadas, é a criação de tokens-chave para a abertura de contas para professores. Para criar 10 tokens, por exemplo, deve-se executar a seguinte função:

## Screenshots

 
