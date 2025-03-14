@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html', methods=['GET'])
def getMainPage():
    return render_template('index.html')