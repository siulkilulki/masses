from flask import Flask, render_template, request, make_response, jsonify
import time
import os
from get_utterances import Utterance
import redis
import pickle
import re
import logging

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

r = redis.StrictRedis(host='localhost', port=6379, db=0)


def log(msg):
    app.logger.info(msg)


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
    log('get_next index: {}, score: {}'.format(index,
                                               r.zscore(UTT_SCORES, index)))
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


def annotate_redis(yesno, index, ip_addr):
    cookie_hash = request.cookies.get(COOKIE_NAME)
    # log('annotate: {}'.format(cookie_hash))
    if not cookie_hash:
        return None
    annotation = r.get('{}:{}'.format(
        cookie_hash, index))  # previous annotation of utterance by that user
    if annotation:
        str_index = int(annotation.decode('utf-8').split(':')[1])
        r.setrange(index, str_index, yesno)  #sets str_index to yesno value
    else:
        # before = r.zscore(UTT_SCORES, index)
        r.zincrby(UTT_SCORES, index)
        # log('incrementing index {}, before_val: {}, value: {}'.format(
        #     index, before, r.zscore(UTT_SCORES, index)))
        str_index = r.append(index, yesno) - 1
    timestamp = time.time()
    r.set('{}:{}'.format(cookie_hash, index), '{}:{}:{}'.format(
        yesno, str_index, timestamp))
    r.set('{}:{}'.format(ip_addr, index), '{}:{}:{}:{}'.format(
        yesno, str_index, timestamp, cookie_hash))
    r.lpush(cookie_hash, '{}:{}:{}'.format(yesno, index, str_index))
    return cookie_hash


def set_cookie(js_hash):
    ## TODO:  dodawać nowe js_hash do listy z key bedacym cookie_hash | czy trzeba?
    old_cookie_hash = None
    cookie_hash = request.cookies.get(COOKIE_NAME)
    if not cookie_hash:
        old_cookie_hash = r.get(js_hash)
        if not old_cookie_hash:
            cookie_hash = str(
                int.from_bytes(os.urandom(4), byteorder='little'))
            r.set(js_hash, cookie_hash)
            log('Cookie not on client side. Creating new cookie.')
        else:
            log('Cookie not on client side. Getting cookie from fingerprint.')
            cookie_hash = old_cookie_hash.decode('utf-8')
    else:
        log('cookie found on client side')
    return cookie_hash


def http_post():
    index = str(request.form.get('index'))
    action = request.form['action']
    js_hash = request.form['hash']
    ip_addr = str(request.headers.get('X-Real-Ip', request.remote_addr))
    if action == 'get':
        cookie_hash = set_cookie(js_hash)
        resp = get_next_response(cookie_hash)
    elif action == 'undo':
        cookie_hash = request.cookies.get(COOKIE_NAME)
        if cookie_hash:
            last_action = r.lpop(cookie_hash)
            if last_action:
                index = int(last_action.decode('utf-8').split(':')[1])
                resp = get_response_by_index(index, cookie_hash)
        # if no cookie-hash or action list is empty resp = None
    elif action == 'yes':
        cookie_hash = annotate_redis('y', index, ip_addr)
        if cookie_hash:
            resp = get_next_response(cookie_hash)
    elif action == 'no':
        cookie_hash = annotate_redis('n', index, ip_addr)
        if cookie_hash:
            resp = get_next_response(cookie_hash)
    if resp:
        # r.sadd
        log(f'ip: {ip_addr}, cookie: {cookie_hash}, hash: {js_hash}, action: {action}, index: {index}'
            )
        return resp


def http_get():
    return render_template('index.html')


@app.route("/", methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        return http_post()
    else:
        return http_get()


if __name__ == "__main__":
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    # app.logger.setLevel(gunicorn_logger.level)
    app.run(host='0.0.0.0', debug=False)
