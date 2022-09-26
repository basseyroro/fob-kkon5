import json
from odoo import http, _
from odoo.http import request


class SupportMobileAPI(http.Controller):

    @http.route('/get/customer/list', type='http', auth='api_key')
    def getCustomerList(self, **kwargs):
        try:
            page = int(kwargs.get("page", '1'))
        except Exception as e:
            page = 1
        return json.dumps(request.env['wb.mobile.request.registration'].getCustomerList(page))

    @http.route('/get/company/list', type='http', auth='api_key')
    def getCompanyList(self, **kwargs):
        return json.dumps(request.env['wb.mobile.request.registration'].getCompanyList())

    @http.route('/get/helpdesk/team/list', type='http', auth='api_key')
    def getHelpdeskTeamList(self, **kwargs):
        try:
            page = int(kwargs.get("page", '1'))
        except Exception as e:
            page = 1
        return json.dumps(request.env['wb.mobile.request.registration'].getHelpdeskTeamList(page))

    @http.route('/get/helpdesk/list', type='http', auth='api_key')
    def getHelpdeskList(self, **kwargs):
        try:
            page = int(kwargs.get("page", '1'))
        except Exception as e:
            page = 1
        return json.dumps(request.env['wb.mobile.request.registration'].getHelpdeskList(page))

    @http.route('/get/assigned/helpdesk/list', type='http', auth='api_key')
    def getAssignedHelpdeskList(self, **kwargs):
        try:
            page = int(kwargs.get("page", '1'))
        except Exception as e:
            page = 1
        return json.dumps(request.env['wb.mobile.request.registration'].getHelpdeskList(page=page, operation="assigned_tickets"))

    @http.route('/get/team/list', type='http', auth='api_key')
    def getTeamList(self, **kwargs):
        try:
            page = int(kwargs.get("page", '1'))
        except Exception as e:
            page = 1
        return json.dumps(request.env['wb.mobile.request.registration'].getTeamList(page))

    @http.route('/get/all/tickets', type='json', auth='api_key', methods=["POST"])
    def assignTeamMember(self, **kwargs):
        request_data = json.loads(request.httprequest.data)
        fse_id = request_data.get("fse_id", 0)
        ticket_id = request_data.get("ticket_id", 0)
        if fse_id == 0 or ticket_id == 0:
            return json.dumps({"status":0, "msg":"fse or ticket id is invalid."})
        return json.dumps(request.env['wb.mobile.request.registration'].assignTeamMember(vals={'fse_id':fse_id, 'ticket_id':ticket_id}))

    @http.route('/get/all/tickets', type='http', auth='api_key')
    def getHelpdeskTicketList(self, **kwargs):
        try:
            page = int(kwargs.get("page", '1'))
        except Exception as e:
            page = 1
        if request.env.user.has_group('wb_mobile_helpdesk_integration.group_mobile_admin'):
            return json.dumps(request.env['wb.mobile.request.registration'].getHelpdeskList(page))
        else:
            return json.dumps({})

