from dotenv import load_dotenv
import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
app = Flask(__name__)

def configure():
    load_dotenv()


@app.route('/')
def index():
   print('Request for index page received')
   secret_nde = os.environ.get('SECRETNDE')
   print(secret_nde)
   return render_template('index.html', secret_nde=secret_nde)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   configure()
   name = request.form.get('name')
   print("hello")
   secret_nde = os.environ.get('SECRETNDE')
   print(secret_nde)

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name, secret_nde=secret_nde)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))


if __name__ == '__main__':
   app.run()