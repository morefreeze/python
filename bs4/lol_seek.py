''' grab lol player info from 178 API '''
#!/bin/env python
#coding=utf-8
import urllib
import urllib2

def post(url, data):
    ''' copy from web post method '''
    req = urllib2.Request(url)
    data = urllib.urlencode(data)
    #enable cookie
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(req, data)
    return response.read()

def main():
    ''' function main write jb comment '''
    pass

if __name__ == '__main__':
    main()
