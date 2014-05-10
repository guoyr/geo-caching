
from constants import *

def closeConnection(conn):
    from twisted.internet import reactor
    def c():
        conn.loseConnection()
    reactor.callLater(TIMEOUT, c)