import http.server
import requests
from urllib.parse import unquote, parse_qs

memory = {}

form = '''<!DOCTYPE html>
<title>Bookmark Server</title>
<form method="POST">
    <label>Long URI:
        <input name="longuri">
    </label>
    <br>
    <label>Short name:
        <input name="shorturi">
    </label>
    <br>
    <button type="submit">Save it!</button>
</form>
<p>URIs I know about:
<pre>
{}
</pre>
'''


def checkURI(uri, timeout=5):


    try:
        r = requests.get(uri, timeout=timeout)
        return r.status_code == 200
    except requests.RequestException:
        return false



class Shortner(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        name = unquote(self.path[1:])

        if name:
            if name in memory:
                self.send_response(303)
                self.send_header('location',memory[name])
                self.end_headers()
            else:
                self.send_response(404)
                self.send_header('content-type','plain/text; charset=utf-8')
                self.end_headers()
                self.wfile.write("I donot know {}".format(name).encode())

        else:
            self.send_response(200)
            self.send_header('content-type','plain/text ; charset=utf-8')
            self.end_headers()
            known = "\n"
            for key in sorted(memory.keys()):
                known.join('{}:{}'.format(key, memory[key]))
            self.wfile.write(form.format(known).encode())


    def do_POST(self):
        length = int(self.get_headers('content-length',0))
        body = self.rfile.read(length).decode()
        params = parse_qs(body)

        if "longuri" not in params or "shorturi" not in params:
            self.send_response(400)
            self.send_headers('content-type','plain/text ; charset=utf-8')
            self.end_headers()
            self.wfile.write("Missing some fields".encode())
            return
        longuri = params["longuri"][0]
        shorturi = params["shorturi"][0]

        if checkURI(longuri):
            memory[shorturi] = longuri
            self.send_response(303)
            self.send_header('location','/')
            self.end_headers()

        else:
            self.send_respone(404)
            self.send_header('content-type','plain/text ; charset-utf-8')
            self.end_headers()
            self.wfile.write("Couldn't fetch uri {}".format(longuri).encode())



if __name__ == '__main__':
    server_address = ('',8000)
    httpd = http.server.HTTPServer(server_address,Shortner)
    httpd.serve_forever()