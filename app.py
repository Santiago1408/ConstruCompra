import pymysql  # Asegúrate de que pymysql está instalado y funcionando

app = Flask(__name__)
@app.route('/')
def index():
        return render_template('index.html')
