# -*- coding: utf-8 -*-

import tornado.ioloop
import tornado.web
import tornado.httpserver
import datetime, time
from naivere.regex import *

def renderMatch(string, start, end):
    return "%s<strong>%s</strong>%s" % (string[0:start],string[start:end+1],string[end+1:len(string)])

def testMatch(pattern,string,isGreedy):
    result = "\n"
    re = Regex(pattern,isGreedy)
    if re.validationResult.error == ERR_NONE:
        m = re.match(string)
        if m.matched:
            result += "match found from %d to %d, result: %s\n" % (m.begin, m.end, renderMatch(string,m.begin,m.end))
        else:
            result += "no match found\n"
    return result + "\n" + re.log

def testMatches(pattern,string):
    result = "\n"
    re = Regex(pattern,False)
    if re.validationResult.error == ERR_NONE:
        matches = re.matches(string)
        if len(matches) > 0:
            result += "matches found:\n"
            for match in matches:
                result += "\tfrom %d to %d, result: %s\n" % (match.begin, match.end, renderMatch(string,match.begin,match.end))
        else:
            result += "no match found\n"
    return result + "\n" + re.log

#handlers

class TestHandler( tornado.web.RequestHandler  ):
    def get( self ):
        self.render("index.html", result="",string="",pattern="",matches="",isGreedy="")
    def post( self, *param, **args ):
        try:
            string = self.get_argument("string")
            pattern = self.get_argument("pattern")
            matches = self.get_argument("matches") == "True"
            isGreedy = self.get_argument("is_greedy") == "True"
            print "%s tested %s for %s" % (self.request.remote_ip,pattern,string)
            if matches:
                self.render("index.html", result = testMatches(pattern,string).replace("\n","<br/>").replace("\t","    ").replace(" ","&nbsp;"),string=string,pattern=pattern,matches=matches,isGreedy=isGreedy)
            else:
                self.render("index.html", result = testMatch(pattern,string,isGreedy).replace("\n","<br/>").replace("\t","    ").replace(" ","&nbsp;"),string=string,pattern=pattern,matches=matches,isGreedy=isGreedy)
        except:
            self.render("index.html", result="",string="",pattern="",matches="",isGreedy="")

application = tornado.web.Application([
    (r"/", TestHandler),
    (r"/(.*\.css)", tornado.web.StaticFileHandler, dict(path="") )
])

#portal
if __name__ == "__main__":
    http_server = tornado.httpserver.HTTPServer( application )
    http_server.listen( 8123 )
    tornado.ioloop.IOLoop.instance().start()
