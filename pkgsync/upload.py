import sys
import urllib2
import urlparse
import base64
import httplib
import socket
import StringIO

class Uploader(object):
    """ Sadly because distutils uploads an invalid http post, we must replicate
    that, which means no use of requests. It's back to basics, people, and a
    lot of code copied from distutils/setuptools """

    def __init__(self, repository):
        self.repository = repository
        self.show_response = True

    def register(self, distribution):
        return self._post_registration(
            distribution.meta.register(),
            self.repository.as_password_manager()
        )

    def upload(self, distribution):
        return self._post_upload(distribution.meta.upload())

    def _post_registration(self, data, auth=None):
        # Build up the MIME payload for the urllib2 POST data
        boundary = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'
        sep_boundary = '\n--' + boundary
        end_boundary = sep_boundary + '--'
        chunks = []
        for key, value in data.items():
            # handle multiple entries for the same name
            if type(value) not in (type([]), type( () )):
                value = [value]
            for value in value:
                chunks.append(sep_boundary)
                chunks.append('\nContent-Disposition: form-data; name="%s"'%key)
                chunks.append("\n\n")
                chunks.append(value)
                if value and value[-1] == '\r':
                    chunks.append('\n')  # write an extra newline (lurve Macs)
        chunks.append(end_boundary)
        chunks.append("\n")

        # chunks may be bytes (str) or unicode objects that we need to encode
        body = []
        for chunk in chunks:
            if isinstance(chunk, unicode):
                body.append(chunk.encode('utf-8'))
            else:
                body.append(chunk)

        body = ''.join(body)

        # build the Request
        headers = {
            'Content-type': 'multipart/form-data; boundary=%s; charset=utf-8'%boundary,
            'Content-length': str(len(body))
        }
        req = urllib2.Request(self.repository.upload_url, body, headers)

        # handle HTTP and include the Basic Auth handler
        opener = urllib2.build_opener(
            urllib2.HTTPBasicAuthHandler(password_mgr=auth)
        )
        data = ''
        try:
            result = opener.open(req)
        except urllib2.HTTPError, e:
            if self.show_response:
                data = e.fp.read()
            result = e.code, e.msg
        except urllib2.URLError, e:
            result = 500, str(e)
        else:
            if self.show_response:
                data = result.read()
            result = 200, 'OK'
        if self.show_response:
            dashes = '-' * 75

        return result

    def _post_upload(self, data):
        # set up the authentication
        auth = "Basic " + base64.encodestring(
            self.repository.username + ":" + self.repository.password
        ).strip()

        # Build up the MIME payload for the POST data
        boundary = '--------------GHSKFJDLGDS7543FJKLFHRE75642756743254'
        sep_boundary = '\n--' + boundary
        end_boundary = sep_boundary + '--'
        body = StringIO.StringIO()
        for key, value in data.items():
            # handle multiple entries for the same name
            if type(value) != type([]):
                value = [value]
            for value in value:
                if type(value) is tuple:
                    fn = ';filename="%s"' % value[0].encode('utf-8')
                    value = value[1]
                else:
                    fn = ""
                value = str(value)
                body.write(sep_boundary)
                body.write('\nContent-Disposition: form-data; name="%s"'%key)
                body.write(fn)
                body.write("\n\n")
                body.write(value)
                if value and value[-1] == '\r':
                    body.write('\n')  # write an extra newline (lurve Macs)
        body.write(end_boundary)
        body.write("\n")
        body = body.getvalue()

        # build the Request
        # We can't use urllib2 since we need to send the Basic
        # auth right with the first request
        schema, netloc, url, params, query, fragments = \
            urlparse.urlparse(self.repository.uri)
        assert not params and not query and not fragments
        if schema == 'http':
            http = httplib.HTTPConnection(netloc)
        elif schema == 'https':
            http = httplib.HTTPSConnection(netloc)
        else:
            raise AssertionError, "unsupported schema "+schema

        data = ''
        try:
            http.connect()
            http.putrequest("POST", url)
            http.putheader('Content-type',
                           'multipart/form-data; boundary=%s'%boundary)
            http.putheader('Content-length', str(len(body)))
            http.putheader('Authorization', auth)
            http.endheaders()
            http.send(body)
        except socket.error, e:
            return

        r = http.getresponse()
        return r.status
