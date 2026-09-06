from flask import Flask, request, redirect, url_for, session, render_template_string, flash
import sqlite3, secrets, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
DB = "gyan_jyoti.db"

SCHOOL = "Gyan Jyoti International School"
ADDRESS = "Turkpattti, Kushinagar, Uttar Pradesh"
DIRECTOR = "Mr. Jata Shankar Gupta"

def getdb():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = getdb()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, roll TEXT, class_name TEXT, section TEXT,
        parent TEXT, phone TEXT, attendance INTEGER DEFAULT 90
    );

    CREATE TABLE IF NOT EXISTS teachers(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, subject TEXT, class_name TEXT, qualification TEXT
    );

    CREATE TABLE IF NOT EXISTS fees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER, fee_type TEXT, amount INTEGER,
        status TEXT DEFAULT 'DUE', paid_date TEXT, receipt TEXT
    );

    CREATE TABLE IF NOT EXISTS notices(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, body TEXT, date TEXT
    );

    CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER, day TEXT, status TEXT
    );
    """)

    if con.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
        con.executemany("""
        INSERT INTO students
        (name,roll,class_name,section,parent,phone,attendance)
        VALUES(?,?,?,?,?,?,?)
        """, [
            ("Aarav Kumar","GJ001","Class 10","A","Raj Kumar","9876543210",94),
            ("Ananya Singh","GJ002","Class 10","A","Vijay Singh","9876543211",91),
            ("Aditya Gupta","GJ003","Class 10","A","Sanjay Gupta","9876543212",96),
            ("Riya Verma","GJ004","Class 10","A","Amit Verma","9876543213",89),
            ("Rahul Singh","GJ005","Class 10","A","Manoj Singh","9876543214",93)
        ])

        con.executemany("""
        INSERT INTO teachers(name,subject,class_name,qualification)
        VALUES(?,?,?,?)
        """, [
            ("Mrs. Priya Sharma","Mathematics","Class 10","M.Sc, B.Ed"),
            ("Mr. Rahul Verma","Science","Class 8","M.Sc, B.Ed"),
            ("Mrs. Neha Singh","English","Class 6","M.A, B.Ed"),
            ("Mr. Amit Kumar","Computer","Class 9","MCA"),
            ("Mrs. Pooja Gupta","Hindi","Class 10","M.A, B.Ed")
        ])

        con.executemany("""
        INSERT INTO fees(student_id,fee_type,amount)
        VALUES(?,?,?)
        """, [
            (1,"Tuition Fee",4500),
            (1,"Transport Fee",1200),
            (1,"Annual Fee",2500),
            (2,"Tuition Fee",4500),
            (2,"Transport Fee",1200),
            (3,"Tuition Fee",4500),
            (4,"Tuition Fee",4500),
            (5,"Tuition Fee",4500)
        ])

        con.executemany("""
        INSERT INTO notices(title,body,date) VALUES(?,?,?)
        """, [
            ("Welcome to New Academic Session",
             "Welcome to Gyan Jyoti International School.",
             "06 Sep 2026"),
            ("Parent-Teacher Meeting",
             "Parent-Teacher meeting information will be announced soon.",
             "05 Sep 2026"),
            ("Annual Cultural Programme",
             "Preparations for the annual cultural programme have started.",
             "03 Sep 2026")
        ])

    con.commit()
    con.close()

init_db()

CSS = r"""
<style>
:root{
 --blue:#123d7a;
 --blue2:#1261c9;
 --light:#f4f7fb;
 --text:#17233b;
 --green:#08a86b;
 --purple:#6840d8;
 --orange:#f58220;
}
*{box-sizing:border-box}
body{
 margin:0;
 font-family:Arial,Helvetica,sans-serif;
 background:var(--light);
 color:var(--text);
}
a{text-decoration:none}
.topbar{
 height:72px;
 background:#0c3a75;
 color:white;
 display:flex;
 align-items:center;
 justify-content:space-between;
 padding:0 5%;
 position:sticky;
 top:0;
 z-index:50;
 box-shadow:0 2px 10px #0003;
}
.brand{
 display:flex;
 align-items:center;
 gap:12px;
 font-weight:800;
 font-size:22px;
}
.brand-icon{font-size:34px}
.brand-text span{color:#4fd4ff}
.brand-small{
 display:block;
 font-size:12px;
 font-weight:500;
 opacity:.9;
 margin-top:2px;
}
.menu-btn{
 width:50px;
 height:44px;
 border:1px solid #ffffff55;
 border-radius:10px;
 background:#ffffff12;
 color:white;
 font-size:27px;
 cursor:pointer;
}
.drawer{
 position:fixed;
 right:-380px;
 top:0;
 width:370px;
 max-width:92%;
 height:100vh;
 background:white;
 z-index:100;
 box-shadow:-8px 0 30px #0004;
 transition:.3s;
 overflow:auto;
}
.drawer.open{right:0}
.drawer-head{
 background:#0c3a75;
 color:white;
 padding:20px;
 display:flex;
 justify-content:space-between;
 align-items:center;
}
.close{
 background:none;
 border:0;
 color:white;
 font-size:28px;
 cursor:pointer;
}
.drawer a{
 display:flex;
 align-items:center;
 justify-content:space-between;
 color:#17233b;
 padding:17px 22px;
 border-bottom:1px solid #edf0f5;
 font-size:15px;
}
.drawer a:hover{background:#f2f7ff;color:#1261c9}
.drawer-section{
 padding:13px 22px 7px;
 font-size:12px;
 color:#7a8496;
 font-weight:bold;
 text-transform:uppercase;
}
.overlay{
 display:none;
 position:fixed;
 inset:0;
 background:#0007;
 z-index:90;
}
.overlay.show{display:block}

.hero{
 min-height:475px;
 color:white;
 position:relative;
 overflow:hidden;
 background:
 linear-gradient(120deg,#08366fdd,#1261c9dd),
 linear-gradient(45deg,#0b477f,#2787c9);
}
.hero:after{
 content:"";
 position:absolute;
 width:500px;
 height:500px;
 right:-180px;
 top:-180px;
 border-radius:50%;
 background:#ffffff12;
}
.hero-inner{
 max-width:1200px;
 margin:auto;
 padding:65px 5% 35px;
 position:relative;
 z-index:2;
}
.hero h1{
 font-size:52px;
 line-height:1.05;
 max-width:600px;
 margin:0 0 18px;
}
.hero p{
 max-width:650px;
 font-size:19px;
 line-height:1.6;
}
.hero-sub{
 opacity:.9;
}
.hero-cards{
 display:grid;
 grid-template-columns:repeat(4,1fr);
 gap:14px;
 margin-top:40px;
}
.quick{
 color:white;
 padding:20px;
 border-radius:14px;
 min-height:112px;
 box-shadow:0 8px 20px #0002;
 transition:.2s;
}
.quick:hover{transform:translateY(-3px)}
.quick.green{background:#08a86b}
.quick.blue{background:#126bd5}
.quick.purple{background:#6840d8}
.quick.orange{background:#f58220}
.quick-icon{font-size:27px}
.quick h3{margin:8px 0 4px}
.quick p{font-size:12px;margin:0;line-height:1.4}

.container{
 max-width:1200px;
 margin:0 auto;
 padding:35px 20px;
}
.section-title{
 display:flex;
 align-items:center;
 justify-content:space-between;
 margin-bottom:20px;
}
.section-title h2{margin:0;font-size:30px}
.cards{
 display:grid;
 grid-template-columns:repeat(auto-fit,minmax(220px,1fr));
 gap:18px;
}
.card{
 background:white;
 border-radius:15px;
 padding:22px;
 box-shadow:0 5px 22px #0000000d;
 margin-bottom:18px;
}
.stat{
 min-height:125px;
}
.stat-icon{font-size:28px}
.number{
 font-size:32px;
 font-weight:800;
 color:var(--blue2);
 margin:7px 0;
}
.grid2{
 display:grid;
 grid-template-columns:repeat(2,1fr);
 gap:20px;
}
table{
 width:100%;
 border-collapse:collapse;
 background:white;
 border-radius:12px;
 overflow:hidden;
}
th,td{
 padding:13px;
 border-bottom:1px solid #e7ebf2;
 text-align:left;
 font-size:14px;
}
th{background:#edf4fd}
.badge{
 display:inline-block;
 padding:6px 10px;
 border-radius:20px;
 background:#fff0d4;
 color:#9b6300;
 font-size:12px;
 font-weight:bold;
}
.badge.paid{background:#dff8eb;color:#087447}
.btn{
 display:inline-block;
 border:0;
 border-radius:8px;
 padding:11px 17px;
 color:white;
 background:var(--blue2);
 font-weight:bold;
 cursor:pointer;
}
.btn.green{background:var(--green)}
.btn.orange{background:var(--orange)}
.btn.purple{background:var(--purple)}
.btn.dark{background:#17233b}
input,select{
 width:100%;
 padding:12px;
 border:1px solid #d6dfea;
 border-radius:8px;
 margin:6px 0 14px;
 background:white;
}
label{font-size:13px;font-weight:bold}
.login-wrap{
 max-width:470px;
 margin:50px auto;
}
.login-logo{text-align:center;font-size:45px}
.login-title{text-align:center}
.role-title{
 font-size:14px;
 padding:8px 12px;
 border-radius:20px;
 display:inline-block;
 color:white;
}
.role-green{background:#08a86b}
.role-blue{background:#1261c9}
.role-purple{background:#6840d8}
.role-orange{background:#f58220}
.attbar{
 height:17px;
 background:#e6ebf2;
 border-radius:20px;
 overflow:hidden;
}
.attfill{
 height:100%;
 background:#08a86b;
 border-radius:20px;
}
.notice{
 border-left:4px solid var(--blue2);
}
.footer{
 background:#0c315f;
 color:white;
 padding:38px 6%;
 margin-top:30px;
}
.footer-grid{
 display:grid;
 grid-template-columns:2fr 1fr 1fr;
 gap:30px;
 max-width:1200px;
 margin:auto;
}
.footer p{opacity:.85;line-height:1.6}
.receipt{
 border:2px solid #dce4ef;
}
.success{
 color:#087447;
 font-weight:800;
 font-size:20px;
}
.small{font-size:12px;color:#68758a}
.mobile-only{display:none}

@media(max-width:900px){
 .hero-cards{grid-template-columns:repeat(2,1fr)}
 .grid2{grid-template-columns:1fr}
 .footer-grid{grid-template-columns:1fr}
}
@media(max-width:650px){
 .topbar{height:64px;padding:0 15px}
 .brand{font-size:16px}
 .brand-icon{font-size:27px}
 .brand-small{font-size:9px}
 .menu-btn{width:44px;height:40px}
 .hero-inner{padding:48px 22px 30px}
 .hero h1{font-size:39px}
 .hero p{font-size:16px}
 .hero-cards{grid-template-columns:1fr 1fr;gap:9px;margin-top:25px}
 .quick{padding:13px;min-height:105px}
 .quick h3{font-size:14px}
 .quick p{font-size:10px}
 .container{padding:25px 14px}
 table{display:block;overflow-x:auto;white-space:nowrap}
 .section-title h2{font-size:24px}
}
</style>
"""

BASE = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{title}} | Gyan Jyoti International School</title>
""" + CSS + r"""
</head>
<body>

<header class="topbar">
 <a href="/" style="color:white">
  <div class="brand">
   <div class="brand-icon">🎓</div>
   <div class="brand-text">
    Gyan Jyoti <span>International School</span>
    <span class="brand-small">Turkpattti, Kushinagar, Uttar Pradesh</span>
   </div>
  </div>
 </a>
 <button class="menu-btn" onclick="openMenu()">☰</button>
</header>

<div id="overlay" class="overlay" onclick="closeMenu()"></div>

<aside id="drawer" class="drawer">
 <div class="drawer-head">
  <div>
   <b>🎓 Gyan Jyoti</b><br>
   <span style="color:#4fd4ff">International School</span>
  </div>
  <button class="close" onclick="closeMenu()">×</button>
 </div>

 <div class="drawer-section">School</div>
 <a href="/">🏠 Home <span>›</span></a>
 <a href="/about">🏫 About School <span>›</span></a>
 <a href="/teachers">👨‍🏫 Teachers <span>›</span></a>
 <a href="/notices">💬 Notices <span>›</span></a>
 <a href="/gallery">🖼️ Gallery <span>›</span></a>
 <a href="/contact">📞 Contact <span>›</span></a>

 <div class="drawer-section">Portals</div>
 <a href="/login/parent">👨‍👩‍👦 Parent Portal <span>›</span></a>
 <a href="/login/teacher">👨‍🏫 Teacher Login <span>›</span></a>
 <a href="/login/class_teacher">🛡️ Class Teacher Login <span>›</span></a>
 <a href="/login/admin">⚙️ Admin Login <span>›</span></a>
</aside>

{% with messages=get_flashed_messages() %}
{% if messages %}
<div class="container">
 {% for m in messages %}
 <div class="card">{{m}}</div>
 {% endfor %}
</div>
{% endif %}
{% endwith %}

{{content|safe}}

<footer class="footer">
 <div class="footer-grid">
  <div>
   <h2>🎓 Gyan Jyoti International School</h2>
   <p>Learning today. Leading tomorrow.</p>
   <p>Turkpattti, Kushinagar, Uttar Pradesh</p>
  </div>
  <div>
   <h3>School</h3>
   <p>About School<br>Teachers<br>Notices<br>Gallery</p>
  </div>
  <div>
   <h3>Director</h3>
   <p>{{director}}</p>
   <p>© 2026 Demo Website</p>
  </div>
 </div>
</footer>

<script>
function openMenu(){
 document.getElementById('drawer').classList.add('open');
 document.getElementById('overlay').classList.add('show');
}
function closeMenu(){
 document.getElementById('drawer').classList.remove('open');
 document.getElementById('overlay').classList.remove('show');
}
</script>
</body>
</html>
"""

def page(title, content):
    return render_template_string(
        BASE,
        title=title,
        content=content,
        director=DIRECTOR
    )

@app.route("/")
def home():
    con=getdb()
    students=con.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    teachers=con.execute("SELECT COUNT(*) FROM teachers").fetchone()[0]
    notices=con.execute("SELECT * FROM notices ORDER BY id DESC LIMIT 3").fetchall()
    con.close()

    content=render_template_string(r"""
<section class="hero">
 <div class="hero-inner">
  <h1>Gyan Jyoti International School</h1>
  <p class="hero-sub">
   Learning today. Leading tomorrow. A professional school management
   and parent information portal.
  </p>

  <div class="hero-cards">
   <a class="quick green" href="/login/parent">
    <div class="quick-icon">👨‍👩‍👦</div>
    <h3>Parent Portal</h3>
    <p>Check fees, attendance and child information.</p>
   </a>

   <a class="quick blue" href="/login/teacher">
    <div class="quick-icon">👨‍🏫</div>
    <h3>Teacher Login</h3>
    <p>Manage classes, students and information.</p>
   </a>

   <a class="quick purple" href="/login/class_teacher">
    <div class="quick-icon">🛡️</div>
    <h3>Class Teacher Login</h3>
    <p>Mark attendance and manage class.</p>
   </a>

   <a class="quick orange" href="/login/admin">
    <div class="quick-icon">⚙️</div>
    <h3>Admin Login</h3>
    <p>Full school management access.</p>
   </a>
  </div>
 </div>
</section>

<div class="container">
 <div class="section-title">
  <h2>School at a Glance</h2>
 </div>

 <div class="cards">
  <div class="card stat">
   <div class="stat-icon">👨‍🎓</div>
   <div class="number">{{students}}</div>
   <b>Total Students</b>
  </div>
  <div class="card stat">
   <div class="stat-icon">👨‍🏫</div>
   <div class="number">{{teachers}}</div>
   <b>Teachers</b>
  </div>
  <div class="card stat">
   <div class="stat-icon">🏫</div>
   <div class="number">8</div>
   <b>Classes</b>
  </div>
  <div class="card stat">
   <div class="stat-icon">💳</div>
   <div class="number">24/7</div>
   <b>Parent Access</b>
  </div>
 </div>

 <div class="section-title">
  <h2>Latest Notices</h2>
  <a class="btn" href="/notices">View All</a>
 </div>

 {% for n in notices %}
 <div class="card notice">
  <h3>{{n.title}}</h3>
  <p>{{n.body}}</p>
  <span class="small">{{n.date}}</span>
 </div>
 {% endfor %}
</div>
""",students=students,teachers=teachers,notices=notices)

    return page("Home",content)

@app.route("/about")
def about():
    content=r"""
<div class="container">
 <div class="section-title"><h2>About Our School</h2></div>
 <div class="card">
  <h1>🎓 Gyan Jyoti International School</h1>
  <p>
   Gyan Jyoti International School is a modern educational institution
   focused on academic excellence, discipline, creativity and the
   all-round development of students.
  </p>
  <div class="grid2">
   <div>
    <h3>📍 School Address</h3>
    <p>Turkpattti, Kushinagar, Uttar Pradesh</p>
   </div>
   <div>
    <h3>👤 Director</h3>
    <p>Mr. Jata Shankar Gupta</p>
   </div>
  </div>
 </div>

 <div class="cards">
  <div class="card">
   <h2>🎯 Our Vision</h2>
   <p>To create confident, knowledgeable and responsible students.</p>
  </div>
  <div class="card">
   <h2>📚 Education</h2>
   <p>Quality learning with academic and co-curricular activities.</p>
  </div>
  <div class="card">
   <h2>🏆 Activities</h2>
   <p>Sports, cultural programmes, technology and creative learning.</p>
  </div>
 </div>
</div>
"""
    return page("About School",content)

@app.route("/teachers")
def teachers():
    con=getdb()
    rows=con.execute("SELECT * FROM teachers").fetchall()
    con.close()

    content=render_template_string(r"""
<div class="container">
 <div class="section-title"><h2>Our Teachers</h2></div>
 <div class="cards">
 {% for t in rows %}
  <div class="card">
   <div style="font-size:45px">👨‍🏫</div>
   <h2>{{t.name}}</h2>
   <p><b>Subject:</b> {{t.subject}}</p>
   <p><b>Class:</b> {{t.class_name}}</p>
   <p><b>Qualification:</b> {{t.qualification}}</p>
  </div>
 {% endfor %}
 </div>
</div>
""",rows=rows)

    return page("Teachers",content)

@app.route("/notices")
def notices():
    con=getdb()
    rows=con.execute("SELECT * FROM notices ORDER BY id DESC").fetchall()
    con.close()

    content=render_template_string(r"""
<div class="container">
 <div class="section-title"><h2>Notice Board</h2></div>
 {% for n in rows %}
 <div class="card notice">
  <h2>{{n.title}}</h2>
  <p>{{n.body}}</p>
  <span class="small">{{n.date}}</span>
 </div>
 {% endfor %}
</div>
""",rows=rows)

    return page("Notices",content)

@app.route("/gallery")
def gallery():
    content=r"""
<div class="container">
 <div class="section-title"><h2>School Gallery</h2></div>
 <div class="cards">
  <div class="card" style="height:190px;text-align:center;padding-top:55px;background:linear-gradient(135deg,#d9edff,#7fb9ee)">
   <div style="font-size:55px">🏫</div><b>School Campus</b>
  </div>
  <div class="card" style="height:190px;text-align:center;padding-top:55px;background:linear-gradient(135deg,#e4dcff,#aa91ee)">
   <div style="font-size:55px">📚</div><b>Classroom</b>
  </div>
  <div class="card" style="height:190px;text-align:center;padding-top:55px;background:linear-gradient(135deg,#d9ffe9,#7fe0ae)">
   <div style="font-size:55px">⚽</div><b>Sports Activity</b>
  </div>
  <div class="card" style="height:190px;text-align:center;padding-top:55px;background:linear-gradient(135deg,#fff0d9,#ffc47b)">
   <div style="font-size:55px">🎭</div><b>Cultural Programme</b>
  </div>
 </div>
</div>
"""
    return page("Gallery",content)

@app.route("/contact")
def contact():
    content=r"""
<div class="container">
 <div class="section-title"><h2>Contact School</h2></div>
 <div class="grid2">
  <div class="card">
   <h2>📍 Address</h2>
   <p>Turkpattti, Kushinagar, Uttar Pradesh</p>
   <h2>👤 Director</h2>
   <p>Mr. Jata Shankar Gupta</p>
  </div>
  <div class="card">
   <h2>📞 School Office</h2>
   <p>For demo purposes, contact details can be added here.</p>
   <a class="btn" href="/">Back to Home</a>
  </div>
 </div>
</div>
"""
    return page("Contact",content)

LOGIN_DATA={
 "parent":("Parent Portal","parent","parent123","green"),
 "teacher":("Teacher Login","teacher","teacher123","blue"),
 "class_teacher":("Class Teacher Login","ct","ct123","purple"),
 "admin":("Admin Login","admin","admin123","orange")
}

@app.route("/login/<role>",methods=["GET","POST"])
def login(role):
    if role not in LOGIN_DATA:
        return redirect("/")

    title,user,passwd,color=LOGIN_DATA[role]

    if request.method=="POST":
        if request.form.get("username")==user and request.form.get("password")==passwd:
            session["role"]=role
            return redirect(url_for("portal",role=role))
        flash("Incorrect username or password.")

    content=render_template_string(r"""
<div class="container">
 <div class="login-wrap">
  <div class="card">
   <div class="login-logo">
    {% if color=="green" %}👨‍👩‍👦{% elif color=="blue" %}👨‍🏫{% elif color=="purple" %}🛡️{% else %}⚙️{% endif %}
   </div>
   <h1 class="login-title">{{title}}</h1>
   <center><span class="role-title role-{{color}}">{{title}}</span></center>
   <form method="post" style="margin-top:25px">
    <label>Username</label>
    <input name="username" placeholder="Enter username" required>

    <label>Password</label>
    <input type="password" name="password" placeholder="Enter password" required>

    <button class="btn {{color}}" style="width:100%">
     Login
    </button>
   </form>

   <div class="card" style="background:#f5f8fc;margin-top:18px;margin-bottom:0">
    <b>Demo Login</b>
    <p style="margin-bottom:0">
     Username: <b>{{user}}</b><br>
     Password: <b>{{passwd}}</b>
    </p>
   </div>
  </div>
 </div>
</div>
""",title=title,user=user,passwd=passwd,color=color)

    return page(title,content)

@app.route("/portal/<role>")
def portal(role):
    if session.get("role")!=role:
        return redirect(url_for("login",role=role))

    if role=="parent":
        return parent_dashboard()
    if role=="teacher":
        return teacher_dashboard()
    if role=="class_teacher":
        return class_teacher_dashboard()
    return admin_dashboard()

@app.route("/dashboard")
def dashboard():
    role=session.get("role","parent")
    return redirect(url_for("portal",role=role))

def parent_dashboard():
    con=getdb()

    s=con.execute(
        "SELECT * FROM students WHERE id=1"
    ).fetchone()

    fees=con.execute(
        "SELECT * FROM fees WHERE student_id=1 ORDER BY id"
    ).fetchall()

    con.close()

    # Total pending and total paid
    due=sum(int(x["amount"]) for x in fees if x["status"]=="DUE")
    paid=sum(int(x["amount"]) for x in fees if x["status"]=="PAID")

    # First pending fee for payment page
    due_fee_id=next(
        (x["id"] for x in fees if x["status"]=="DUE"),
        None
    )

    content=render_template_string(r"""
<div class="container">

 <div class="section-title">
  <h2>Parent Dashboard</h2>
  <a class="btn dark" href="/logout">Logout</a>
 </div>

 <div class="card">
  <h2>👦 Welcome, Parent</h2>

  <p>
   <b>{{s.name}}</b> |
   {{s.class_name}} -
   Section {{s.section}} |
   Roll No. {{s.roll}}
  </p>

  <p>
   Parent: {{s.parent}} |
   Phone: {{s.phone}}
  </p>
 </div>


 <!-- DASHBOARD STATS -->

 <div class="cards">

  <!-- ATTENDANCE -->

  <div class="card stat">

   <div class="stat-icon"
        style="width:58px;height:58px;border-radius:50%;
        background:#7ac142;color:white;
        display:flex;align-items:center;
        justify-content:center;font-size:28px">
    ●
   </div>

   <div class="number">
    {{s.attendance}}%
   </div>

   <b style="font-size:18px">
    Attendance
   </b>

  </div>


  <!-- TOTAL PENDING FEE -->

  {% if due > 0 %}

  <a href="/pay/{{due_fee_id}}"
     class="card stat"
     style="
       display:block;
       color:inherit;
       cursor:pointer;
       position:relative;
       text-decoration:none;
     ">

   <div style="
        width:58px;
        height:58px;
        border-radius:50%;
        background:#f3264f;
        color:white;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:30px;
        font-weight:bold;">
    ₹
   </div>

   <div class="number">
    ₹{{due}}
   </div>

   <b style="font-size:18px">
    Total Fee Pending
   </b>

   <div style="
        font-size:14px;
        color:#68758a;
        margin-top:8px;">
    You have ₹{{due}} fee to be paid
   </div>

   <div style="margin-top:15px;">
    <span class="btn"
          style="background:#1261c9;">
     Pay Now →
    </span>
   </div>

  </a>

  {% else %}

  <div class="card stat">

   <div style="
        width:58px;
        height:58px;
        border-radius:50%;
        background:#7ac142;
        color:white;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:30px;">
    ✓
   </div>

   <div class="number">
    ₹0
   </div>

   <b>
    No Fee Due
   </b>

  </div>

  {% endif %}


  <!-- PAID -->

  <div class="card stat">

   <div style="font-size:42px">
    💳
   </div>

   <div class="number">
    ₹{{paid}}
   </div>

   <b style="font-size:18px">
    Paid
   </b>

  </div>

 </div>


 <!-- ATTENDANCE DETAILS -->

 <div class="card">

  <h2>Attendance</h2>

  <div class="attbar">
   <div class="attfill"
        style="width:{{s.attendance}}%">
   </div>
  </div>

  <p>
   {{s.attendance}}% attendance this academic year.
  </p>

 </div>


 <!-- FEE DETAILS -->

 <div class="card">

  <div class="section-title">
   <h2>Fee Details</h2>
  </div>

  <table>

   <tr>
    <th>Fee Type</th>
    <th>Amount</th>
    <th>Status</th>
    <th>Action</th>
   </tr>

   {% for f in fees %}

   <tr>

    <td>
     {{f.fee_type}}
    </td>

    <td>
     ₹{{f.amount}}
    </td>

    <td>

     <span class="badge
       {% if f.status=='PAID' %}paid{% endif %}">
      {{f.status}}
     </span>

    </td>

    <td>

     {% if f.status=="DUE" %}

     <a class="btn green"
        href="/pay/{{f.id}}">
      Pay Now
     </a>

     {% else %}

     <a href="/receipt/{{f.id}}">
      Receipt
     </a>

     {% endif %}

    </td>

   </tr>

   {% endfor %}

  </table>

 </div>


 <!-- CLASS TEACHER -->

 <div class="card">

  <h2>👩‍🏫 Class Teacher</h2>

  <p>
   <b>Mrs. Priya Sharma</b>
  </p>

  <p>
   Mathematics — Class 10
  </p>

 </div>

</div>
""",
        s=s,
        fees=fees,
        due=due,
        paid=paid,
        due_fee_id=due_fee_id
    )

    return page("Parent Dashboard",content)


def teacher_dashboard():
    con=getdb()
    teachers=con.execute("SELECT * FROM teachers").fetchall()
    students=con.execute("SELECT * FROM students").fetchall()
    con.close()

    content=render_template_string(r"""
<div class="container">
 <div class="section-title">
  <h2>Teacher Dashboard</h2>
  <a class="btn dark" href="/logout">Logout</a>
 </div>

 <div class="cards">
  <div class="card stat"><div class="number">{{students|length}}</div><b>Students</b></div>
  <div class="card stat"><div class="number">{{teachers|length}}</div><b>Teachers</b></div>
  <div class="card stat"><div class="number">8</div><b>Classes</b></div>
 </div>

 <div class="card">
  <h2>Teacher Information</h2>
  <table>
   <tr><th>Name</th><th>Subject</th><th>Class</th><th>Qualification</th></tr>
   {% for t in teachers %}
   <tr><td>{{t.name}}</td><td>{{t.subject}}</td><td>{{t.class_name}}</td><td>{{t.qualification}}</td></tr>
   {% endfor %}
  </table>
 </div>
</div>
""",teachers=teachers,students=students)

    return page("Teacher Dashboard",content)

@app.route("/attendance",methods=["GET","POST"])
def attendance():
    if session.get("role") not in ("class_teacher","admin"):
        return redirect("/")

    con=getdb()
    students=con.execute("SELECT * FROM students WHERE class_name='Class 10' AND section='A'").fetchall()

    if request.method=="POST":
        day=datetime.now().strftime("%d-%m-%Y")
        for s in students:
            status=request.form.get("status_"+str(s["id"]),"Present")
            con.execute(
                "INSERT INTO attendance(student_id,day,status) VALUES(?,?,?)",
                (s["id"],day,status)
            )
        con.commit()
        con.close()
        flash("Attendance saved successfully.")
        return redirect("/attendance")

    con.close()

    content=render_template_string(r"""
<div class="container">
 <div class="section-title">
  <h2>Mark Attendance</h2>
  <a class="btn dark" href="/logout">Logout</a>
 </div>

 <div class="card">
  <p><b>Class:</b> Class 10 &nbsp; <b>Section:</b> A</p>
  <p class="small">Date: {{date}}</p>

  <form method="post">
   <table>
    <tr><th>Roll No.</th><th>Student Name</th><th>Status</th></tr>
    {% for s in students %}
    <tr>
     <td>{{s.roll}}</td>
     <td>{{s.name}}</td>
     <td>
      <label style="font-weight:normal">
       <input type="radio" name="status_{{s.id}}" value="Present" checked style="width:auto;margin:0"> Present
      </label>
      &nbsp;
      <label style="font-weight:normal">
       <input type="radio" name="status_{{s.id}}" value="Absent" style="width:auto;margin:0"> Absent
      </label>
     </td>
    </tr>
    {% endfor %}
   </table>
   <br>
   <button class="btn purple">✓ Save Attendance</button>
  </form>
 </div>
</div>
""",students=students,date=datetime.now().strftime("%d-%m-%Y"))

    return page("Attendance",content)

def class_teacher_dashboard():
    con=getdb()
    students=con.execute(
        "SELECT * FROM students WHERE class_name='Class 10' AND section='A'"
    ).fetchall()
    con.close()

    content=render_template_string(r"""
<div class="container">
 <div class="section-title">
  <h2>Class Teacher Dashboard</h2>
  <a class="btn dark" href="/logout">Logout</a>
 </div>

 <div class="card">
  <h2>🛡️ Class Teacher</h2>
  <p><b>Mrs. Priya Sharma</b></p>
  <p>Class 10 — Section A</p>
 </div>

 <div class="cards">
  <div class="card stat"><div class="number">{{students|length}}</div><b>Students in Class</b></div>
  <div class="card stat"><div class="number">94%</div><b>Class Attendance</b></div>
  <div class="card stat"><div class="number">A</div><b>Section</b></div>
 </div>

 <div class="card">
  <div class="section-title">
   <h2>My Students</h2>
   <a class="btn purple" href="/attendance">Manage Attendance</a>
  </div>
  <table>
   <tr><th>Roll</th><th>Student</th><th>Parent</th><th>Attendance</th></tr>
   {% for s in students %}
   <tr>
    <td>{{s.roll}}</td>
    <td>{{s.name}}</td>
    <td>{{s.parent}}</td>
    <td>{{s.attendance}}%</td>
   </tr>
   {% endfor %}
  </table>
 </div>
</div>
""",students=students)

    return page("Class Teacher Dashboard",content)

def admin_dashboard():
    con=getdb()
    students=con.execute("SELECT * FROM students").fetchall()
    teachers=con.execute("SELECT * FROM teachers").fetchall()
    fees=con.execute("SELECT * FROM fees").fetchall()
    notices=con.execute("SELECT * FROM notices ORDER BY id DESC LIMIT 5").fetchall()
    con.close()

    total=len(students)
    paid=sum(x["amount"] for x in fees if x["status"]=="PAID")
    due=sum(x["amount"] for x in fees if x["status"]=="DUE")

    content=render_template_string(r"""
<div class="container">
 <div class="section-title">
  <h2>Admin Dashboard</h2>
  <a class="btn dark" href="/logout">Logout</a>
 </div>

 <div class="cards">
  <div class="card stat"><div class="number">{{total}}</div><b>Total Students</b></div>
  <div class="card stat"><div class="number">{{teachers|length}}</div><b>Total Teachers</b></div>
  <div class="card stat"><div class="number">8</div><b>Total Classes</b></div>
  <div class="card stat"><div class="number">₹{{paid}}</div><b>Fees Collected</b></div>
 </div>

 <div class="grid2">
  <div class="card">
   <h2>💰 Fee Overview</h2>
   <p><b>Paid:</b> ₹{{paid}}</p>
   <p><b>Due:</b> ₹{{due}}</p>
   <a class="btn orange" href="/admin/fees">Fee Management</a>
  </div>

  <div class="card">
   <h2>📋 Attendance</h2>
   <p>Manage class attendance and view student records.</p>
   <a class="btn purple" href="/attendance">Attendance Management</a>
  </div>
 </div>

 <div class="card">
  <h2>🧑‍🎓 Students</h2>
  <table>
   <tr><th>Roll</th><th>Name</th><th>Class</th><th>Parent</th><th>Attendance</th></tr>
   {% for s in students %}
   <tr><td>{{s.roll}}</td><td>{{s.name}}</td><td>{{s.class_name}} - {{s.section}}</td><td>{{s.parent}}</td><td>{{s.attendance}}%</td></tr>
   {% endfor %}
  </table>
 </div>

 <div class="card">
  <h2>👨‍🏫 Teachers</h2>
  <table>
   <tr><th>Name</th><th>Subject</th><th>Class</th></tr>
   {% for t in teachers %}
   <tr><td>{{t.name}}</td><td>{{t.subject}}</td><td>{{t.class_name}}</td></tr>
   {% endfor %}
  </table>
 </div>

 <div class="card">
  <h2>📢 Recent Notices</h2>
  {% for n in notices %}
  <p><b>{{n.title}}</b> — {{n.date}}</p>
  {% endfor %}
 </div>
</div>
""",students=students,teachers=teachers,notices=notices,
   total=total,paid=paid,due=due)

    return page("Admin Dashboard",content)

@app.route("/admin/fees")
def admin_fees():
    if session.get("role")!="admin":
        return redirect("/login/admin")

    con=getdb()
    rows=con.execute("""
    SELECT fees.*,students.name,students.roll
    FROM fees JOIN students ON students.id=fees.student_id
    ORDER BY fees.id DESC
    """).fetchall()
    con.close()

    content=render_template_string(r"""
<div class="container">
 <div class="section-title">
  <h2>Fee Management</h2>
  <a class="btn dark" href="/portal/admin">Back</a>
 </div>

 <div class="card">
  <table>
   <tr><th>Student</th><th>Roll</th><th>Fee</th><th>Amount</th><th>Status</th></tr>
   {% for f in rows %}
   <tr>
    <td>{{f.name}}</td>
    <td>{{f.roll}}</td>
    <td>{{f.fee_type}}</td>
    <td>₹{{f.amount}}</td>
    <td><span class="badge {% if f.status=='PAID' %}paid{% endif %}">{{f.status}}</span></td>
   </tr>
   {% endfor %}
  </table>
 </div>
</div>
""",rows=rows)

    return page("Fee Management",content)

@app.route("/pay/<int:fid>",methods=["GET","POST"])
def pay(fid):
    if session.get("role")!="parent":
        return redirect("/login/parent")

    con=getdb()
    f=con.execute("""
    SELECT fees.*,students.name,students.class_name,students.section
    FROM fees JOIN students ON students.id=fees.student_id
    WHERE fees.id=? AND students.id=1
    """,(fid,)).fetchone()

    if not f:
        con.close()
        return "Fee not found",404

    if request.method=="POST":
        receipt="GJIS-"+datetime.now().strftime("%Y%m%d%H%M%S")
        paid_date=datetime.now().strftime("%d %b %Y, %I:%M %p")
        con.execute("""
        UPDATE fees SET status='PAID',paid_date=?,receipt=? WHERE id=?
        """,(paid_date,receipt,fid))
        con.commit()
        con.close()
        return redirect("/receipt/"+str(fid))

    con.close()

    content=render_template_string(r"""
<div class="container">
 <div class="login-wrap" style="max-width:650px">
  <div class="card">
   <h1>💳 Online Fee Payment</h1>
   <p>Gyan Jyoti International School</p>
   <hr>
   <h2>{{f.fee_type}}</h2>
   <div class="number">₹{{f.amount}}</div>
   <p>Student: <b>{{f.name}}</b></p>
   <p>Class: {{f.class_name}} - {{f.section}}</p>

   <div class="card" style="background:#fff8e9">
    <b>Demo Payment</b>
    <p class="small">This demo does not charge real money.</p>
   </div>

   <form method="post">
    <label>Demo Card / UPI Reference</label>
    <input placeholder="1234 5678 9012">
    <label>Payment Method</label>
    <select>
     <option>UPI</option>
     <option>Debit Card</option>
     <option>Credit Card</option>
     <option>Net Banking</option>
    </select>
    <button type="submit" class="btn green" style="width:100%;font-size:17px">
     🔒 Pay ₹{{f.amount}} Now
    </button>
   </form>
  </div>
 </div>
</div>
""",f=f)

    return page("Online Fee Payment",content)

@app.route("/receipt/<int:fid>")
def receipt(fid):
    if session.get("role")!="parent":
        return redirect("/login/parent")

    con=getdb()
    f=con.execute("""
    SELECT fees.*,students.name,students.class_name,students.section
    FROM fees JOIN students ON students.id=fees.student_id
    WHERE fees.id=? AND students.id=1
    """,(fid,)).fetchone()
    con.close()

    if not f:
        return "Receipt not found",404

    content=render_template_string(r"""
<div class="container">
 <div style="max-width:750px;margin:auto">
  <div class="card receipt" id="receipt">
   <center>
    <div style="font-size:45px">🎓</div>
    <h1>Gyan Jyoti International School</h1>
    <p>Turkpattti, Kushinagar, Uttar Pradesh</p>
    <h2>FEE PAYMENT RECEIPT</h2>
   </center>

   <hr>

   <div class="grid2">
    <div>
     <p><b>Receipt No.</b><br>{{f.receipt}}</p>
     <p><b>Student</b><br>{{f.name}}</p>
     <p><b>Class</b><br>{{f.class_name}} - {{f.section}}</p>
    </div>
    <div>
     <p><b>Fee Type</b><br>{{f.fee_type}}</p>
     <p><b>Amount Paid</b><br>₹{{f.amount}}</p>
     <p><b>Payment Date</b><br>{{f.paid_date}}</p>
    </div>
   </div>

   <hr>

   <center>
    <div class="success">✓ PAYMENT SUCCESSFUL</div>
    <p>Thank you for making the fee payment.</p>
   </center>
  </div>

  <button class="btn blue" onclick="window.print()">🧾 Print / Save Bill</button>
  <a class="btn green" href="/dashboard">Back to Dashboard</a>
 </div>
</div>
""",f=f)

    return page("Fee Receipt",content)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__=="__main__":
    print("\n==============================================")
    print(" GYAN JYOTI INTERNATIONAL SCHOOL")
    print(" PROFESSIONAL DEMO PORTAL")
    print("==============================================")
    print("Website: http://127.0.0.1:5000")
    print("")
    print("Parent       : parent / parent123")
    print("Teacher      : teacher / teacher123")
    print("Class Teacher: ct / ct123")
    print("Admin        : admin / admin123")
    print("==============================================\n")
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=False)
