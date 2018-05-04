from flask import Flask, render_template, request
app = Flask(__name__)

def post_action():
    return get_action()

def get_action():
    hour = '12.00'
    left_context = 'Dawno, dawno temu był sobia para młoda, bardzo piękna para młoda. Msza rozpocznie się o godzinie '
    right_context = '. Następnie para młoda uda się na wesele do Kubusia i będą się bawić do białego rana.'
    return render_template('index.html', hour=hour, left_context=left_context, right_context=right_context)

@app.route("/", methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
       return  post_action()
    else:
       return get_action()




if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
