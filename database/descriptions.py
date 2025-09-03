#  only static data + HTML templates
class Product:
    def __init__(self, name, price):
        self.name, self.price = name, price

class Feature:
    def __init__(self, title, description):
        self.title, self.description = title, description

products = [
    Product("30 дней", "299₽"),
    Product("Навсегда", "499₽"),
    Product("Сброс HWID", "249₽"),
]
products_beta = [
    Product("BETA 1.21.4 — 30 дней", "800₽"),
    Product("BETA 1.21.4 — Навсегда", "1199₽"),
]

general_features = [
    Feature("Обходы",  "Современные методы обхода античитов популярных серверов."),
    Feature("Визуалы", "TargetESP, Animations и десятки других визуальных модулей."),
    Feature("Поддержка", "Ответ за 2-10 минут и помощь с любыми ошибками."),
    Feature("Оптимизация", "Хороший FPS, потянет даже картошка.")
]

# ------------ LOGIN -------------
LOGIN_HTML = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Вход</title>
<style>
:root{--card:#26282e;--border:#474a52;--text:#f1f2f4;--muted:#9c9ea4}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,Arial,sans-serif;color:var(--text);
     min-height:100vh;display:flex;justify-content:center;align-items:center}
.box{width:340px;padding:46px;border:1px solid var(--border);border-radius:18px;
     background:var(--card);box-shadow:0 6px 18px #000a;text-align:center}
h1{margin-bottom:28px;font-size:2rem}
input,button{width:100%;padding:13px;margin:9px 0;border-radius:12px;font-size:1rem}
input{border:1px solid var(--border);background:#1d1f24;color:var(--text)}
button{border:none}
a{display:block;margin-top:16px;color:var(--muted);text-decoration:none;font-size:.95rem}
a:hover{color:var(--text)}
{{ bg_style|safe }}{{ btn_style|safe }}
</style></head><body>
<div class="box">
  <h1>Вход</h1>
  <form method="POST">
    <input name="username" placeholder="Логин" required>
    <input name="password" type="password" placeholder="Пароль" required>
    <button class="btn">Войти</button>
  </form>
  <a href="{{ url_for('register') }}">Нет аккаунта? Регистрация</a>
  <a href="{{ url_for('shop') }}">⬅ На главную</a>
</div></body></html>"""

# ------------ REGISTER -------------
REGISTER_HTML = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Регистрация</title>
<style>
:root{--card:#26282e;--border:#474a52;--text:#f1f2f4;--muted:#9c9ea4}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,Arial,sans-serif;color:var(--text);
     min-height:100vh;display:flex;justify-content:center;align-items:center}
.box{width:340px;padding:46px;border:1px solid var(--border);border-radius:18px;
     background:var(--card);box-shadow:0 6px 18px #000a;text-align:center}
h1{margin-bottom:28px;font-size:2rem}
input,button{width:100%;padding:13px;margin:9px 0;border-radius:12px;font-size:1rem}
input{border:1px solid var(--border);background:#1d1f24;color:var(--text)}
button{border:none}
a{display:block;margin-top:16px;color:var(--muted);text-decoration:none;font-size:.95rem}
a:hover{color:var(--text)}
{{ bg_style|safe }}{{ btn_style|safe }}
</style></head><body>
<div class="box">
  <h1>Регистрация</h1>
  <form method="POST">
    <input name="username" placeholder="Логин" required>
    <input name="password" type="password" placeholder="Пароль" required>
    <input name="email" type="email" placeholder="E-mail" required>
    <button class="btn">Создать аккаунт</button>
  </form>
  <a href="{{ url_for('login') }}">Уже есть аккаунт? Вход</a>
  <a href="{{ url_for('shop') }}">⬅ На главную</a>
</div>
</body></html>
"""

# ------------ PROFILE -------------
PROFILE_HTML = """
<!DOCTYPE html><html><head><meta charset="UTF-8"><title>Кабинет</title>
<style>
:root{--card:#26282e;--border:#474a52;--text:#f1f2f4;--muted:#9c9ea4}
*{box-sizing:border-box;margin:0;padding:0}
body{
  font-family:Inter,Arial,sans-serif;
  color:var(--text);
  min-height:100vh;
  background:#1a1c21;

  display:flex;
  justify-content:flex-start;
  align-items:flex-start;
  padding:190px 0 0 400px;
}
.container{display:flex;align-items:flex-start;gap:14px}
.avatar-card,.info-card{padding:36px 42px;border:1px solid var(--border);border-radius:20px;background:var(--card);box-shadow:0 6px 18px #000a}
.avatar-card{display:flex;flex-direction:column;align-items:center;min-width:200px}
.avatar-img{width:120px;height:120px;border-radius:50%;object-fit:cover;border:2px solid var(--border);background:#1d1f24;margin-bottom:14px;}
.upload-btn,.delete-btn{padding:10px 16px;border-radius:12px;border:none;background:#64666d;color:#fff;font-weight:600;cursor:pointer;margin-top:6px}
.info-card{min-width:400px}
h1{margin-bottom:28px;font-size:1.6rem;text-align:center}
.row{display:flex;align-items:center;margin-bottom:22px;gap:14px}
.label{min-width:140px;padding:10px;background:#1d1f24;border:1px solid var(--border);border-radius:12px;text-align:center;font-weight:600}
input{flex:1;padding:10px;border:1px solid var(--border);border-radius:12px;background:#1a1c21;color:var(--text)}
.btn-small{padding:10px 16px;border:none;border-radius:12px;font-weight:700;cursor:pointer}
.back{display:block;text-align:center;margin-top:28px;color:var(--muted);text-decoration:none;font-weight:600}
.back:hover{color:var(--text)}
#ov{display:none;position:fixed;inset:0;background:#0008;backdrop-filter:blur(3px);z-index:1000}
#mdl{display:none;position:fixed;left:50%;top:50%;transform:translate(-50%,-50%) scale(.9);background:var(--card);border:1px solid var(--border);border-radius:18px;padding:42px;width:420px;max-width:90vw;box-shadow:0 6px 18px #000a;transition:.3s;z-index:1001}
#mdl.show{transform:translate(-50%,-50%) scale(1)}
.close{position:absolute;top:12px;right:18px;font-size:24px;background:none;border:none;color:var(--muted);cursor:pointer}
.payment-btn{display:block;margin:14px 0;text-align:center}
{{ bg_style|safe }}{{ btn_style|safe }}
</style></head><body>
<div class="container">

  <!-- карточка с аватаркой -->
  <div class="avatar-card">
    <img class="avatar-img" src="{{ user.avatar_url if user.avatar_url else url_for('static', filename='icon.png') }}" alt="Аватар">
    <form method="POST" enctype="multipart/form-data" style="display:flex;flex-direction:column;align-items:center;gap:8px;">
      <input type="file" name="avatar" accept="image/*" style="display:none" id="avatarInput" onchange="this.form.submit()">
      <button type="button" class="upload-btn" onclick="document.getElementById('avatarInput').click()">Загрузить аватарку</button>
      {% if user.avatar_url %}
        <button type="submit" name="delete_avatar" class="delete-btn">Удалить аватарку</button>
      {% endif %}
    </form>
  </div>

  <!-- карточка с информацией -->
  <div class="info-card">
    <h1>Личный кабинет</h1>
    <div class="row"><span class="label">UID</span><input value="{{ user.uid }}" readonly></div>
    <div class="row"><span class="label">Логин</span><input value="{{ user.username }}" readonly></div>
    <div class="row"><span class="label">E-mail</span><input value="{{ user.email }}" readonly></div>
    <div class="row"><span class="label">Роль</span><input value="{{ user.role }}" readonly></div>
    <div class="row"><span class="label">HWID</span>
      <div style="flex:1;display:flex;gap:10px">
        <input value="{{ user.hwid or 'не привязан' }}" readonly>
        <button class="btn-small" onclick="openModal('Сброс HWID','250₽')">Сбросить</button>
      </div>
    </div>
    <div class="row"><span class="label">Клиент до</span>
      <input value="{{ user.subscription_end or '-' }}" readonly>
    </div>

    <!-- Актив. ключ -->
    <form method="POST" class="row">
      <span class="label">Актив. ключ</span>
      <div style="flex:1;display:flex;gap:10px">
        <input id="activation_key" 
               name="activation_key" 
               placeholder="XXXX XXXX XXXX XXXX" 
               required>
        <button type="submit" class="btn-small">Активировать</button>
      </div>
    </form>

    <a class="back" href="{{ url_for('shop') }}">⬅ На главную</a>
  </div>
</div>

<!-- модальное окно -->
<div id="ov" onclick="closeModal()"></div>
<div id="mdl">
  <button class="close" onclick="closeModal()">&times;</button>
  <h2 id="pn"></h2><p id="pp" style="margin-bottom:26px"></p>
  <h3 style="margin:0 0 18px;font-size:1.1rem">Выбери способ оплаты</h3>
  <a class="payment-btn" href="https://funpay.com/lots/1099/trade" target="_blank">💳 FunPay (РФ)</a>
  <a class="payment-btn" href="https://discord.gg/bBCAAURNEY" target="_blank">💸 Украинская карта</a>
</div>
<script>
const ov=document.getElementById('ov'),mdl=document.getElementById('mdl'),pn=document.getElementById('pn'),pp=document.getElementById('pp');
function openModal(n,p){pn.textContent=n;pp.textContent='Цена: '+p;ov.style.display='block';mdl.style.display='block';setTimeout(()=>mdl.classList.add('show'),10);}
function closeModal(){ov.style.display='none';mdl.classList.remove('show');setTimeout(()=>mdl.style.display='none',200);}
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeModal()});
</script>
</body></html>"""