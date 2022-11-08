from flask import Flask, render_template, request, redirect, url_for
# base de datos
import sqlite3

app = Flask(__name__)

@app.route('/index', methods=['GET'])
@app.route('/', methods=['GET'])
def index():
		# Conectarse con la DB
    con = sqlite3.connect('DB/catlingo.db')
    cur = con.cursor()

    # Obtener toda la informacion de la tabla users. 
		# (idioma a practicar, respuestas correctas e incorrectas)
    cur.execute("SELECT * FROM users")
    user_data = cur.fetchall()[0] # ejemplo (0, "italian", 2, 0)
    con.close()
    language = user_data[1]
    correct = user_data[2]
    wrong = user_data[3]

    # traduce el idioma al español
    language = traslate_language(language)
    word_tuple = get_random_word()

		##### Nueva funcionalidad :) #####
    # Mostrar ultimas 4 respuestas
    answers = -1
    # se activa si se ingreso una respuesta
    if correct > 0 or wrong > 0:
        con = sqlite3.connect('DB/catlingo.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM answers")
        answers = cur.fetchall()
        con.close()
        # invertir lista
        answers = answers[::-1]
        if len(answers) > 4:
            # ultimas 4 respuestas
            answers = answers[:4]

    return render_template('index.html', word_data=word_tuple, correct=correct, wrong=wrong, answers=answers, language=language)

# enumeracion de datos
from enum import Enum

class Languages(Enum):
    SPANISH = 1
    ENGLISH = 2
    ITALIAN = 3
    CATALAN = 4

def traslate_language(language):
    language = language.upper()
    language = Languages[language].value

    if language ==1:
        language = "español"
    if language == 2:
        language = "inglés"
    if language == 3:
        language = "italiano"
    if language == 4:
        language = "catalán"
    return language

# al principio importaremos random
import random

def get_random_word():
    # conexion con la DB
    con = sqlite3.connect('DB/catlingo.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM words")
    # obtener data
    words = cur.fetchall()
    # Cerrar conexion DB
    con.close()
    # cantidad de palabras
    count_words = (len(words))
    # seleccionar palabra de forma aleatoria
    random_id = random.randrange(0, count_words)

    word_tuple = words[random_id]
    return word_tuple
    
@app.route('/check/<int:id>', methods=['POST'])
def check(id):
    # si se responde el formulario se activa
    if request.method == 'POST':
        # recibir palabra del formulario
        submit_word = request.form['submit_word']
        # palabra en mayusculas
        submit_word = submit_word.upper()

        # conectar DB
        con = sqlite3.connect('DB/catlingo.db')
        cur = con.cursor()
        # obtener idioma
        cur.execute("SELECT * FROM users")
        user_data= cur.fetchall()[0]
        language = user_data[1]
        correct = user_data[2]
        wrong = user_data[3]

        correct_word, spanish_word = get_word(id, language)
        correct_word = correct_word.upper()

        # resultado correcto
        if correct_word == submit_word:
            correct = correct + 1
            cur.execute("UPDATE users SET correct = ?", (correct,))
            result = 1
        # resultado incorrecto
        else:
            wrong = wrong + 1
            cur.execute("UPDATE users SET wrong = ?", (wrong,))
            result = 0

        # guardar respuesta
        cur.execute("INSERT INTO answers (spanish, word, submit, result) VALUES (?, ?, ?, ?)",
                    (spanish_word, correct_word, submit_word, result,))
        # guardar los cambios en la tabla
        con.commit()
        cur.execute("SELECT * FROM answers")
        DB_answers = cur.fetchall()
        print(DB_answers)
        con.close()

    return redirect(url_for('index'))


def get_word(id, language):
    # conexion con la DB
    con = sqlite3.connect('DB/catlingo.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM words WHERE id=?", (id,))
    # obtener data
    words = cur.fetchall()[0]
    # Cerrar conexion DB
    con.close()

    language = language.upper()
    # posicion de la palabra buscada en la tupla
    pos = Languages[language].value
    # seleccionar palabra en la tupla, la cual contiene la palabra en distintos idiomas.
    select_word = words[pos]
    spanish_word = words[Languages.SPANISH.value]
    return select_word, spanish_word

@app.route('/change_language/<string:language>', methods=['GET'])
def change_language(language):
    con = sqlite3.connect('DB/catlingo.db')
    cur = con.cursor()
    cur.execute("UPDATE users SET language = ? WHERE id=1", (language,))
    con.commit()
    con.close()
    return redirect(url_for('index'))

@app.route('/reset', methods=['GET'])
def reset():
    con = sqlite3.connect('DB/catlingo.db')
    cur = con.cursor()
    cur.execute("UPDATE users SET correct = 0, wrong = 0 WHERE id=1")
    cur.execute("delete from answers")
    con.commit()
    con.close()
    return redirect(url_for('index'))

@app.route('/words')
def words():
    con = sqlite3.connect('DB/catlingo.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM words")
    words = cur.fetchall()
    con.close()
    return render_template('words.html', words=words)

@app.route('/words/delete/<int:id>', methods=['DELETE'])
def delete(id):
    # Conectar con la DB
    con = sqlite3.connect('DB/catlingo.db')
    cur = con.cursor()
    cur.execute("DELETE FROM words WHERE id=?",
                (id,))
    # Guardar los cambios en la tabla
    con.commit()
    # Cerrar conexion con la DB
    con.close()

    return redirect(url_for('words'))

@app.route('/words/add', methods=['POST'])
def add():
    # si se responde el formulario se activa
    if request.method == 'POST':
        # recibir datos del formulario
        spanish = request.form['spanish']
        english = request.form['english']
        italian = request.form['italian']
        catalan = request.form['catalan']
        # Conectar con la DB
        con = sqlite3.connect('DB/catlingo.db')
        cur = con.cursor()
        # Guardar en la DB
        cur.execute("INSERT INTO words (spanish, english, italian, catalan) VALUES (?, ?, ?, ?)",
                    (spanish, english, italian, catalan,))
        # Enviar los cambios a la tabla
        con.commit()
        # Cerrar conexion con la DB
        con.close()
    # redirige al html words
    return redirect(url_for('words'))

@app.route('/words/edit/<int:id>', methods=['GET'])
def edit(id):
    # conectar DB
    con = sqlite3.connect('DB/catlingo.db')
    cur = con.cursor()
    cur.execute("SELECT * FROM words WHERE id=?", (id,))
    word_data = cur.fetchall()[0]

    # todas las palabras
    cur.execute("SELECT * FROM words")
    words = cur.fetchall()

    con.close()
    return render_template('edit.html', word=word_data, words=words)

@app.route('/words/update/<int:id>', methods=['PATCH'])
def update(id):
    # obtener datos formulario
    spanish = request.form['spanish']
    english = request.form['english']
    italian = request.form['italian']
    catalan = request.form['catalan']
    # conectar DB
    con = sqlite3.connect('DB/catlingo.db')
    cur = con.cursor()
    cur.execute("UPDATE words SET spanish = ?, english = ?, italian = ?, catalan = ? where id = ?",
                (spanish, english, italian, catalan, id))

    con.commit()
    con.close()
    return redirect(url_for('words'))


if __name__ == '__main__':
    app.run(debug=True)
