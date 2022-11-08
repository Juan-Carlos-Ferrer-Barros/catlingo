# importamos la base de datos
import sqlite3

# Conectarse con la base de datos. Si no existe el archivo lo creará
con = sqlite3.connect('db/catlingo.db')
cur = con.cursor()

# Crear las tablas

# Palabras
cur.execute("""
    CREATE TABLE words (
    id         INTEGER NOT NULL,
    spanish    TEXT,
    english    TEXT,
    italian    TEXT,
    catalan    TEXT,
    PRIMARY KEY(id AUTOINCREMENT)
    )
    """
)

# Respuestas
cur.execute(
    """
    CREATE TABLE answers (
    id          INTEGER NOT NULL,
    spanish     TEXT,
    word        TEXT,
    submit      TEXT,
    result      INTEGER,
    PRIMARY KEY(id AUTOINCREMENT)
    )
    """
)

# Usuarios
cur.execute(
    """
    CREATE TABLE users (
    id          INTEGER NOT NULL,
    language    TEXT NOT NULL,
    correct     INTEGER NOT NULL,
    wrong       INTEGER NOT NULL,
    PRIMARY KEY(id AUTOINCREMENT)
    )
    """
)

cur.execute(
    """
    INSERT INTO users
    (language, correct, wrong)
    VALUES
    ('spanish', 0, 0)
    """
)

cur.execute(
    """
    INSERT INTO words
    (spanish, english, italian, catalan)
    VALUES
    ('gato', 'cat', 'gatto', 'gat')
    """
)

# Cerrar conexion DB
con.commit()
con.close()