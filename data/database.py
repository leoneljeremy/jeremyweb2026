import mysql.connector 



# database = mysql.connector.connect( # LLAMAMOS AL FUNCION CONNECT PARA CONECTARNOS
#     host ='localhost',
#     port = 3306,

#     ssl_disabled = False,
#     user ='root', #USUARIO QUE USAMOS NOSOTROS
#     password ='root' #CONTRASEÑA CON LA QUE NOS CONECTAMOS
#     # database='oscar'
# ) 

database = mysql.connector.connect( # LLAMAMOS AL FUNCION CONNECT PARA CONECTARNOS
    #host='informatica.iesquevedo.es',
    host='83.33.148.8',
    port = 3333,
    ssl_disabled = True,
    user ='root', #USUARIO QUE USAMOS NOSOTROS
    password ='1asir', #CONTRASEÑA CON LA QUE NOS CONECTAMOS
    database='JeremyEspinoza'
) 