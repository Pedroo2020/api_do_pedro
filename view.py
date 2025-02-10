from flask import Flask, jsonify, request
from main import app, con
from flask_bcrypt import generate_password_hash, check_password_hash
import re


def validar_senha(senha):
    if len(senha) < 8:
        return jsonify({"error": "A senha deve ter pelo menos 8 caracteres."}), 400

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", senha):
        return jsonify({"error": "A senha deve conter pelo menos um símbolo especial (!@#$%^&*...)."}), 400

    if not re.search(r"[A-Z]", senha):
        return jsonify({"error": "A senha deve conter pelo menos uma letra maiúscula."}), 400

    if len(re.findall(r"\d", senha)) < 2:
        return jsonify({"error": "A senha deve conter pelo menos dois números."}), 400

    return True

@app.route('/livro', methods=['GET'])
def livro():
    cur = con.cursor()
    cur.execute("SELECT ID_LIVRO, TITULO, AUTOR, ANO_PUBLICACAO FROM LIVROS")
    livros = cur.fetchall()
    livros_dic = []
    for livro in livros:
            livros_dic.append({
                'id_livro': livro[0],
                'titulo': livro[1],
                'autor': livro[2],
                'ano_publicacao': livro[3]
            })
    return jsonify(mensagem='Lista de livros', livros=livros_dic)

@app.route('/livro', methods=['POST'])
def livro_post():
    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor = con.cursor()
    cursor.execute("SELECT 1 FROM LIVROS WHERE TITULO = ?", (titulo,))

    if cursor.fetchone():
        return jsonify("Livro já cadastrado")

    cursor.execute("INSERT INTO LIVROS(TITULO, AUTOR, ANO_PUBLICACAO) VALUES (?, ?, ?)", (titulo, autor, ano_publicacao))

    con.commit()
    cursor.close()

    return jsonify({
        'message': "Livro cadastrado com sucesso!",
        'livro': {
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao
        }
    })

@app.route('/livro/<int:id>', methods=['PUT'])
def livro_put(id):
    cursor = con.cursor()

    cursor.execute("SELECT ID_LIVRO, TITULO, AUTOR, ANO_PUBLICACAO FROM LIVROS WHERE ID_LIVRO = ?", (id,))
    livro_data = cursor.fetchone()

    if not livro_data:
        cursor.close()
        return jsonify({"Livro não encontrado"})

    data = request.get_json()
    titulo = data.get('titulo')
    autor = data.get('autor')
    ano_publicacao = data.get('ano_publicacao')

    cursor.execute("UPDATE LIVROS SET TITULO = ?, AUTOR = ?, ANO_PUBLICACAO = ? WHERE ID_LIVRO = ?",
                   (titulo, autor, ano_publicacao, id))

    con.commit()
    cursor.close()

    return jsonify({
        'message': "Livro atualizado com sucesso!",
        'livro': {
            'titulo': titulo,
            'autor': autor,
            'ano_publicacao': ano_publicacao
        }
    })

@app.route('/livro/<int:id>', methods=['DELETE'])
def deletar_livro(id):
    cursor = con.cursor()

    cursor.execute("SELECT 1 FROM livros WHERE ID_LIVRO = ?", (id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Livro não encontrado"}), 404

    cursor.execute("DELETE FROM livros WHERE ID_LIVRO = ?", (id,))
    con.commit()
    cursor.close()

    return jsonify({
        'message': "Livro excluído com sucesso!",
        'id_livro': id
    })

@app.route('/usuario', methods=['GET'])
def listar_usuario():
    cur = con.cursor()
    cur.execute("SELECT ID_USUARIO, NOME, EMAIL FROM USUARIOS")
    usuarios = cur.fetchall()
    usuarios_dic = []
    for usuario in usuarios:
        usuarios_dic.append({
            'id_usuario': usuario[0],
            'nome': usuario[1],
            'email': usuario[2]
        })
    return jsonify(mensagem='Lista de usuarios', usuarios=usuarios_dic)

@app.route('/usuario', methods=['POST'])
def cadastrar_usuario():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    senha_check = validar_senha(senha)
    if senha_check is not True:
        return senha_check

    cursor = con.cursor()
    cursor.execute("SELECT 1 FROM USUARIOS WHERE EMAIL = ?", (email,))

    if cursor.fetchone():
        return jsonify({"error": "Email já cadastrado"}), 400

    senha = generate_password_hash(senha).decode('utf-8')

    cursor.execute("INSERT INTO USUARIOS(NOME, EMAIL, SENHA) VALUES (?, ?, ?)", (nome, email, senha))

    con.commit()
    cursor.close()

    return jsonify({
        'message': "Usuário cadastrado com sucesso!",
        'usuario': {
            'nome': nome,
            'email': email,
            'senha': senha
        }
    })

@app.route('/usuario/<int:id>', methods=['PUT'])
def editar_usuario(id):
    cursor = con.cursor()

    cursor.execute("SELECT ID_USUARIO, NOME, EMAIL, SENHA FROM USUARIOS WHERE ID_USUARIO = ?", (id,))
    usuario_data = cursor.fetchone()

    if not usuario_data:
        cursor.close()
        return jsonify({"error": "Usuário não encontrado"}), 404



    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    cursor.execute("SELECT 1 FROM USUARIOS WHERE EMAIL = ?", (email,))

    if cursor.fetchone():
        return jsonify("Email já cadastrado")

    cursor.execute("UPDATE USUARIOS SET NOME = ?, EMAIL = ?, SENHA = ? WHERE ID_USUARIO = ?",
                   (nome, email, senha, id))

    con.commit()
    cursor.close()

    return jsonify({
        'message': "usuario atualizado com sucesso",
        'usuario': {
            'nome': nome,
            'email': email,
            'Senha': senha
        }
    })

@app.route('/usuario/<int:id>', methods=['DELETE'])
def excluir_usuario(id):
    cursor = con.cursor()

    cursor.execute("SELECT 1 FROM USUARIOS WHERE ID_USUARIO = ?", (id,))
    if not cursor.fetchone():
        cursor.close()
        return jsonify({"error": "Usuário não encontrado"}), 404

    cursor.execute("DELETE FROM USUARIOS WHERE ID_USUARIO = ?", (id,))
    con.commit()
    cursor.close()

    return jsonify({
        'message': "Usuário excluído com sucesso!",
        'id_usuario': id
    })

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')

    if not email or not senha:
        return jsonify({"error": "Todos os campos (email, senha) são obrigatórios."}), 400

    cursor = con.cursor()
    cursor.execute("SELECT SENHA FROM USUARIOS WHERE EMAIL =?", (email,))
    usuario = cursor.fetchone()
    cursor.close()

    if not usuario:
        return jsonify({"error": "Usuário ou senha inválidos."}), 401

    senha_armazenada = usuario[0]
    if check_password_hash(senha_armazenada, senha):
        return jsonify({"message": "Login realizado com sucesso!"})

    return jsonify({"error": "Senha incorreta."}), 401