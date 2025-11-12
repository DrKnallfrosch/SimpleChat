from bottle import Bottle, template, static_file, redirect, request, response
from authentication import userbase
from datetime import datetime
import random as rdom
import time
import json


class WebApp:
    def __init__(self):
        self.sessions = {}  # session_id -> user_data
        self.chat_messages = []  # Liste aller Chat-Nachrichten
        self.app = Bottle()
        self.setup_routes()

    def setup_routes(self):
        """Richtet die Routen der Webanwendung ein"""
        self.app.route('/')(self.index)
        self.app.route('/login')(self.login)
        self.app.route('/static/style/<filename:path>')(self.style)
        self.app.route('/static/js/<filename:path>')(self.js)
        self.app.route('/chat_room', method='POST')(self.chat_room)
        self.app.route('/chat', method='GET')(self.chat)
        self.app.route('/chat', method='POST')(self.chat_post)
        self.app.route('/api/messages')(self.api_messages)
        self.app.route('/api/send', method='POST')(self.api_send)
        self.app.route('/check_session')(self.check_session)
        self.app.route('/logout')(self.logout)
        self.app.error(404)(self.error404)
        self.app.error(405)(self.error405)

    def index(self):
        """Startseite - Leitet zum Login weiter"""
        return redirect('/login')

    def login(self):
        """Login-Seite"""
        error = request.query.get('error', 'none')
        return template('template/index.html', error_display=error)

    def get_current_user(self):
        """Holt den aktuellen Benutzer aus der Session"""
        session_id = request.get_cookie('session_id')

        if not session_id:
            return None

        if session_id not in self.sessions:
            return None

        session_data = self.sessions[session_id]
        session_age = time.time() - session_data['timestamp']

        if session_age >= 300:  # 5 Minuten abgelaufen
            # Session automatisch bereinigen
            del self.sessions[session_id]
            return None

        return session_data['username']

    def check_session(self):
        """API-Endpoint zum Überprüfen der Session"""
        username = self.get_current_user()
        if username:
            session_id = request.get_cookie('session_id')
            session_data = self.sessions[session_id]
            session_age = time.time() - session_data['timestamp']
            remaining_time = 300 - session_age

            return json.dumps({
                'valid': True,
                'username': username,
                'remaining_time': int(remaining_time)
            })
        else:
            return json.dumps({
                'valid': False,
                'redirect_url': '/login?error=Session expired'
            })

    def chat_room(self):
        username = request.forms.get('username')
        password = request.forms.get('password')

        if userbase.authenticate(username, password):
            # Session ID generieren
            while True:
                session_id = str(rdom.randint(1, 9999999))
                if session_id not in self.sessions:
                    break

            # Session speichern
            self.sessions[session_id] = {
                'username': username,
                'timestamp': time.time()
            }

            # Session Cookie setzen
            response.set_cookie('session_id', session_id, path='/', max_age=300)

            return template('template/chat_room.html', username=username)
        else:
            return redirect('/login?error=Login failed')

    def chat(self):
        """Haupt-Chat-Seite"""
        username = self.get_current_user()

        if not username:
            return redirect('/login?error=Session expired')

        return template('template/chat_room.html', username=username)

    def chat_post(self):
        """Verarbeitet Formular-basierte Nachrichten"""
        username = self.get_current_user()
        if not username:
            return redirect('/login?error=Session expired')

        message = request.forms.get('message', '').strip()
        if message:
            self.add_message(username, message)

        return template('template/chat_room.html', username=username)

    def api_messages(self):
        """API: Gibt alle Nachrichten zurück"""
        username = self.get_current_user()
        if not username:
            return json.dumps({
                'error': 'Session expired',
                'redirect': '/login?error=Session expired'
            })

        last_id = int(request.query.get('last_id', 0))
        filtered_messages = [msg for msg in self.chat_messages if msg['id'] > last_id]

        return json.dumps({
            'messages': filtered_messages,
            'current_user': username
        })

    def api_send(self):
        """API: Empfängt neue Nachrichten"""
        username = self.get_current_user()
        if not username:
            return json.dumps({
                'success': False,
                'error': 'Session expired',
                'redirect': '/login?error=Session expired'
            })

        message = request.forms.get('message', '').strip()
        if not message:
            return json.dumps({'success': False, 'error': 'Empty message'})

        message_id = self.add_message(username, message)
        session_id = request.get_cookie('session_id')
        response.set_cookie('session_id', session_id, path='/', max_age=300)

        return json.dumps({
            'success': True,
            'message_id': message_id
        })

    def add_message(self, username, message):
        """Fügt eine Nachricht zum Chat hinzu"""
        message_data = {
            'id': len(self.chat_messages) + 1,
            'username': username,
            'message': message,
            'timestamp': datetime.now().strftime('%H:%M'),
            'datetime': datetime.now().isoformat()
        }
        self.chat_messages.append(message_data)

        # Begrenze die Anzahl der gespeicherten Nachrichten
        if len(self.chat_messages) > 1000:
            self.chat_messages = self.chat_messages[-500:]

        return message_data['id']

    def logout(self):
        """Logout Route - Löscht die Session"""
        session_id = request.get_cookie('session_id')

        if session_id in self.sessions:
            del self.sessions[session_id]

        # Cookie löschen
        response.set_cookie('session_id', '', path='/', expires=0)

        return redirect('/login')

    def error404(self, error):
        return template('template/error404.html')

    def error405(self, error):
        return template('template/error405.html')

    def style(self, filename):
        return static_file(filename, root="./static/style")

    def js(self, filename):
        return static_file(filename, root="./static/js")

    def run(self):
        self.app.run(host='localhost', port=8080, debug=True)


if __name__ == '__main__':
    web_app = WebApp()
    web_app.run()
