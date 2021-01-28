from flask import Flask, render_template, request, redirect, session, flash, url_for

app = Flask(__name__)
app.secret_key = 'Israel'

class Jogo:
    def __init__(self, nome, categoria, console):
        self.nome = nome
        self.categoria = categoria
        self.console = console

class Usuario:
    def __init__(self, id, usuario, senha):
        self.id = id
        self.usuario = usuario
        self.senha = senha

    def __str__(self):
        return f'Usuário: {self.usuario}\nSenha: {self.senha}'

listJogos = [Jogo('Dark Souls', 'Ação', 'PC'),
             Jogo('Final Fantasy', 'RPG', 'Playstation 2'),
             Jogo('Castlevania', 'Plataforma', 'Xbox 360')]

dictUsuarios = {'Israel': Usuario(1, 'Israel', 123),
                'Joice': Usuario(2, 'Joice', 321),
                'Rafaella': Usuario(3, 'Rafaella', 456)}

@app.route('/')
def lista():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        print(f"lista: {url_for('login')}")
        return redirect(url_for('login'))
    return render_template('lista.html', titulo='Jogos do Israel', jogos=listJogos)

@app.route('/novo')
def novaTela():
    if 'usuario_logado' not in session or session['usuario_logado'] is None:
        print(f"url_for('novaTela'): {url_for('novaTela')}")
        return redirect(url_for('login', proxima=url_for('novaTela')))
    return render_template('novo.html', titulo='Novo jogo')

@app.route('/criar', methods=['POST'])
def adicionaJogo():
    nome = request.form['nome']
    categoria = request.form['categoria']
    console = request.form['console']
    listJogos.append(Jogo(nome, categoria, console))

    return redirect(url_for('lista'))

@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)

@app.route('/autenticar', methods=['POST'])
def auth():
    if request.form['usuario'] in dictUsuarios:
        userLog = Usuario(request.form['usuario'], request.form['usuario'], request.form['senha'])
        if userLog.senha == str(dictUsuarios[userLog.usuario].senha):
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

app.run('127.0.0.1', debug=True, port=2020)