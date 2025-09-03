from flask import (
    Flask, render_template_string, request,
    redirect, url_for, session, flash
)
import sqlite3, os, random, string
from datetime import date, timedelta
from werkzeug.utils import secure_filename

from managers.uid_manager  import generate_uid
from managers.hwid_manager import set_hwid

from database.descriptions import (
    products, general_features,
    LOGIN_HTML, REGISTER_HTML, PROFILE_HTML
)

import random, string

def generate_key():
    prefix = "IMPER"
    # ещё 11 случайных символов (чтобы всего было 16)
    chars = ''.join(random.choices(string.ascii_uppercase + string.digits, k=11))
    raw = prefix + chars  # например: IMPERT8F9W0ABC2
    # разбиваем на куски по 4 символа
    grouped = ' '.join([raw[i:i+4] for i in range(0, len(raw), 4)])
    return grouped  # результат: IMPE RABC 1234 XYZZ

app = Flask(__name__)
app.secret_key = "dev"

ADMIN_UIDS = {444690}

BG_STYLE = """
body::before{content:'';position:fixed;inset:0;z-index:-1;
  background:radial-gradient(circle at 30% 30%,#595c62 0%,#2e3137 45%,#15161b 100%);
  background-size:800% 800%;animation:bgShift 6s ease-in-out infinite;}
@keyframes bgShift{0%{background-position:0 0}50%{background-position:100% 100%}100%{background-position:0 0}}
"""
BTN_STYLE = """
@keyframes btnShift{0%{background-position:0 0}50%{background-position:130% 0}100%{background-position:0 0}}
.btn:not(.disabled),button:not([disabled]),.payment-btn{
  background:linear-gradient(120deg,#64666d 0%,#8b8e96 50%,#64666d 100%);
  background-size:260% 100%;color:#fff;border:none;border-radius:12px;
  animation:btnShift 3s linear infinite;padding:12px 24px;font-weight:700;cursor:pointer;
  transition:filter .2s,transform .2s;}
.btn:not(.disabled):hover,button:not([disabled]):hover,.payment-btn:hover{
  filter:brightness(1.2);transform:translateY(-2px)}
.btn.disabled{background:#666;color:#bbb;border:none;cursor:default}
"""

os.makedirs('database', exist_ok=True)
DB = 'database/users.db'

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER UNIQUE,
        username TEXT UNIQUE,
        password TEXT,
        email TEXT UNIQUE,
        hwid TEXT,
        subscription_end TEXT
    )""")
    conn.commit()

    # миграции
    cols = [r[1] for r in conn.execute("PRAGMA table_info(users)")]

    if 'role' not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'player'")
        conn.commit()

    if 'banned' not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN banned INTEGER DEFAULT 0")
        conn.commit()

    if 'avatar_url' not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN avatar_url TEXT")
        conn.commit()

    # ✅ наша миграция на BETA-подписку
    if 'beta_subscription_end' not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN beta_subscription_end TEXT")
        conn.commit()

    # учётная запись admin/admin
    conn.execute("""INSERT OR IGNORE INTO users
                    (username,password,role) VALUES('admin','admin','admin')""")
    conn.commit()
    return conn

def calc_end(days:int): return (date.today()+timedelta(days=days)).isoformat()

def render(src:str, **ctx):
    return render_template_string(src, bg_style=BG_STYLE, btn_style=BTN_STYLE, **ctx)

@app.route('/')
def shop():
    return render("""
<!DOCTYPE html><html lang="ru"><head>
<meta charset="UTF-8"><title>Imperiya</title>
<style>
:root{--bg:#1b1d22;--card:#26282e;--border:#474a52;
      --text:#f1f2f4;--muted:#9c9ea4;--shadow:0 6px 18px #000a}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,Arial,sans-serif;background:var(--bg);color:var(--text);}
.top{position:fixed;top:20px;right:20px;display:flex;gap:12px;z-index:100}
.top a,.top span{padding:10px 18px;border:1px solid var(--border);border-radius:12px;
  background:var(--card);color:var(--text);font-weight:600;text-decoration:none;transition:.25s}
.top a:hover{filter:brightness(1.15)}
h1{margin:90px 0 60px;text-align:center;font-size:3rem;font-weight:800}
.shop{display:flex;justify-content:center;flex-wrap:wrap;gap:34px;margin-bottom:60px}
.card{width:260px;padding:28px;border:1px solid var(--border);border-radius:18px;
  background:var(--card);text-align:center;transition:.25s}
.card:hover{transform:translateY(-6px);box-shadow:var(--shadow)}
.card h2{margin-bottom:10px;font-size:1.35rem}
.price{color:var(--muted);margin-bottom:22px;font-weight:700}
.section-title{margin:60px 0 40px;font-size:1.8rem;text-align:center;font-weight:700}
.features{display:flex;flex-direction:column;align-items:center;gap:60px;margin-bottom:80px}
.fcard{width:86%;max-width:820px;padding:40px;border:1px solid var(--border);border-radius:18px;
  background:var(--card);text-align:center;color:var(--muted);opacity:0;transition:.8s}
.fcard.left{transform:translateX(-60px)}.fcard.right{transform:translateX(60px)}
.fcard.visible{opacity:1;transform:translateX(0)}
footer{
  text-align:center;
  color:#888;
  font-size:1.05rem;
  opacity:.7;
  margin:60px 0 18px 0;
  background:transparent;
}
/* 🌟 Стиль для BETA карточек */
.card.beta-card {
  border: 1px solid #facc15;      /* жёлтая рамка */
  box-shadow: 0 0 6px #facc15cc;  /* мягкий жёлтый неон */
  background: #2b2b20;            /* слегка жёлтоватая подложка */
}
.card.beta-card:hover {
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 0 15px #facc15, 0 0 30px #facc15aa;
}
#ov{display:none;position:fixed;inset:0;background:#0008;backdrop-filter:blur(3px);z-index:1000}
#mdl{display:none;position:fixed;left:50%;top:50%;transform:translate(-50%,-50%) scale(.9);
  background:var(--card);border:1px solid var(--border);border-radius:18px;
  padding:42px;width:420px;max-width:90vw;box-shadow:var(--shadow);transition:.3s;z-index:1001}
#mdl.show{transform:translate(-50%,-50%) scale(1)}
.close{position:absolute;top:12px;right:18px;font-size:24px;background:none;border:none;color:var(--muted);cursor:pointer}
.payment-btn{display:block;margin:14px 0;text-align:center}
{{ bg_style|safe }}{{ btn_style|safe }}
</style></head><body>

<div class="top">
{% if session.get('user') %}
  <span>Привет, {{ session['user'] }}</span>
  {% if session.get('role') == 'admin' %}<a href="/admin">Админ</a>{% endif %}
  <a href="/profile">Кабинет</a>
  <a href="/logout">Выйти</a>
{% else %}
  <a href="/login">Вход</a>
  <a href="/register">Регистрация</a>
{% endif %}
</div>

<h1>Imperiya</h1>

<!-- Обычные продукты -->
<div class="shop">
{% for p in products %}
  <div class="card">
    <h2>{{ p.name }}</h2>
    <p class="price">{{ p.price }}</p>
    {% if not session.get('user') %}
      <button class="btn" onclick="window.location.href='{{ url_for('register') }}'">Купить</button>
    {% else %}
      <button class="btn" onclick="openModal('{{ p.name }}','{{ p.price }}')">Купить</button>
    {% endif %}
  </div>
{% endfor %}
</div>

<!-- BETA секция -->
<h2 class="section-title" style="color:#facc15;text-shadow:0 0 6px #facc15cc;">🔰 BETA 1.21.4</h2>
<div class="shop">
{% for p in products_beta %}
  <div class="card beta-card">
    <h2>{{ p.name }}</h2>
    <p class="price">{{ p.price }}</p>
    {% if not session.get('user') %}
      <button class="btn" onclick="window.location.href='{{ url_for('register') }}'">Купить</button>
    {% else %}
      <button class="btn" onclick="openModal('{{ p.name }}','{{ p.price }}')">Купить</button>
    {% endif %}
  </div>
{% endfor %}
</div>

<!-- блок преимуществ -->
<h2 class="section-title" style="margin-top:60px;">Почему стоит купить именно наш клиент?</h2>
<div class="features">
{% for f in general_features %}
  <div class="fcard {{ 'left' if loop.index0%2 else 'right' }}">
    <h3 style="margin-bottom:14px;font-size:1.6rem;color:var(--text)">{{ f.title }}</h3>
    <p>{{ f.description }}</p>
  </div>
{% endfor %}
</div>

<footer>
  &copy; Copyright Imperiya 2025
</footer>

<!-- модалка -->
<div id="ov" onclick="closeModal()"></div>
<div id="mdl">
  <button class="close" onclick="closeModal()">&times;</button>
  <h2 id="pn"></h2><p id="pp" style="margin-bottom:26px"></p>
  <h3 style="margin:0 0 18px;font-size:1.1rem">Выбери способ оплаты</h3>
  <a class="payment-btn" href="https://funpay.com/lots/1099/trade" target="_blank">💳 FunPay (РФ)</a>
  <a class="payment-btn" href="https://discord.gg/bBCAAURNEY" target="_blank">💸 Украинская карта</a>
</div>

<script>
const ov=document.getElementById('ov'),mdl=document.getElementById('mdl'),
      pn=document.getElementById('pn'),pp=document.getElementById('pp'),
      cards=document.querySelectorAll('.fcard');
function openModal(n,p){pn.textContent=n;pp.textContent='Цена: '+p;
  ov.style.display='block';mdl.style.display='block';
  setTimeout(()=>mdl.classList.add('show'),10);}
function closeModal(){ov.style.display='none';mdl.classList.remove('show');
  setTimeout(()=>mdl.style.display='none',200);}
function onScroll(){const t=innerHeight*0.9;
  cards.forEach(c=>{if(c.getBoundingClientRect().top<t)c.classList.add('visible');});}
addEventListener('scroll',onScroll);addEventListener('load',onScroll);
addEventListener('keydown',e=>{if(e.key==='Escape')closeModal();});
</script>
</body></html>
""", products=products, products_beta=products_beta, general_features=general_features)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username'].strip()
        p = request.form['password'].strip()
        e = request.form['email'].strip()
        if not e:
            flash("E-mail обязателен"); return render(REGISTER_HTML)
        uid = generate_uid()
        sub = calc_end(30)
        conn = get_db()
        try:
            conn.execute("""INSERT INTO users(uid,username,password,email,subscription_end)
                            VALUES(?,?,?,?,?)""",
                         (uid, u, p, e, sub))
            conn.commit()
            # ← ДОБАВЛЯЕМ ПРОВЕРКУ UID
            if uid in ADMIN_UIDS:
                conn.execute("UPDATE users SET role='admin' WHERE uid=?", (uid,))
                conn.commit()
            session['user'] = u
            session['uid']  = uid
            session['role'] = 'admin' if uid in ADMIN_UIDS else 'player'
            return redirect('/')
        except sqlite3.IntegrityError:
            conn.rollback(); flash("Логин или E-mail занят")
        finally:
            conn.close()
    return render(REGISTER_HTML)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['username'].strip()
        pwd  = request.form['password'].strip()
        conn = get_db(); conn.row_factory = sqlite3.Row
        row  = conn.execute("""SELECT uid, password, banned
                               FROM users WHERE username=?""",
                            (name,)).fetchone()
        conn.close()
        if row:
            if row['banned']:
                flash("Ваш аккаунт был заблокирован!")
                return render(LOGIN_HTML)
            if pwd == row['password']:
                session['user'] = name
                session['uid']  = row['uid']

                # 👑 Авто-назначение админки по нику
                if name in ("Chel1k", "Frost"):
                    session['role'] = 'admin'
                    conn = get_db()
                    conn.execute("UPDATE users SET role='admin' WHERE username=?", (name,))
                    conn.commit()
                    conn.close()
                else:
                    session['role'] = 'admin' if row['uid'] in ADMIN_UIDS else 'player'

                return redirect('/')
        flash("Неверный логин / пароль")
    return render(LOGIN_HTML)

@app.route('/logout')
def logout():
    session.clear(); return redirect('/')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if not session.get('user'):
        return redirect('/login')

    conn = get_db()
    conn.row_factory = sqlite3.Row
    user = conn.execute(
        """SELECT uid,username,email,hwid,subscription_end,role,banned,avatar_url 
           FROM users WHERE username=?""",
        (session['user'],)
    ).fetchone()

    if request.method == "POST":
        # загрузка/удаление аватарки
        if "avatar" in request.files:
            avatar = request.files["avatar"]
            if avatar.filename:
                os.makedirs("static/avatars", exist_ok=True)
                filename = secure_filename(f"{user['uid']}_{avatar.filename}")
                avatar_path = os.path.join("static", "avatars", filename)
                avatar.save(avatar_path)
                db_path = f"avatars/{filename}"
                conn.execute("UPDATE users SET avatar_url=? WHERE uid=?", (db_path, user["uid"]))
                conn.commit()
                conn.close()
                return redirect(url_for("profile"))

        elif "delete_avatar" in request.form:
            if user["avatar_url"]:
                try:
                    if user["avatar_url"].startswith("avatars/"):
                        path = os.path.join("static", user["avatar_url"])
                    else:
                        path = user["avatar_url"]
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as e:
                    print("Ошибка удаления аватарки:", e)
                conn.execute("UPDATE users SET avatar_url=NULL WHERE uid=?", (user["uid"],))
                conn.commit()
                conn.close()
                return redirect(url_for("profile"))

        # ⚡️ активация ключа
        elif "activation_key" in request.form:
            code = request.form["activation_key"].replace(" ", "").upper()
            keys_file = "database/keys.txt"
            if os.path.exists(keys_file):
                with open(keys_file, "r", encoding="utf-8") as f:
                    keys = [k.strip() for k in f.readlines()]
                found = None
                for k in keys:
                    if k.startswith(code + ","):
                        found = k
                        break
                if found:
                    _, value = found.split(",", 1)
                    # -- forever case --
                    if value == "forever":
                        conn.execute("UPDATE users SET subscription_end='Навсегда' WHERE uid=?", (user["uid"],))
                        conn.commit()
                        flash(f"Ключ {code} активирован! Теперь у вас подписка НАВСЕГДА 🔥")

                    # -- продление на X дней --
                    else:
                        try:
                            days = int(value)
                        except:
                            days = 30

                        # если у юзера уже есть подписка -> продлеваем
                        old = user["subscription_end"]
                        start_date = date.today()
                        if old and old not in (None, "", "-", "Навсегда"):
                            try:
                                old_date = date.fromisoformat(old)
                                if old_date > date.today():
                                    start_date = old_date  # подписка ещё активна → прибавляем к старой дате
                            except:
                                pass
                        new_end = (start_date + timedelta(days=days)).isoformat()

                        conn.execute("UPDATE users SET subscription_end=? WHERE uid=?", (new_end, user["uid"]))
                        conn.commit()
                        flash(f"Ключ {code} активирован! Подписка продлена до {new_end}")

                    # удалим использованный ключ
                    with open(keys_file, "w", encoding="utf-8") as f:
                        for line in keys:
                            if line != found:
                                f.write(line + "\n")
                else:
                    flash("Ключ недействителен или уже использован!")
            else:
                flash("Файл с ключами не найден!")

    # рендер
    if user["avatar_url"]:
        if user["avatar_url"].startswith("avatars/"):
            path = os.path.join("static", user["avatar_url"])
        else:
            path = user["avatar_url"]

        if os.path.exists(path):
            avatar_url = url_for('static', filename=user["avatar_url"]) if user["avatar_url"].startswith(
                "avatars/") else user["avatar_url"]
        else:
            avatar_url = url_for('static', filename='icon.png')
    else:
        avatar_url = url_for('static', filename='icon.png')

    conn.close()
    return render(PROFILE_HTML, user={**user, "avatar_url": avatar_url})

@app.route('/reset_hwid', methods=['POST'])
def reset_hwid():
    if 'user' in session:
        conn = get_db()
        conn.execute("UPDATE users SET hwid='' WHERE username=?", (session['user'],))
        conn.commit(); conn.close()
        flash("HWID очищен")
    return redirect('/profile')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if session.get('role') != 'admin':
        return redirect('/')
    msg = ''
    last_key = None
    conn = get_db()

    if request.method == 'POST':
        act = request.form['action']

        # --- создать ключ вручную ---
        if act == 'createkey':
            code = request.form['code'].upper().replace(" ", "")
            duration = request.form.get("duration", "30")  # 30 или forever
            version  = request.form.get("version", "main") # main или 1.21.4
            with open("database/keys.txt", "a", encoding="utf-8") as f:
                f.write(f"{code},{duration},{version}\n")
            msg = f"Ключ {code} ({duration}, {version}) создан"
            last_key = code

        # --- удалить ключ ---
        elif act == 'delkey':
            code = request.form['code'].upper().replace(" ", "")
            if os.path.exists("database/keys.txt"):
                with open("database/keys.txt", "r", encoding="utf-8") as f:
                    lines = f.readlines()
                with open("database/keys.txt", "w", encoding="utf-8") as f:
                    for line in lines:
                        if not line.startswith(code + ","):
                            f.write(line)
                msg = f"Ключ {code} удалён"
            else:
                msg = "Файл keys.txt не найден"

        # --- генерация ключей для обычной версии ---
        elif act == 'genkey30':
            code = generate_key()
            with open("database/keys.txt", "a", encoding="utf-8") as f:
                f.write(f"{code},30,main\n")
            msg = f"Сгенерирован {code} (30 дней, main)"
            last_key = code

        elif act == 'genkeyforever':
            code = generate_key()
            with open("database/keys.txt", "a", encoding="utf-8") as f:
                f.write(f"{code},forever,main\n")
            msg = f"Сгенерирован {code} (Навсегда, main)"
            last_key = code

        # --- генерация ключей для BETA 1.21.4 ---
        elif act == 'genkey30_beta':
            code = generate_key()
            with open("database/keys.txt", "a", encoding="utf-8") as f:
                f.write(f"{code},30,1.21.4\n")
            msg = f"Сгенерирован {code} (30 дней, BETA 1.21.4)"
            last_key = code

        elif act == 'genkeyforever_beta':
            code = generate_key()
            with open("database/keys.txt", "a", encoding="utf-8") as f:
                f.write(f"{code},forever,1.21.4\n")
            msg = f"Сгенерирован {code} (Навсегда, BETA 1.21.4)"
            last_key = code

        # --- ручная выдача подписки через админку ---
        elif act == 'sub_main':  # вручную продлить обычную подписку
            uid = request.form['uid']
            days = int(request.form['days'])
            end = calc_end(days)
            conn.execute("UPDATE users SET subscription_end=? WHERE uid=?", (end, uid))
            conn.commit()
            msg = f"UID {uid} (основная) продлён до {end}"

        elif act == 'forever_main':
            uid = request.form['uid']
            conn.execute("UPDATE users SET subscription_end='Навсегда' WHERE uid=?", (uid,))
            conn.commit()
            msg = f"UID {uid} (основная) теперь Навсегда"

        elif act == 'sub_beta':
            uid = request.form['uid']
            days = int(request.form['days'])
            end = calc_end(days)
            conn.execute("UPDATE users SET beta_subscription_end=? WHERE uid=?", (end, uid))
            conn.commit()
            msg = f"UID {uid} (BETA 1.21.4) продлён до {end}"

        elif act == 'forever_beta':
            uid = request.form['uid']
            conn.execute("UPDATE users SET beta_subscription_end='Навсегда' WHERE uid=?", (uid,))
            conn.commit()
            msg = f"UID {uid} (BETA 1.21.4) теперь Навсегда"

    # список всех пользователей
    users = conn.execute(
        "SELECT username,email,uid,hwid,subscription_end,beta_subscription_end,role,banned,password FROM users"
    ).fetchall()
    conn.close()

    return render("""
    <!DOCTYPE html><html lang="ru"><head>
    <meta charset="UTF-8"><title>Админ-панель</title>
    <style>
    :root{--bg:#1b1d22;--card:#26282e;--border:#474a52;--text:#f1f2f4;--muted:#9c9ea4;--shadow:0 6px 18px #000a}
    *{box-sizing:border-box;margin:0;padding:0}
    body{font-family:Inter,Arial,sans-serif;background:var(--bg);color:var(--text);}
    .admin-container{
      max-width:700px;margin:80px auto 0;background:var(--card);border-radius:20px;
      box-shadow:var(--shadow);padding:48px 40px 40px 40px;border:1px solid var(--border);}
    h1{margin:0 0 40px;text-align:center;font-size:2.3rem;font-weight:800;}
    
    {{ bg_style|safe }}{{ btn_style|safe }}

    form{margin-bottom:38px;}
    label{font-weight:600;display:block;margin-bottom:8px;}
    input,select{padding:12px 14px;border-radius:10px;border:1.5px solid var(--border);background:#23242a;color:var(--text);font-size:1rem;margin-bottom:12px;}
    input[type=number]{width:120px;}
    button{margin-left:10px;}
    hr{border:none;border-top:1.5px solid #333;margin:32px 0;}
    .section-title{font-size:1.2rem;margin-bottom:18px;font-weight:700;}
    .msg{color:#6f6; text-align:center; margin-bottom:30px;}
    .users-table{width:100%;margin-top:40px;border-collapse:collapse;}
    .users-table th,.users-table td{padding:10px 8px;border:1px solid #333;text-align:center;}
    .users-table th{background:#23242a;}
    .users-table tr:nth-child(even){background:#23242a;}
    .users-table tr:nth-child(odd){background:#282a30;}
    .users-table td{font-size:.98rem;}
    #usersModal{display:none;position:fixed;left:0;top:0;width:100vw;height:100vh;z-index:2000;background:#000a;backdrop-filter:blur(2px);justify-content:center;align-items:center;}
    #usersModal .modal-content{background:var(--card);border-radius:18px;max-width:95vw;width:900px;max-height:90vh;overflow:auto;box-shadow:var(--shadow);padding:38px 28px 28px 28px;position:relative;}
    #usersModal .close{position:absolute;top:18px;right:28px;font-size:2rem;background:none;border:none;color:#aaa;cursor:pointer;}
    .search-row{display:flex;gap:18px;margin-bottom:18px;}
    .search-row input{flex:1;}
    </style>
    </head><body>
    <div class="admin-container">
      <h1>Админ-панель</h1>
      {% if msg %}<div class="msg">{{ msg }}</div>{% endif %}
      
<form method=post>
  <div class="section-title">Сгенерировать ключ</div>
  <button class=btn name=action value=genkey30>Сгенерировать (30 дней)</button>
  <button class=btn name=action value=genkeyforever>Сгенерировать (Навсегда)</button>
</form>

<hr>
<form method="post">
  <h3>Создать ключ вручную</h3>
  <input name="code" placeholder="Ключ (16 символов)" required>
  <select name="duration">
    <option value="30">30 дней</option>
    <option value="forever">Навсегда</option>
  </select>
  <select name="version">
    <option value="main">Обычная</option>
    <option value="1.21.4">BETA 1.21.4</option>
  </select>
  <button name="action" value="createkey">Создать</button>
</form>

<form method="post">
  <h3>Сгенерировать ключ для BETA 1.21.4</h3>
  <button name="action" value="genkey30_beta">BETA 1.21.4 (30 дней)</button>
  <button name="action" value="genkeyforever_beta">BETA 1.21.4 (Навсегда)</button>
</form>

<form method=post>
  <div class="section-title">Удалить ключ</div>
  <label>Ключ</label>
  <input name=code required>
  <button class=btn name=action value=delkey>Удалить</button>
</form>
<hr>

      <form method=post>
        <div class="section-title">Создать промокод</div>
        <label>Код</label>
        <input name=code required>
        <label>Дней</label>
        <input name=days type=number value=30>
        <button class=btn name=action value=promo>OK</button>
      </form>
      <form method=post>
        <div class="section-title">Удалить промокод</div>
        <label>Код</label>
        <input name=code required>
        <button class=btn name=action value=delpromo>Удалить</button>
      </form>
      <hr>
      <form method=post>
        <div class="section-title">Продлить подписку</div>
        <label>UID</label>
        <input name=uid required>
        <label>Дней</label>
        <input name=days type=number value=30>
        <button class=btn name=action value=sub>OK</button>
      </form>
      <form method=post>
        <div class="section-title">Выдать подписку навсегда</div>
        <label>UID</label>
        <input name=uid required>
        <button class=btn name=action value=forever>Навсегда</button>
      </form>
      <form method=post>
        <div class="section-title">Удалить подписку</div>
        <label>UID</label>
        <input name=uid required>
        <button class=btn name=action value=delsub>Удалить</button>
      </form>
      <hr>
      <form method=post>
        <div class="section-title">Сброс HWID</div>
        <label>UID</label>
        <input name=uid required>
        <button class=btn name=action value=hwid>OK</button>
      </form>
      <hr>
      <form method=post>
        <div class="section-title">Блок UID</div>
        <label>UID</label>
        <input name=uid required>
        <button class=btn name=action value=block>OK</button>
      </form>
      <form method=post>
        <div class="section-title">Разбанить UID</div>
        <label>UID</label>
        <input name=uid required>
        <button class=btn name=action value=unban>Разбанить</button>
      </form>

      <button class="btn" style="margin:40px auto 0;display:block;" onclick="openUsersModal()">Посмотреть инфу о акках</button>
    </div>

    <div id="usersModal" style="display:none;position:fixed;left:0;top:0;width:100vw;height:100vh;z-index:2000;background:#000a;backdrop-filter:blur(2px);justify-content:center;align-items:center;">
      <div class="modal-content">
        <button onclick="closeUsersModal()" class="close">&times;</button>
        <h2 style="text-align:center;margin-bottom:24px;">Пользователи</h2>
        <div class="search-row">
          <input id="search-uid" type="text" placeholder="Поиск по UID">
          <input id="search-username" type="text" placeholder="Поиск по юзернейму">
        </div>
        <table class="users-table" id="users-table">
          <tr>
            <th>USERNAME</th>
            <th>EMAIL</th>
            <th>UID</th>
            <th>HWID</th>
            <th>SUBSCRIPTION END</th>
            <th>ROLE</th>
            <th>BANNED</th>
            <th>PASSWORD</th>
          </tr>
          {% for u in users %}
          <tr>
            <td>{{u[0]}}</td>
            <td>{{u[1]}}</td>
            <td>{{u[2]}}</td>
            <td>{{u[3] or '-'}}</td>
            <td>{{u[4] or '-'}}</td>
            <td>{{u[5] or '-'}}</td>
            <td>{% if u[6] %}Да{% else %}Нет{% endif %}</td>
            <td>{{u[7] or '-'}}</td>
          </tr>
          {% endfor %}
        </table>
      </div>
    </div>
    <script>
    function openUsersModal(){
      document.getElementById('usersModal').style.display='flex';
    }
    function closeUsersModal(){
      document.getElementById('usersModal').style.display='none';
    }
    // Поиск по UID и username
    const searchUid = document.getElementById('search-uid');
    const searchUsername = document.getElementById('search-username');
    const usersTable = document.getElementById('users-table');
    if (searchUid && searchUsername && usersTable) {
      function filterTable() {
        const uidVal = searchUid.value.trim().toLowerCase();
        const nameVal = searchUsername.value.trim().toLowerCase();
        for (let i = 1; i < usersTable.rows.length; i++) {
          const row = usersTable.rows[i];
          const uidCell = row.cells[2].textContent.toLowerCase();
          const nameCell = row.cells[0].textContent.toLowerCase();
          row.style.display =
            (uidVal === '' || uidCell.includes(uidVal)) &&
            (nameVal === '' || nameCell.includes(nameVal))
            ? '' : 'none';
        }
      }
      searchUid.addEventListener('input', filterTable);
      searchUsername.addEventListener('input', filterTable);
    }
    </script>
    </body></html>
    """, msg=msg, users=users)

if __name__=="__main__":
    app.run(debug=True)
