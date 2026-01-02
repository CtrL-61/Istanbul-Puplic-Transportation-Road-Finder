from flask import Flask, render_template, request
import networkx as nx

app = Flask(__name__)

# Buraya kendi metro ağını ve duraklarını eklediğin kodları koy
# Örnek kısa yapı:
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
