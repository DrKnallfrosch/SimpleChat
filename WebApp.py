from bottle import Bottle, template, static_file, redirect

class WebApp:
    def __init__(self):
        self.app = Bottle()
        self.app.route('/')(self.index)
        self.app.route('/login')(self.login)
        self.app.route('/style/style.css')(self.style)
        self.app.route('/chat_room')(self.chat_room)

    def index(self):
        return redirect('/login')
    def login(self):
        return template('template/index.html')

    def style(self):
        return static_file('style/style.css', root=".")

    def chat_room(self):
        return template('template/chat_room.tpl')

    def run(self):
        self.app.run(host='localhost', port=8080, debug=True)

if __name__ == '__main__':
    web_app = WebApp()
    web_app.run()