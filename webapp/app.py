from flask import Flask, render_template, request, make_response, jsonify
import os
from get_utterances import Utterance
import redis
import pickle
import re

app = Flask(__name__)

r = redis.StrictRedis(host='localhost', port=6379, db=0)


def log(msg):
    with open('/tmp/tmp', 'w') as f:
        print(msg, f, flush=True)


def load_utterances(filename):
    with open(filename, 'rb') as f:
        utterances = pickle.load(f)
    return utterances


utterances = load_utterances(
    '/home/siulkilulki/gitrepos/mass-scraper/utterances.pkl')

UTT_SCORES = 'utterance-scores'
COOKIE_NAME = 'cookie-hash'
# log(utterances[0:2])

#initialize_redis_db
# r.flushdb()
# status = None
status = r.get('status')
if status:
    status = status.decode('utf-8')
else:
    r.flushdb()
if status != 'filled':
    log('filling status')
    for i in range(len(utterances)):
        if r.zscore(UTT_SCORES, str(i)) == None:
            log(i)
            r.zadd(UTT_SCORES, 0, str(i))
    r.set('status', 'filled')
    status = 'filled'


def get_next():
    index = int(r.zrangebyscore(UTT_SCORES, '-inf', 'inf')[1])
    left_context = utterances[index]['prefix'].replace('\n', '<br>')
    hour = utterances[index]['hour'].replace('\n', '<br>')
    right_context = ' '.join(
        utterances[index]['suffix'].split(' ')[:10]).replace('\n', '<br>')
    # log('get_next index: {}, score: {}'.format(index,
    #                                            r.zscore(UTT_SCORES, index)))
    return index, left_context, hour, right_context


def get_next_response(cookie_hash):
    index, left_context, hour, right_context = get_next()
    resp = jsonify(
        index=index,
        left_context=left_context,
        hour=hour,
        right_context=right_context)
    if cookie_hash:
        resp.set_cookie(COOKIE_NAME, cookie_hash, max_age=60 * 60 * 24 * 90)
    return resp


def get_by_index(index):
    left_context = utterances[index]['prefix'].replace('\n', '<br>')
    hour = utterances[index]['hour'].replace('\n', '<br>')
    right_context = ' '.join(
        utterances[index]['suffix'].split(' ')[:10]).replace('\n', '<br>')
    # log('get_next index: {}, score: {}'.format(index,
    # r.zscore(UTT_SCORES, index)))
    return index, left_context, hour, right_context


def get_response_by_index(index, cookie_hash):
    index, left_context, hour, right_context = get_by_index(index)
    resp = jsonify(
        index=index,
        left_context=left_context,
        hour=hour,
        right_context=right_context)
    if cookie_hash:
        resp.set_cookie(COOKIE_NAME, cookie_hash, max_age=60 * 60 * 24 * 90)
    return resp


def annotate_redis(yesno, index):
    cookie_hash = request.cookies.get(COOKIE_NAME)
    log('annotate: {}'.format(cookie_hash))
    if not cookie_hash:
        return None
    annotation = r.get('{}:{}'.format(
        cookie_hash, index))  # previous annotation of utterance by that user
    if annotation:
        str_index = int(annotation.decode('utf-8').split(':')[1])
        log(str_index)
        r.setrange(index, str_index, yesno)  #sets str_index to yesno value
    else:
        # before = r.zscore(UTT_SCORES, index)
        r.zincrby(UTT_SCORES, index)
        # log('incrementing index {}, before_val: {}, value: {}'.format(
        #     index, before, r.zscore(UTT_SCORES, index)))
        str_index = r.append(index, yesno) - 1
    r.set('{}:{}'.format(cookie_hash, index), '{}:{}'.format(yesno, str_index))
    r.lpush(cookie_hash, '{}:{}:{}'.format(yesno, index, str_index))
    return cookie_hash


def set_cookie(js_hash):
    # dodawać nowe js_hash do listy z key bedacym cookie_hash
    old_cookie_hash = None
    cookie_hash = request.cookies.get(COOKIE_NAME)
    log(js_hash)
    log('set cookie: {}'.format(cookie_hash))
    if not cookie_hash:
        old_cookie_hash = r.get(js_hash)
        if not old_cookie_hash:
            cookie_hash = str(
                int.from_bytes(os.urandom(4), byteorder='little'))
            r.set(js_hash, cookie_hash)
        else:
            cookie_hash = old_cookie_hash.decode('utf-8')
    log('old_cookie: {}, cookie: {}'.format(old_cookie_hash, cookie_hash))
    return cookie_hash


def http_post():
    index = str(request.form.get('index'))
    action = request.form['action']
    js_hash = request.form['hash']
    log(request.form)
    if action == 'get':
        cookie_hash = set_cookie(js_hash)
        return get_next_response(cookie_hash)
    elif action == 'undo':
        cookie_hash = request.cookies.get(COOKIE_NAME)
        if cookie_hash:
            last_action = r.lpop(cookie_hash)
            if last_action:
                index = int(last_action.decode('utf-8').split(':')[1])
                return get_response_by_index(index, cookie_hash)
        # if no cookie-hash or action list is empty return None
    elif action == 'yes':
        cookie_hash = annotate_redis('y', index)
        if cookie_hash:
            return get_next_response(cookie_hash)
    elif action == 'no':
        cookie_hash = annotate_redis('n', index)
        if cookie_hash:
            return get_next_response(cookie_hash)


def http_get():
    return render_template('index.html')


@app.route("/", methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        return http_post()
    else:
        return http_get()


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
