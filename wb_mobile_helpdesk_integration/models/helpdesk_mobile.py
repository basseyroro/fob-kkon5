import logging
import json
# import requests
from odoo import api, fields, models, _

_logger = logging.getLogger(__name__)


class HelpdeskStages(models.Model):
    _inherit = "helpdesk.stage"

    display_in_mobile_app = fields.Boolean("Is display in mobile application?", default=False, copy=False)
    update_from_mobile_app = fields.Boolean("Update from mobile application?", default=False, copy=False)


class WBMobileRequestRegistration(models.Model):
    _name = "wb.mobile.request.registration"
    _description = "Mobile Helpdesk Request Registratiton List"

    name = fields.Selection([('fse','FSE')])
    request = fields.Text("Request")
    response = fields.Text("Response")
    state = fields.Selection([('draft', 'Draft'),
                              ('invalid', 'Invalid'),
                              ('done','Done')], default='draft')
    active = fields.Boolean("Active", default=True)
    process_message = fields.Char("Proceed Message")

    def getCustomerList(self, page=0):
        customer_list = []
        offset_limit = 0
        for offset in range(page):
            if offset > 0:
                offset_limit += 50
        total_records = self.env['res.partner'].sudo().search([], order="id")
        actual_records = total_records[offset_limit:50]
        # offset = offset_limit, limit = 50,
        for prd in actual_records:
            customer_list.append({'name':prd.display_name, 'id':prd.id, 'customer_id': prd.x_studio_customer_id or '',
                            'first_name': prd.x_studio_first_name or '',
                            'last_name': prd.x_studio_last_name or '',
                            'country_id': prd.country_id.id or False,
                            'country_name': prd.country_id.name or '',
                            'state_id': prd.state_id.id or False,
                            'state_name': prd.state_id.name or '',
                            'mobile': prd.mobile or '',
                            'phone': prd.phone or '',
                            'street': prd.street or '',
                            'street2': prd.street2 or '',
                            'zip': prd.zip or '',
                            'city': prd.city or '',
                            'email': prd.email or '',
                            'total_records': len(total_records)
                            })
        return customer_list

    def getCompanyList(self):
        return [{'name':prd.name, 'id':prd.id} for prd in self.env['res.company'].sudo().search([])]

    def getHelpdeskTeamList(self, page=0):
        obj_list = []
        offset_limit = 0
        for offset in range(page):
            if offset > 0:
                offset_limit += 50
        for prd in self.env['helpdesk.team'].sudo().search([],offset=offset_limit, limit=50, order="id"):
            obj_list.append({'name': prd.name, 'id': prd.id, 'company_id': prd.company_id.id})
        return obj_list

    def getHelpdeskList(self, page=0, operation="pending_tickets"):
        helpdesk_list = []
        offset_limit = 0
        for offset in range(page):
            if offset > 0:
                offset_limit += 50
        domain = [('stage_id.display_in_mobile_app', '=', True),('stage_id.update_from_mobile_app', '=', True)]
        if operation == "assigned_tickets":
            domain = [('stage_id.display_in_mobile_app', '=', True),('x_studio_fse','=',self.env.user.id), ('stage_id.update_from_mobile_app', '=', False)]
        for prd in self.env['helpdesk.ticket'].search(domain,
                                                      offset=offset_limit, limit=50, order="id"):
            customer_detail = prd.partner_id
            area_manager_detail = prd.x_studio_many2one_field_F3tVh
            helpdesk_list.append({'name': prd.name,
                 'id': prd.id,
                 'helpdesk_number':prd.x_studio_helpdesk_id or '',
                 'helpdesk_team_id': prd.team_id.id,
                 'helpdesk_team_name': prd.team_id.name,
                 'sale_id': prd.sudo().x_studio_many2one_field_fD8Y4.name,
                 'assigned_user_id': prd.user_id.id,
                 'assigned_user_name': prd.user_id.name,
                 'ticket_type_id': prd.ticket_type_id.id,
                 'ticket_type_name': prd.ticket_type_id.name,
                 'created_by': prd.create_uid.name,
                 'created_date': "{}".format(prd.create_date),
                 'customer_id': customer_detail.id,
                 'customer_name': customer_detail.name,
                  'customer_customer_id': customer_detail.x_studio_customer_id or '',
                  'customer_first_name': customer_detail.x_studio_first_name or '',
                  'customer_last_name': customer_detail.x_studio_last_name or '',
                  'customer_country_id': customer_detail.country_id.id or False,
                  'customer_country_name': customer_detail.country_id.name or '',
                  'customer_state_id': customer_detail.state_id.id or False,
                  'customer_state_name': customer_detail.state_id.name or '',
                  'customer_mobile': customer_detail.mobile or '',
                  'customer_phone': customer_detail.phone or '',
                  'customer_street': customer_detail.street or '',
                  'customer_street2': customer_detail.street2 or '',
                  'customer_zip': customer_detail.zip or '',
                  'customer_city': customer_detail.city or '',
                  'customer_email': customer_detail.email or '',
                 'area_manager_id': area_manager_detail.id,
                 'area_manager_name': area_manager_detail.name,
                  'area_manager_country_name': area_manager_detail.partner_id.country_id.name or '',
                  'area_manager_state_name': area_manager_detail.partner_id.state_id.name or '',
                  'area_manager_mobile': area_manager_detail.partner_id.mobile or '',
                  'area_manager_phone': area_manager_detail.partner_id.phone or '',
                  'area_manager_street': area_manager_detail.partner_id.street or '',
                  'area_manager_street2': area_manager_detail.partner_id.street2 or '',
                  'area_manager_zip': area_manager_detail.partner_id.zip or '',
                  'area_manager_city': area_manager_detail.partner_id.city or '',
                  'area_manager_email': area_manager_detail.partner_id.email or '',
                 'fse_id': prd.x_studio_fse.id,
                 'fse_name': prd.x_studio_fse.name,
                 'company_id': prd.company_id.id,
                 'company_name': prd.company_id.name,
                 'stage_id': prd.stage_id.id,
                 'stage_name': prd.stage_id.name,
                 })
        return helpdesk_list

    def getHelpdeskTicketList(self, page=0):
        helpdesk_list = []
        offset_limit = 0
        for offset in range(page):
            if offset > 0:
                offset_limit += 50
        domain = [('stage_id.display_in_mobile_app', '=', True)]
        for prd in self.env['helpdesk.ticket'].sudo().search(domain,
                                                      offset=offset_limit,
                                                      limit=50, order="id"):
            customer_detail = prd.partner_id
            area_manager_detail = prd.x_studio_many2one_field_F3tVh
            helpdesk_list.append({'name': prd.name,
                 'id': prd.id,
                 'helpdesk_number':prd.x_studio_helpdesk_id or '',
                 'helpdesk_team_id': prd.team_id.id,
                 'helpdesk_team_name': prd.team_id.name,
                 'sale_id': prd.sudo().x_studio_many2one_field_fD8Y4.name,
                 'assigned_user_id': prd.user_id.id,
                 'assigned_user_name': prd.user_id.name,
                 'ticket_type_id': prd.ticket_type_id.id,
                 'ticket_type_name': prd.ticket_type_id.name,
                 'created_by': prd.create_uid.name,
                 'created_date': "{}".format(prd.create_date),
                 'customer_id': customer_detail.id,
                 'customer_name': customer_detail.name,
                  'customer_customer_id': customer_detail.x_studio_customer_id or '',
                  'customer_first_name': customer_detail.x_studio_first_name or '',
                  'customer_last_name': customer_detail.x_studio_last_name or '',
                  'customer_country_id': customer_detail.country_id.id or False,
                  'customer_country_name': customer_detail.country_id.name or '',
                  'customer_state_id': customer_detail.state_id.id or False,
                  'customer_state_name': customer_detail.state_id.name or '',
                  'customer_mobile': customer_detail.mobile or '',
                  'customer_phone': customer_detail.phone or '',
                  'customer_street': customer_detail.street or '',
                  'customer_street2': customer_detail.street2 or '',
                  'customer_zip': customer_detail.zip or '',
                  'customer_city': customer_detail.city or '',
                  'customer_email': customer_detail.email or '',
                 'area_manager_id': area_manager_detail.id,
                 'area_manager_name': area_manager_detail.name,
                  'area_manager_country_name': area_manager_detail.partner_id.country_id.name or '',
                  'area_manager_state_name': area_manager_detail.partner_id.state_id.name or '',
                  'area_manager_mobile': area_manager_detail.partner_id.mobile or '',
                  'area_manager_phone': area_manager_detail.partner_id.phone or '',
                  'area_manager_street': area_manager_detail.partner_id.street or '',
                  'area_manager_street2': area_manager_detail.partner_id.street2 or '',
                  'area_manager_zip': area_manager_detail.partner_id.zip or '',
                  'area_manager_city': area_manager_detail.partner_id.city or '',
                  'area_manager_email': area_manager_detail.partner_id.email or '',
                 'fse_id': prd.x_studio_fse.id,
                 'fse_name': prd.x_studio_fse.name,
                 'company_id': prd.company_id.id,
                 'company_name': prd.company_id.name,
                 'stage_id': prd.stage_id.id,
                 'stage_name': prd.stage_id.name,
                 })
        return helpdesk_list

    def getProductList(self):
        return json.dumps([{'id':prd.id, 'name':prd.name} for prd in
                self.env['product.product'].search([('sale_ok', '=', True)])])

    def getTeamList(self, page=0):
        helpdesk_list = []
        offset_limit = 0
        for offset in range(page):
            if offset > 0:
                offset_limit += 50
        for prd in self.env['res.users'].sudo().search([('share', '=', False)],
                                                       offset=offset_limit, limit=50, order="id"):
            user_detail = prd.partner_id
            helpdesk_list.append({'id': prd.id, 'name': prd.name, 'country_name': user_detail.country_id.name or '',
                                    'state_name': user_detail.state_id.name or '',
                                    'mobile': user_detail.mobile or '',
                                    'phone': user_detail.phone or '',
                                    'street': user_detail.street or '',
                                    'street2': user_detail.street2 or '',
                                    'zip': user_detail.zip or '',
                                    'city': user_detail.city or '',
                                    'email': user_detail.email or '',})
        return helpdesk_list

    def assignTeamMember(self, vals={}):
        # vals = {'fse_id':1, 'ticket_id':1}
        key_vals = ['fse_id', 'ticket_id']
        response_data = {"status":0, "msg":"Record not updated."}
        if not vals:
            response_data['msg'] = "Getting blank payload."
            return json.dumps(response_data)
        if type(vals) != type({}):
            response_data['msg'] = "Payload should be in dictionary format."
            return json.dumps(response_data)
        for rkey in key_vals:
            if rkey not in vals or not vals.get(rkey):
                response_data['msg'] = "{} key is not found or its a blank".format(rkey)
                return json.dumps(response_data)
        fse_id = self.env['res.users'].sudo().search([('id', '=', vals.get("fse_id"))])
        if not fse_id:
            response_data['msg'] = "FSE_ID key value is not found."
            return json.dumps(response_data)
        ticket_id = self.env['helpdesk.ticket'].sudo().search([('id', '=', vals.get("ticket_id"))])
        if not ticket_id:
            response_data['msg'] = "TICKET_ID key value is not found."
            return json.dumps(response_data)
        if not ticket_id.stage_id.update_from_mobile_app:
            response_data['msg'] = "This ticket is not in correct state. Pls refresh the records."
            return json.dumps(response_data)
        ticket_id.write({"x_studio_fse":vals.get("fse_id")})
        response_data['msg'] = "FSE user successfully updated in this ticket."
        response_data['status'] = 1
        return response_data
