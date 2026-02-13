class Usuario:
    def __init__(self, id: int, nombre: str, correo: str, contraseña: str, es_admin: int = 0):
        self.id = id
        self.nombre = nombre
        self.correo = correo
        self.contraseña = contraseña
        self.es_admin = es_admin
