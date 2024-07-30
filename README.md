## Sobre o TesteFacil
![image](https://github.com/user-attachments/assets/49b4cd55-71fd-4514-9217-e0d94b2ee4df)
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
1. Escolhendo o tipo de conta
![image](https://github.com/user-attachments/assets/6d0442ee-44ea-46f1-960a-b2e23502ee86)
3. Abrindo Conta Professor utilizando token
![image](https://github.com/user-attachments/assets/87330c98-0f12-4a81-bf1f-b0d93c148e9d)
5. Abrindo Conta Estudante/Aluno
![image](https://github.com/user-attachments/assets/ba2765a8-b26e-4799-80e5-06d867273fef)

7. Dashboard Professor
![image](https://github.com/user-attachments/assets/646f531c-a914-4a1b-ac77-3e3102a526da)
![image](https://github.com/user-attachments/assets/7dcb673d-83b9-4932-adb9-f7a39a1f050c)
10. Professor Criando Turma
 ![image](https://github.com/user-attachments/assets/c1b0024e-f0b2-47d2-aeda-67790b67fa00)
12. Professor Criando Teste
![image](https://github.com/user-attachments/assets/2ac60b6f-585a-479e-b653-138b3d2593b1)
![image](https://github.com/user-attachments/assets/f8302fa7-3e8d-4cc0-b8c5-379299c00e32)
![image](https://github.com/user-attachments/assets/b896c4ec-209e-4a79-ab0c-1ff428473e82)
14. Aluno Incressando em Turma
![image](https://github.com/user-attachments/assets/6c913f93-bbc1-4850-abf3-065a700f3587)
16. Aluno Visualizando Testes
![image](https://github.com/user-attachments/assets/d08db320-4c08-42ef-8187-33eaca33b450)
![image](https://github.com/user-attachments/assets/db363838-f090-4453-a978-a98e59f94477)
17. Professor vendo o teste
![image](https://github.com/user-attachments/assets/55ab24c0-b9de-438b-b414-0c800ba06649)
19. Professor vendo estatísticas
![image](https://github.com/user-attachments/assets/ea523ab8-400d-4fbb-9701-15b014bfb0c9)

Desenvolvido por... Narciso Pascoal Albino Cadeado (@magiccode4Dim)
narcisopascoal97@gmail.com.

 
