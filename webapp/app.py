from flask import Flask, render_template, request, make_response, jsonify
import secrets
import time
from get_utterances import Utterance
import redis
import pickle
import re
import logging

UTT_SCORES = 'utterance-scores'
COOKIE_NAME = 'cookie-hash'
MAX_COOKIES_PER_IP = 5

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

r = redis.StrictRedis(unix_socket_path='/redis-socket/redis.sock', db=0)


def log(msg):
    app.logger.info(msg)


def load_utterances(filename):
    with open(filename, 'rb') as f:
        utterances = pickle.load(f)
    return utterances


utterances = load_utterances(
    '/home/siulkilulki/gitrepos/mass-scraper/utterances.pkl')

#initialize_redis_db
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


def get_utterance_for_web(index):
    left_context = utterances[index]['prefix'].replace('\n', '<br>')
    hour = utterances[index]['hour'].replace('\n', '<br>')
    right_context = ' '.join(
        utterances[index]['suffix'].split(' ')[:10]).replace('\n', '<br>')
    return left_context, hour, right_context


def find_not_annotated(cookie_hash):
    # XXX: should be effecient enough even though it's O(n)
    for index in range(len(utterances)):
        if not r.exists(f'{cookie_hash}:{index}'):
            return index


def get_next(cookie_hash):
    """returns utterance with minmum annotations if that utterance
    wasn't annotated by cookie_hash user
    or not yet annotated utterance by cookie_hash user"""
    index = int(r.zrangebyscore(UTT_SCORES, '-inf', 'inf')[1])
    if r.exists(f'{cookie_hash}:{index}'):
        index = find_not_annotated(cookie_hash)
        log('found unannotated index: {}'.format(index))
    left_context, hour, right_context = get_utterance_for_web(index)
    # log('get_next index: {}, score: {}'.format(index,
    #                                            r.zscore(UTT_SCORES, index)))
    return index, left_context, hour, right_context


def get_next_response(cookie_hash):
    index, left_context, hour, right_context = get_next(cookie_hash)
    resp = jsonify(
        index=index,
        left_context=left_context,
        hour=hour,
        right_context=right_context)
    if cookie_hash:
        resp.set_cookie(COOKIE_NAME, cookie_hash, max_age=60 * 60 * 24 * 90)
    return resp


def get_by_index(index):
    left_context, hour, right_context = get_utterance_for_web(index)
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


def annotate_redis(yesno, index, ip_addr, cookie_hash):
    # log('annotate: {}'.format(cookie_hash))
    timestamp = time.time()
    annotation = r.get('{}:{}'.format(
        cookie_hash, index))  # previous annotation of utterance by that user
    if annotation:
        # log(annotation.decode('utf-8'))
        str_index = int(annotation.decode('utf-8').split(':')[1])
        r.setrange(index, str_index, yesno)  #sets str_index to yesno value
    else:
        # before = r.zscore(UTT_SCORES, index)
        r.zincrby(UTT_SCORES, index)
        # log('incrementing index {}, before_val: {}, value: {}'.format(
        #     index, before, r.zscore(UTT_SCORES, index)))
        str_index = r.append(index, yesno) - 1
    r.set('{}:{}'.format(cookie_hash, index), '{}:{}:{}:{}'.format(
        yesno, str_index, timestamp, ip_addr))
    r.set('{}:{}'.format(ip_addr, index), '{}:{}:{}:{}'.format(
        yesno, str_index, timestamp, cookie_hash))
    undo_cookie_key = 'undo:' + cookie_hash
    first_undo_action = r.rpop(undo_cookie_key)
    if first_undo_action:
        first_undo_action = first_undo_action.decode('utf-8')
        if first_undo_action.split(':')[1] != str(index):
            r.lpush(cookie_hash, first_undo_action)
    while (r.llen(undo_cookie_key) != 0):
        r.rpoplpush(undo_cookie_key, cookie_hash)
    r.lpush(cookie_hash, '{}:{}:{}'.format(yesno, index, str_index))


def set_cookie(js_hash):
    ## TODO:  dodawać nowe js_hash do listy z key bedacym cookie_hash | czy trzeba?
    old_cookie_hash = None
    js_hash_key = 'jshash:' + js_hash
    cookie_hash = request.cookies.get(COOKIE_NAME)
    if not cookie_hash:
        old_cookie_hash = r.get(js_hash_key)
        if not old_cookie_hash:
            cookie_hash = secrets.token_urlsafe(16)
            r.set(js_hash_key, cookie_hash)
            log('Cookie not on client side. Creating new cookie.')
        else:
            log('Cookie not on client side. Getting cookie from fingerprint.')
            cookie_hash = old_cookie_hash.decode('utf-8')
    else:
        log('cookie found on client side')
    return cookie_hash


def ip_cookies_violation(ttl):
    if ttl <= 0:
        return None
    else:
        m, s = divmod(ttl, 60)
        h, m = divmod(m, 60)
        hour_str = f'{h} godz. ' if h != 0 else ''
        minute_str = f'{m} min ' if m != 0 else ''
        wait_time_str = hour_str + minute_str + f'{s} sek.'
        return jsonify(wait_time_str=wait_time_str)


def undo(cookie_hash):
    last_action = r.lpop(cookie_hash)
    if last_action:
        last_action = last_action.decode('utf-8')
        r.rpush('undo:' + cookie_hash, last_action)
        index = int(last_action.split(':')[1])
        return get_response_by_index(index, cookie_hash)
    log('No last action returning None')
    # if no cookie-hash or action list is empty resp = None


def handle_ip_cookies(ip_key, cookie_hash):
    """mechanism for forcing users to use maximum X cookies per ip but no more than X"""
    r.sadd(ip_key, cookie_hash)
    if int(r.ttl(ip_key)) == -1:
        r.expire(ip_key, 60 * 60 * 3)
        log('{}, expire started'.format(ip_key))


def get(cookie_hash):
    undo_cookie_key = 'undo:' + cookie_hash
    while (r.llen(undo_cookie_key) != 0):
        r.rpoplpush(undo_cookie_key, cookie_hash)
    return get_next_response(cookie_hash)


def http_post():
    resp = None
    action = request.form['action']
    index = int(request.form['index']) if action != 'get' else None
    js_hash = request.form['hash']
    ip_addr = str(request.headers.get('X-Real-Ip', request.remote_addr))
    ip_key = 'ip-cookies:' + ip_addr
    ip_key_scard = r.scard(ip_key)
    if ip_key_scard >= MAX_COOKIES_PER_IP:
        ttl = int(r.ttl(ip_key))
        app.logger.warning(
            f'MAX_COOKIES_PER_IP violation! ip: {ip_addr}, ttl: {ttl}, scard: {ip_key_scard}, action: {action}, index: {index}'
        )
        return ip_cookies_violation(ttl)
    if action == 'get':
        cookie_hash = set_cookie(js_hash)
        resp = get(cookie_hash)
    else:
        cookie_hash = request.cookies.get(COOKIE_NAME)
        if not cookie_hash:
            log('No cookie hash given by client')
            return None
    if action == 'undo':
        resp = undo(cookie_hash)
    elif action == 'yes':
        annotate_redis('y', index, ip_addr, cookie_hash)
        resp = get_next_response(cookie_hash)
    elif action == 'no':
        annotate_redis('n', index, ip_addr, cookie_hash)
        resp = get_next_response(cookie_hash)
    if resp:
        # r.sadd
        handle_ip_cookies(ip_key, cookie_hash)
        log(f'ip: {ip_addr}, cookie: {cookie_hash}, hash: {js_hash}, action: {action}, index: {index}, ip_scard_before_req: {ip_key_scard}'
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


@app.route("/hidden", methods=['GET', 'POST'])
def dev_root():
    ip_addr = str(request.headers.get('X-Real-Ip', request.remote_addr))
    cookie_hash = request.cookies.get(COOKIE_NAME)
    if ip_addr != '192.168.1.1' and cookie_hash != '1594469046':
        return None
    if request.method == 'POST':
        return http_post()
    else:
        return render_template('index-dev.html')


if __name__ == "__main__":
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    # app.logger.setLevel(gunicorn_logger.level)
    app.run(host='0.0.0.0', debug=False)
