from flask import jsonify


class InvalidUsage(Exception):

    def __init__(self, message, status_code):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code

    def generate_message(self):
        resp = jsonify({'error_message': self.message, 'status_code': self.status_code})
        resp.status_code = self.status_code
        return resp
