import logging
import os

from flask import Flask, make_response as _make_response
from flask import request
from xml.sax.saxutils import quoteattr

import borders.borders

app = Flask(__name__)


def make_response(ret, code):
    resp = _make_response(ret, code)
    resp.mimetype = 'text/xml; charset=utf-8'
    return resp


@app.route("/all/<terc>.osm", methods=["GET", ])
def get_all_borders(terc):
    resp = make_response(borders.borders.get_borders(terc), 200)
    resp.headers['Content-Disposition'] = 'attachment; filename={0}.osm'.format(terc)
    return resp


@app.route("/nosplit/<terc>.osm", methods=["GET", ])
def get_nosplit_borders(terc):
    resp = make_response(borders.borders.get_borders(terc, borders_mapping=lambda x: x), 200)
    resp.headers['Content-Disposition'] = 'attachment; filename={0}.osm'.format(terc)
    return resp


@app.route("/error<stuff>", methods=["GET", ])
def error(stuff):
    raise ValueError("Sample error")


@app.route("/<terc>.osm", methods=["GET", ])
def get_lvl8_borders(terc):
    resp = make_response(borders.borders.get_borders(terc, lambda x: x.tags.get('admin_level') == "8"), 200)
    resp.headers['Content-Disposition'] = 'attachment; filename={0}.osm'.format(terc)
    return resp


@app.errorhandler(Exception)
def report_exception(e):
    app.logger.error('{0}: {1}'.format(request.path, e), exc_info=(type(e), e, e.__traceback__))
    return make_response(
        """<?xml version='1.0' encoding='UTF-8'?>
        <osm version="0.6" generator="import adresy merger.py">
            <node id="-1" lon="19" lat="52">
                <tag k="fixme" v=%s />
            </node>
        </osm>""" % quoteattr(repr(e)), 200)


if __name__ == '__main__':
    ADMINS = ['logi-osm@vink.pl']
    if not app.debug:
        from logging.handlers import SMTPHandler

        mail_handler = SMTPHandler('127.0.0.1',
                                   'server-error@vink.pl',
                                   ADMINS, 'OSM Rest-Server Failed')
        mail_handler.setLevel(logging.INFO)
        app.logger.addHandler(mail_handler)
    app.run(host='0.0.0.0', port=5002, debug=bool(os.environ.get('DEBUG', False)))
