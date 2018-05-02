# MeSHx-Notes
Web System for Clinical Notes Information Extraction

Como instanciar o projeto:

    Criar uma pasta para o projeto.

    No diretório criado no passo anterior (dentro do terminal) executar o comando: "git clone https://github.com/nlp-pucrs/clinical-notes-web.git".

    Ainda no terminal: "cd clinical-notes-web/clinical_notes"
    
        "pip install -r requirements.txt" para instalar todos os pacotes que são necessários paras a aplicação poder ser executada.
    
    Finalmente, para executar o servidor: 
    *A versão do Python deve ser 3 ou superior.
    
        No Windows:

            "python manage.py runserver"

            Caso tenha tanto python 2.x e 3.x ao invés de "python" é preciso especificar onde está instalado Python 3.x.
                Ex.:
                    "C:/Python35/python manage.py runserver"

        No Linux:

            "python manage.py runserver" 
            
            Se tiver ambas as versões (2.x e 3.x) usar: "python3 manage.py runserver"
