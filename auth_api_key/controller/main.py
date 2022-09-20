import json
from odoo import http, _
from odoo.http import request


class SupportAPI(http.Controller):

    @http.route('/test/connection', type='http', auth='public')
    def rest_api_test_connection(self, **kwargs):
        return json.dumps({"status":"Successfully Connected!"})

    @http.route('/user/connection/auth', type='json', auth='public', methods=['POST'])
    def rest_api_auth_user_connection(self, **kwargs):
        user_auth_obj = request.env['auth.api.key']
        request_data = json.loads(request.httprequest.data)
        response_status = {"status":0, "msg":"Invalid credential", "token":""}
        if not request_data:
            return response_status
        if response_status.get("user", None) or response_status.get("psw", None):
            response_status["msg"] = "Missing credentials information."
            return response_status
        if request.session and not request.session.get("db"):
            response_status["msg"] = "Single service should be rune."
            return response_status
        if request.session and request.session.get("db"):
            user = None
            try:
                user = request.session.authenticate(request.session.get("db"),
                                                    request_data.get("user", ""),
                                                    request_data.get("psw", ""))
            except Exception as e:
                response_status["msg"] = "Invalid auth credential!"
                return response_status
            if user and type(user) == type(1):
                # try:
                    user_token = user_auth_obj.sudo().search([('user_id','=',user)])
                    if user_token:
                        response_status["msg"] = "Successfully Login!"
                        response_status["token"] = user_token.key
                        response_status["status"] = 1
                    else:
                        user_token = user_auth_obj.create_new_key({'user_id': user})
                        response_status["msg"] = "Successfully Login!"
                        response_status["token"] = user_token
                        response_status["status"] = 1
                    return response_status
                # except Exception as e:
                #     response_status["msg"] = "Please approach administrator to create auto token!"
                #     return response_status
        response_status["msg"] = "Requested service not found!"
        return response_status
