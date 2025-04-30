from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def base():
    return render_template('base.html')

@app.route('/main')
def main_page():
    return render_template('main.html')

@app.route('/stats')
def stats_page():
    return render_template('stats.html')

if __name__ == '__main__':
    app.run(debug=True)