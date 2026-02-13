class VideojuegoRepository:
    
    def get_all(self, db):
        """Obtiene todos los videojuegos"""
        try:
            cursor = db.cursor()
            sql = """
                SELECT v.id, v.nombre, v.precio, v.genero, v.valoracion,
                       GROUP_CONCAT(c.nombre) as consolas
                FROM videojuegos v
                LEFT JOIN videojuego_consola vc ON v.id = vc.videojuego_id
                LEFT JOIN consolas c ON vc.consola_id = c.id
                GROUP BY v.id, v.nombre, v.precio, v.genero, v.valoracion
            """
            cursor.execute(sql)
            juegos = cursor.fetchall()
            return juegos
        except Exception as e:
            print(f"Error en get_all: {e}")
            return []
        finally:
            cursor.close()

    
    def get_por_consola(self, db, nombre_consola):
        """Obtiene videojuegos por consola específica"""
        try:
            cursor = db.cursor()
            sql = """
                SELECT v.id, v.nombre, v.precio, v.genero, v.valoracion
                FROM videojuegos v
                INNER JOIN videojuego_consola vc ON v.id = vc.videojuego_id
                INNER JOIN consolas c ON vc.consola_id = c.id
                WHERE c.nombre = %s
                ORDER BY v.nombre
            """
            cursor.execute(sql, (nombre_consola,))
            juegos = cursor.fetchall()
            return juegos
        except Exception as e:
            print(f"Error en get_por_consola: {e}")
            return []
        finally:
            cursor.close()

    
    def get_por_id(self, db, videojuego_id):
        """Obtiene un videojuego por ID"""
        try:
            cursor = db.cursor()
            sql = "SELECT id, nombre, precio, genero, valoracion FROM videojuegos WHERE id = %s"
            cursor.execute(sql, (videojuego_id,))
            juego = cursor.fetchone()
            return juego
        except Exception as e:
            print(f"Error en get_por_id: {e}")
            return None
        finally:
            cursor.close()

    
    def insertar_videojuego(self, db, videojuego, consola):
        """Inserta un nuevo videojuego"""
        try:
            cursor = db.cursor()
            
            # Insertar el videojuego
            sql = """
                INSERT INTO videojuegos (nombre, precio, genero, valoracion)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (videojuego.nombre, videojuego.precio, 
                                videojuego.genero, videojuego.valoracion))
            
            # Obtener el ID del videojuego insertado
            videojuego_id = cursor.lastrowid
            
            # Obtener el ID de la consola
            sql_consola = "SELECT id FROM consolas WHERE nombre = %s"
            cursor.execute(sql_consola, (consola,))
            resultado = cursor.fetchone()
            
            if resultado:
                consola_id = resultado[0]
                
                # Insertar en la tabla videojuego_consola
                sql_relacion = """
                    INSERT INTO videojuego_consola (videojuego_id, consola_id)
                    VALUES (%s, %s)
                """
                cursor.execute(sql_relacion, (videojuego_id, consola_id))
            
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error en insertar_videojuego: {e}")
        finally:
            cursor.close()

    
    def insertar_videojuego_multiples_consolas(self, db, videojuego, consolas):
        """Inserta un nuevo videojuego con múltiples consolas"""
        try:
            cursor = db.cursor()
            
            # Insertar el videojuego
            sql = """
                INSERT INTO videojuegos (nombre, precio, genero, valoracion)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (videojuego.nombre, videojuego.precio, 
                                videojuego.genero, videojuego.valoracion))
            
            # Obtener el ID del videojuego insertado
            videojuego_id = cursor.lastrowid
            
            # Insertar en la tabla videojuego_consola para cada consola
            for consola in consolas:
                sql_consola = "SELECT id FROM consolas WHERE nombre = %s"
                cursor.execute(sql_consola, (consola,))
                resultado = cursor.fetchone()
                
                if resultado:
                    consola_id = resultado[0]
                    
                    # Insertar en la tabla videojuego_consola
                    sql_relacion = """
                        INSERT INTO videojuego_consola (videojuego_id, consola_id)
                        VALUES (%s, %s)
                    """
                    cursor.execute(sql_relacion, (videojuego_id, consola_id))
            
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error en insertar_videojuego_multiples_consolas: {e}")
        finally:
            cursor.close()

    
    def borrar_videojuego(self, db, videojuego_id):
        """Borra un videojuego"""
        try:
            cursor = db.cursor()
            
            # Borrar las relaciones
            sql_relaciones = "DELETE FROM videojuego_consola WHERE videojuego_id = %s"
            cursor.execute(sql_relaciones, (videojuego_id,))
            
            # Borrar el videojuego
            sql = "DELETE FROM videojuegos WHERE id = %s"
            cursor.execute(sql, (videojuego_id,))
            
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error en borrar_videojuego: {e}")
        finally:
            cursor.close()

    
    def actualizar_videojuego(self, db, videojuego):
        """Actualiza un videojuego"""
        try:
            cursor = db.cursor()
            sql = """
                UPDATE videojuegos 
                SET nombre = %s, precio = %s, genero = %s, valoracion = %s
                WHERE id = %s
            """
            cursor.execute(sql, (videojuego.nombre, videojuego.precio, 
                                videojuego.genero, videojuego.valoracion, videojuego.id))
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error en actualizar_videojuego: {e}")
        finally:
            cursor.close()

    
    def buscar_videojuegos(self, db, nombre="", genero=""):
        """Busca videojuegos por nombre y/o género"""
        try:
            cursor = db.cursor()
            sql = "SELECT id, nombre, precio, genero, valoracion FROM videojuegos WHERE 1=1"
            params = []
            
            if nombre:
                sql += " AND nombre LIKE %s"
                params.append(f"%{nombre}%")
            
            if genero:
                sql += " AND genero = %s"
                params.append(genero)
            
            sql += " ORDER BY nombre"
            cursor.execute(sql, params)
            juegos = cursor.fetchall()
            return juegos
        except Exception as e:
            print(f"Error en buscar_videojuegos: {e}")
            return []
        finally:
            cursor.close()
    
    def get_consolas_por_videojuego(self, db, videojuego_id):
        """Obtiene las consolas de un videojuego específico"""
        try:
            cursor = db.cursor()
            sql = """
                SELECT c.nombre
                FROM consolas c
                INNER JOIN videojuego_consola vc ON c.id = vc.consola_id
                WHERE vc.videojuego_id = %s
            """
            cursor.execute(sql, (videojuego_id,))
            consolas = cursor.fetchall()
            return [consola[0] for consola in consolas]
        except Exception as e:
            print(f"Error en get_consolas_por_videojuego: {e}")
            return []
        finally:
            cursor.close()

    
    def actualizar_consolas_videojuego(self, db, videojuego_id, nuevas_consolas):
        """Actualiza las consolas de un videojuego"""
        try:
            cursor = db.cursor()
            
            # Borrar las consolas actuales
            sql_delete = "DELETE FROM videojuego_consola WHERE videojuego_id = %s"
            cursor.execute(sql_delete, (videojuego_id,))
            
            # Insertar las nuevas consolas
            for consola in nuevas_consolas:
                sql_consola = "SELECT id FROM consolas WHERE nombre = %s"
                cursor.execute(sql_consola, (consola,))
                resultado = cursor.fetchone()
                
                if resultado:
                    consola_id = resultado[0]
                    
                    sql_insert = """
                        INSERT INTO videojuego_consola (videojuego_id, consola_id)
                        VALUES (%s, %s)
                    """
                    cursor.execute(sql_insert, (videojuego_id, consola_id))
            
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Error en actualizar_consolas_videojuego: {e}")
        finally:
            cursor.close()