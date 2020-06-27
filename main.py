import urllib.parse as urlparse
import http.server, socketserver, os
import requests
import json
from datetime import datetime, timedelta
from dateutil import parser

search_history = {}

def send_post(id): # Отправка POST запроса для поиска на rsmp.nalog.ru
    if id in search_history.keys(): # Проверяем был ли поиск с таким запросом
        if "dtQueryBegin" in search_history[id]:
            date_time_str = search_history[id]["dtQueryBegin"]
            new_date = parser.parse(date_time_str)
            past = datetime.now() - timedelta(seconds=300)
            if new_date > past:
                print("return from cache")
                return search_history[id]

    data = 'mode=quick&page=1&query='+id+'&pageSize=10&sortField=NAME_EX&sort=ASC' # Тело запроса
    data = data.encode()
    headers = {} # Формируем заголовки
    headers['Host'] = 'rmsp.nalog.ru'
    headers['Connection'] = 'keep-alive'
    headers['Content-Length'] = str(len(data))
    headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
    headers['X-Requested-With'] = 'XMLHttpRequest'
    headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    headers['Origin'] = 'https://rmsp.nalog.ru'
    headers['Sec-Fetch-Site'] = 'same-origin'
    headers['Sec-Fetch-Mode'] = 'cors'
    headers['Sec-Fetch-Dest'] = 'empty'
    headers['Referer'] = 'https://rmsp.nalog.ru/search.html?mode=quick'
    headers['Accept-Encoding'] = 'gzip, deflate, br'
    headers['Accept-Language'] = 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7'
    cookies = {} # Добавляем куки чтобы вызывать меньше подозрений у сервера
    jar = requests.cookies.RequestsCookieJar()
    jar.set('_ym_d','1593178141')
    jar.set('_ym_uid','1593178141869048956')
    jar.set('_ym_isad','2')
    jar.set('top100_id','t1.289463.606547912.1593178165921')
    jar.set('tmr_lvid','335f06728c9b3e4bcff1a32b0d6cd7f5')
    jar.set('tmr_lvidTS','1593178165947')
    jar.set('last_visit','1593200955497::1593211755497')
    jar.set('tmr_reqNum','7')
    jar.set('JSESSIONID','DAE91859BA237ED18120F7DCEAEF50B3')

    r = requests.post('https://rmsp.nalog.ru/search-proc.json', headers = headers, cookies = cookies, data=data) # Отправляем запрос
    result = json.loads(r.content.decode('utf-8')) # Получаем данные
    fin = {}
    fin["status"] = 0 # 0 - не найдено, 1 - найдено
    if "dtQueryBegin" in result:
        fin["dtQueryBegin"] = result["dtQueryBegin"]
    else:
        fin["dtQueryBegin"] = datetime.now()

    if "data" in result:
        if len(result["data"]) == 1:
            fin["category"] = result["data"][0]["category"]
            fin["status"] = 1
    
    search_history[id] = fin
    return fin

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        urlParams = urlparse.urlparse(self.path)
        if urlParams.path == "/search.html":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(json.dumps(search_history).encode('utf-8'))
        else:   
            if os.access( '.' + os.sep + urlParams.path, os.R_OK ):
                http.server.SimpleHTTPRequestHandler.do_GET(self)
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write((open('index.html').read()))
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = post_data.decode('utf-8')
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        result = send_post(data)
        response = "Не найдено"
        if result["status"] == 1:
            response = result["category"]

        self.wfile.write("{}".format(response).encode('utf-8'))
        
httpd = socketserver.TCPServer(('127.0.0.1', 8000), Handler)
httpd.serve_forever()