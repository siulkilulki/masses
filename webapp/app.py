from flask import Flask, render_template, request, make_response
import redis
app = Flask(__name__)


def load_parishes(directory):
    return {}


parishes = load_parishes('dir')


def post_action():
    return get_action()


def get_action():
    hour = '12.00'
    left_context = 'Dawno, dawno temu był sobia para młoda, bardzo piękna para młoda. Msza rozpocznie się o godzinie '
    right_context = '. Następnie para młoda uda się na wesele do Kubusia i będą się bawić do białegop prana.'
    resp = make_response(
        render_template(
            'index.html',
            hour=hour,
            left_context=left_context,
            right_context=right_context))
    return resp


@app.route("/", methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        return post_action()
    else:
        return get_action()


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
