from bottle import Bottle, template, static_file, redirect

class WebApp:
    def __init__(self):
        self.app = Bottle()
        self.app.route('/')(self.index)
        self.app.route('/login')(self.login)
        self.app.route('/register')(self.register)
        self.app.route('/style/<filename:path>')(self.style)
        self.app.route('/chat_room', method='POST')(self.chat_room)
        self.app.error(404)(self.error404)
        self.app.error(405)(self.error405)

    def index(self):
        return redirect('/login')

    def login(self):
        return template('template/index.html')

    def register(self):
        return template('template/register.html')

    def chat_room(self):
        return template('template/chat_room.html')

    def error404(self, error):
        return template('template/error404.html')

    def error405(self, error):
        return template('template/error405.html')

    def style(self, filename):
        return static_file(filename, root="./style")

    def run(self):
        self.app.run(host='localhost', port=8080, debug=True)

if __name__ == '__main__':
    web_app = WebApp()
    web_app.run()
