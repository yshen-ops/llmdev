import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, make_response
from original.graph import get_bot_response, get_messages_list, memory

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'GET':
        memory.storage.clear()
        response = make_response(render_template('index.html', messages=[]))
        return response

    user_message = request.form['user_message']
    get_bot_response(user_message, memory)
    messages = get_messages_list(memory)

    return make_response(render_template('index.html', messages=messages))

@app.route('/clear', methods=['POST'])
def clear():

    memory.storage.clear()
    response = make_response(render_template('index.html', messages=[]))
    
    return response

if __name__ == '__main__':
    app.run(debug=True)