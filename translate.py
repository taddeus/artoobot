import requests


translate_url = 'http://www.r2d2translator.com/composeSongD2R2.php'
file_url = 'http://www.r2d2translator.com/audio/%s.MP3'


class ReqError(RuntimeError):
    pass


def encode(msg):
    e = ''
    for i, c in enumerate(msg):
        if i:
            e += '!'
        if c == ' ':
            e += 'silence'
        else:
            e += str(1 + (ord(c) + 60) % 80)
    return e


def get_audio_url(msg):
    enc = encode(msg)
    vol = '!'.join('1' * len(enc))
    req = requests.post(translate_url, data={'volumes': vol, 'sons': enc})
    if req.status_code != 200:
        raise ReqError()
    res = req.text
    if not res.startswith(' &cle='):
        raise ReqError()
    fileid = res[6:]
    return file_url % fileid


def request_audio(msg):
    req = requests.get(get_audio_url(msg), stream=True)
    if req.status_code != 200:
        raise ReqError()
    return req


def read_request(req):
    return req.raw.read(decode_content=False)


def save_request(req, path):
    with file(path, 'wb') as f:
        for chunk in req.iter_content(1024):
            f.write(chunk)


def get_audio(msg):
    return read_request(request_audio(msg))


def save_audio(msg, path):
    save_request(request_audio(msg), path)
