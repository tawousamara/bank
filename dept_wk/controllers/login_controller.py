from odoo import http
from odoo.http import request
from odoo.exceptions import AccessError
from odoo.http import Response
import odoo
import json
from datetime import datetime


class CustomAuthController(http.Controller):

    @http.route('/api/v1/get_authenticated_user', auth='none', type='json', methods=['POST'], csrf=False, cors='*')
    def get_authenticated_user(self, **kw):
        request_body = request.httprequest.data.decode('utf-8')
        data = json.loads(request_body)
        session_id = data.get('session_id')
        db = data.get('db')
        uid = data.get('uid')
        if not session_id:
            return http.Response(json.dumps({'code': 401, 'error': 'Unauthorized.'}), status=400, content_type='application/json')

        session_in_come = request.session
        session_in_come.sid = session_id
        session_in_come.db = db
        session_in_come.uid = uid

        session = odoo.http.root.session_store.get(session_in_come.sid)

        if not session:
            return http.Response(json.dumps({'code': 401, 'error': 'Unauthorized.'}), status=401, content_type='application/json')

        if session.session_expiration and session.session_expiration < datetime.now():
            return http.Response(json.dumps({'code': 401, 'error': 'Session expired.'}), status=401, content_type='application/json')

        user = request.env['res.users'].sudo().search(
            [('id', '=', session.uid)])

        response_body = {
            'results': {'code': 200, 'message': 'OK'},
            'session_id': session_id,
            'user': {
                'id': user.id,
                'name': user.name,
                'login': user.login,

            }
        }

        return http.Response(json.dumps(response_body), status=200, content_type='application/json')

    @http.route('/api/v1/check_token', auth='none', type='http', methods=['POST'], csrf=False, cors='*')
    def check_token(self, **kw):
        request_body = request.httprequest.data.decode('utf-8')
        data = json.loads(request_body)
        session_id = data.get('session_id')
        uid = data.get('uid')
        db = data.get('db')

        if not session_id:
            return http.Response(json.dumps({'code': 400, 'error': 'Session ID is required.'}), status=400, content_type='application/json')
        session_in_come = request.session
        session_in_come.sid = session_id
        session_in_come.db = db
        session_in_come.uid = uid

        session = odoo.http.root.session_store.get(session_in_come.sid)

        if not session:
            return http.Response(json.dumps({'code': 401, 'error': 'Unauthorized.'}), status=401, content_type='application/json')

        if session.session_expiration and session.session_expiration < datetime.now():
            return http.Response(json.dumps({'code': 401, 'error': 'Session expired.'}), status=401, content_type='application/json')
        response_body = {
            'results': {'code': 200, 'message': 'OK'},
            'session_id': session_id,
        }
        return http.Response(json.dumps(response_body), status=200, content_type='application/json')

    @http.route('/api/v1/authenticate', auth='none', type='http', methods=['POST'], csrf=False, cors='*')
    def authenticate(self, **kw):
        request_body = request.httprequest.data.decode('utf-8')
        data = json.loads(request_body)

        login = data.get('login')
        db = data.get('db')
        password = data.get('password')

        if not http.db_filter([db]):
            raise AccessError("Database not found.")
        uid = request.session.authenticate(db, login, password)
        if not uid:
            return Response(json.dumps({'code': 401, 'error': 'Unauthorized.'}), status=401, content_type='application/json')

        odoo.http.root.session_store.save(request.session)
        response_body = {
            'results': {'code': 200, 'message': 'OK'},
            'uid': uid,
            'session_id': request.session.sid,
        }

        return Response(json.dumps(response_body), status=200, content_type='application/json')

    @http.route('/web/session/authenticate', type='http', auth="none", csrf=False, methods=['OPTIONS'])
    def authenticate_options(self, **kwargs):
        response = Response(status=200)
        return response

    @http.route('/test', type='http', auth="none", csrf=False, methods=['GET'])
    def test(self, **kwargs):
        return 'TEST'
