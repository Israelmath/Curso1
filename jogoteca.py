import time

import pymysql
from flask import Flask, render_template, request, redirect, session, flash, url_for, send_from_directory
import os

from daos.dao import JogoDao, UsuarioDao
from models.jogoModel import Jogo
from models.usuarioModel import Usuario


app = Flask(__name__)
app.secret_key = 'Israel'

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWD'] = '.,Avaiana41'
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_PORT'] = 3306
app.config['UPLOADS_PATH'] = os.path.dirname(os.path.abspath(__file__)) + '/upload'

db = pymysql.connect(user='root',
                     passwd='.,Avaiana41',
                     host='127.0.0.1',
                     db='jogoteca',
                     port=3306)

jogoDao = JogoDao(db)
usuarioDao = UsuarioDao(db)

listJogos = jogoDao.listar()

@app.route('/')
def home():
    listJogos = jogoDao.listar()
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login'))
    return render_template('home.html', titulo='Jogos do Israel', jogos=listJogos)

@app.route('/novo')
def novaTela():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('novaTela')))
    return render_template('novo.html', titulo='Novo jogo')

@app.route('/editar/<int:id>')
def editar(id):
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        return redirect(url_for('login', proxima=url_for('editar')))
    jogo = jogoDao.busca_por_id(id)
    nomeImagem = recuperaImagem(id)
    # jogoNome = f"capa{id}.jpg"
    print(nomeImagem)
    if nomeImagem is None:
        nomeImagem = 'choseImg.png'

    return render_template('editar.html', titulo='Editar jogo', jogo=jogo, nomeArquivo=nomeImagem)

@app.route('/criar', methods=['POST'])
def adicionaJogo():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    jogoNovo = Jogo(nome, categoria, console)
    jogo = jogoDao.salvar(jogoNovo)


    arquivo = request.files['arquivo']
    uploadPath = app.config['UPLOADS_PATH']
    timestamp = time.time()
    if arquivo.filename != '':
        arquivo.save(f'{uploadPath}/capa{jogo.id}-{timestamp}.jpg')

    return redirect(url_for('home'))

@app.route('/atualizar/', methods=['POST'])
def atualizar():
    id = int(request.form['id'])
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']

    jogoEditado = Jogo(nome, categoria, console, id=id)

    deletaImagem(jogoEditado.id)
    jogoDao.salvar(jogoEditado)

    arquivo = request.files['arquivo']
    uploadPath = app.config['UPLOADS_PATH']
    timestamp = time.time()
    if arquivo.filename != '':
        arquivo.save(f'{uploadPath}/capa{jogoEditado.id}-{timestamp}.jpg')

    return redirect(url_for('home'))

@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)

@app.route('/autenticar', methods=['POST'])
def auth():
    usuario = usuarioDao.buscar_por_id(request.form['usuario'])

    if usuario:
        userLog = Usuario(request.form['usuario'], request.form['usuario'], request.form['senha'])
        if userLog.senha == str(usuario.senha):
            session['usuario_logado'] = userLog.usuario
            flash(userLog.usuario + ' logou com sucesso!')
            proximaPagina = request.form['proxima']
            print(f'proximaPagina: {proximaPagina}')
            return redirect(proximaPagina)
        else:
            flash('Hum... Isso não deu certo. Tente novamente.')
            return redirect(url_for('login'))
    else:
        flash('Hum... Isso não deu certo. Tente novamente.')
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Nenhum usuário logado!')
    return redirect(url_for('login'))

@app.route('/excluir/<int:id>')
def excluir(id):
    jogoDao.deletar(id)

    return redirect(url_for('home'))

@app.route('/upload/<nome_arquivo>')
def imgGenerics(nome_arquivo):
    return send_from_directory('upload', nome_arquivo)

def recuperaImagem(id: int):
    print(f'recuperaImagem - type(id): {type(id)}')
    print(f'capa{id}')

    for nomeArquivo in os.listdir(app.config['UPLOADS_PATH']):
        if f'capa{id}' in nomeArquivo:
            return nomeArquivo
    return None

def deletaImagem(id: int):
    print(f'deletaImagem - type(id): {type(id)}')
    print(f'capa{id}')

    nomeArquivo = recuperaImagem(id)
    if nomeArquivo is not None:
        print(f"nomeArquivo: {nomeArquivo}")
        print(f"path: {os.path.join(app.config['UPLOADS_PATH'], nomeArquivo)}")
        os.remove(os.path.join(app.config['UPLOADS_PATH'], nomeArquivo))

app.run('127.0.0.1', debug=True, port=2032)