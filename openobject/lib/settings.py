from oobjlib.connection import Connection


def make_cnx(dbname="", login="",
    password="",
    server=""):
    return Connection(
        server=server,
        dbname=dbname,
        login=login,
        password=password,
        port=8069)

