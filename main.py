from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'document_scanner_app'


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/about', methods=['GET'])
def about():
    return render_template('about.html')


if __name__ == '__main__':
    app.run(debug=True)
