import bcrypt
from domain.model.usuario import Usuario

class UsuarioRepository:
    
    def _hashear_contraseña(self, contraseña):
        """Cifra la contraseña con bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(contraseña.encode(), salt).decode()
    
    def _verificar_contraseña(self, contraseña, hash_guardado):
        """Verifica si la contraseña coincide con el hash"""
        return bcrypt.checkpw(contraseña.encode(), hash_guardado.encode())
    
    def get_all(self, db):
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        return usuarios
    
    def get_por_correo(self, db, correo):
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
        usuario = cursor.fetchone()
        cursor.close()
        return usuario
    
    def insertar_usuario(self, db, usuario: Usuario):
        cursor = db.cursor()
        contraseña_cifrada = self._hashear_contraseña(usuario.contraseña)
        cursor.execute(
            "INSERT INTO usuarios (nombre, correo, contraseña) VALUES (%s, %s, %s)",
            (usuario.nombre, usuario.correo, contraseña_cifrada)
        )
        db.commit()
        cursor.close()
    
    def verificar_credenciales(self, db, correo, contraseña):
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM usuarios WHERE correo = %s",
            (correo,)
        )
        usuario = cursor.fetchone()
        cursor.close()
        
        if usuario and self._verificar_contraseña(contraseña, usuario["contraseña"]):
            return usuario
        return None
