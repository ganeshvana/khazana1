from odoo import models, fields, api, _
from odoo.http import request


# class Website(models.Model):
#     _inherit = 'website'
#
#     sale_order_id = fields.Many2one('sale.order', "Sale Order")
#
#     def sale_get_order(self, force_create=False, code=None, update_pricelist=False, force_pricelist=False):
#         """ Return the current sales order after mofications specified by params.
#         :param bool force_create: Create sales order if not already existing
#         :param str code: Code to force a pricelist (promo code)
#                          If empty, it's a special case to reset the pricelist with the first available else the default.
#         :param bool update_pricelist: Force to recompute all the lines from sales order to adapt the price with the current pricelist.
#         :param int force_pricelist: pricelist_id - if set,  we change the pricelist with this one
#         :returns: browse record for the current sales order
#         """
#         self.ensure_one()
#         partner = self.env.user.partner_id
#         sale_order_id = request.session.get('sale_order_id')
#         check_fpos = False
#         if not sale_order_id and not self.env.user._is_public():
#             last_order = partner.last_website_so_id
#             if last_order:
#                 available_pricelists = self.get_pricelist_available()
#                 # Do not reload the cart of this user last visit if the cart uses a pricelist no longer available.
#                 sale_order_id = last_order.pricelist_id in available_pricelists and last_order.id
#                 check_fpos = True
#
#         # Test validity of the sale_order_id
#         sale_order = self.env['sale.order'].with_company(request.website.company_id.id).sudo().browse(sale_order_id).exists() if sale_order_id else None
#
#         # Do not reload the cart of this user last visit if the Fiscal Position has changed.
#         if check_fpos and sale_order:
#             fpos_id = (
#                 self.env['account.fiscal.position'].sudo()
#                 .with_company(sale_order.company_id.id)
#                 .get_fiscal_position(sale_order.partner_id.id, delivery_id=sale_order.partner_shipping_id.id)
#             ).id
#             if sale_order.fiscal_position_id.id != fpos_id:
#                 sale_order = None
#
#         if not (sale_order or force_create or code):
#             if request.session.get('sale_order_id'):
#                 request.session['sale_order_id'] = None
#             return self.env['sale.order']
#
#         if self.env['product.pricelist'].browse(force_pricelist).exists():
#             pricelist_id = force_pricelist
#             request.session['website_sale_current_pl'] = pricelist_id
#             update_pricelist = True
#         else:
#             pricelist_id = request.session.get('website_sale_current_pl') or self.get_current_pricelist().id
#
#         if not self._context.get('pricelist'):
#             self = self.with_context(pricelist=pricelist_id)
#
#         # cart creation was requested (either explicitly or to configure a promo code)
#         if not sale_order:
#             # TODO cache partner_id session
#             pricelist = self.env['product.pricelist'].browse(pricelist_id).sudo()
#             so_data = self._prepare_sale_order_values(partner, pricelist)
#             sale_order = self.env['sale.order'].with_company(request.website.company_id.id).with_user(SUPERUSER_ID).create(so_data)
#
#             # set fiscal position
#             if request.website.partner_id.id != partner.id:
#                 sale_order.onchange_partner_shipping_id()
#             else: # For public user, fiscal position based on geolocation
#                 country_code = request.session['geoip'].get('country_code')
#                 if country_code:
#                     country_id = request.env['res.country'].search([('code', '=', country_code)], limit=1).id
#                     sale_order.fiscal_position_id = request.env['account.fiscal.position'].sudo().with_company(request.website.company_id.id)._get_fpos_by_region(country_id)
#                 else:
#                     # if no geolocation, use the public user fp
#                     sale_order.onchange_partner_shipping_id()
#
#             request.session['sale_order_id'] = sale_order.id
#
#         # case when user emptied the cart
#         if not request.session.get('sale_order_id'):
#             request.session['sale_order_id'] = sale_order.id
#
#         # check for change of pricelist with a coupon
#         pricelist_id = pricelist_id or partner.property_product_pricelist.id
#
#         # check for change of partner_id ie after signup
#         if sale_order.partner_id.id != partner.id and request.website.partner_id.id != partner.id:
#             flag_pricelist = False
#             if pricelist_id != sale_order.pricelist_id.id:
#                 flag_pricelist = True
#             fiscal_position = sale_order.fiscal_position_id.id
#
#             # change the partner, and trigger the onchange
#             sale_order.write({'partner_id': partner.id})
#             sale_order.with_context(not_self_saleperson=True).onchange_partner_id()
#             sale_order.write({'partner_invoice_id': partner.id})
#             sale_order.onchange_partner_shipping_id() # fiscal position
#             sale_order['payment_term_id'] = self.sale_get_payment_term(partner)
#
#             # check the pricelist : update it if the pricelist is not the 'forced' one
#             values = {}
#             if sale_order.pricelist_id:
#                 if sale_order.pricelist_id.id != pricelist_id:
#                     values['pricelist_id'] = pricelist_id
#                     update_pricelist = True
#
#             # if fiscal position, update the order lines taxes
#             if sale_order.fiscal_position_id:
#                 sale_order._compute_tax_id()
#
#             # if values, then make the SO update
#             if values:
#                 sale_order.write(values)
#
#             # check if the fiscal position has changed with the partner_id update
#             recent_fiscal_position = sale_order.fiscal_position_id.id
#             # when buying a free product with public user and trying to log in, SO state is not draft
#             if (flag_pricelist or recent_fiscal_position != fiscal_position) and sale_order.state == 'draft':
#                 update_pricelist = True
#
#         if code and code != sale_order.pricelist_id.code:
#             code_pricelist = self.env['product.pricelist'].sudo().search([('code', '=', code)], limit=1)
#             if code_pricelist:
#                 pricelist_id = code_pricelist.id
#                 update_pricelist = True
#         elif code is not None and sale_order.pricelist_id.code and code != sale_order.pricelist_id.code:
#             # code is not None when user removes code and click on "Apply"
#             pricelist_id = partner.property_product_pricelist.id
#             update_pricelist = True
#
#         # update the pricelist
#         if update_pricelist:
#             request.session['website_sale_current_pl'] = pricelist_id
#             values = {'pricelist_id': pricelist_id}
#             sale_order.write(values)
#             for line in sale_order.order_line:
#                 if line.exists():
#                     sale_order._cart_update(product_id=line.product_id.id, line_id=line.id, add_qty=0)
#
#         if not sale_order:
#             sale_order = self.sale_order_id
#         print(sale_order, "sale_order=======")
#         return sale_order

class Survey(models.Model):
    _inherit = 'survey.survey'
    
    crm_id = fields.Many2one('crm.lead', "Lead")
    
class SurveyAns(models.Model):
    _inherit = 'survey.user_input'
    
    # crm_id = fields.Many2one(related='survey_id.crm_id', store=True)
    crm_id = fields.Many2one('crm.lead', "Lead")
    
    @api.model_create_multi
    def create(self, vals_list):
        result = super(SurveyAns, self).create(vals_list)
        if result.survey_id:
            if result.survey_id.crm_id:
                result.crm_id = result.survey_id.crm_id.id
        return result
    
class Lead(models.Model):
    _inherit = 'crm.lead'
    
    interested_in = fields.Selection([('loose_furniture','Loose Furniture'),('fixed_furniture','Fixed Furniture'),('full_house','Full House')], "Interested In")
    crm_team_ids = fields.Many2many('crm.team', 'team_lead_rel', 'team_id', 'lead_id', "Sale Teams")
    survey_id = fields.Many2one('survey.survey', "Need Analysis Form")
    priority = fields.Selection([('0', 'Low'),
    ('1', 'Warm'),
    ('2', 'Hot'),
    ('3', 'Very Hot'),],
         index=True,
        default='0')
    
    def need_analysis_form(self):
        survey = self.env['survey.survey'].search([('title', '=', 'Need Analysis Form')])
        if survey:
            self.survey_id = survey.id
            survey.crm_id = self.id
            survey.action_test_survey()
            return {
                'type': 'ir.actions.act_url',
                'name': "Need Analysis",
                'target': '_blank',
                'url': '/survey/test/%s' % survey.access_token,
            }
    
    def write(self, vals):
        res = super(Lead, self).write(vals)
        mail = ''
        if 'stage_id' in vals:
            mail_template_id = self.env.ref('oi_crm.mail_template_crm_stage_change')
            tempalte = self.env['mail.template'].browse(mail_template_id.id)
            for fol in self.message_partner_ids:
                if fol.email:
                    mail += fol.email + ','
            tempalte.email_to = mail
            self.env['mail.template'].browse(mail_template_id.id).send_mail(self.id, force_send=True)
        return res
    
    def action_view_project_ids(self):
        self.ensure_one()
        view_form_id = self.env.ref('project.edit_project').id
        view_kanban_id = self.env.ref('project.view_project_kanban').id
        projects = []
        for quotation in self.order_ids:
            if quotation.project_ids:
                for project in quotation.project_ids:
                    projects.append(project.id)
        action = {
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', projects)],
            'view_mode': 'kanban,form',
            'name': _('Projects'),
            'res_model': 'project.project',
        }
        if len(projects) == 1:
            action.update({'views': [(view_form_id, 'form')], 'res_id': projects[0]})
        else:
            action['views'] = [(view_kanban_id, 'kanban'), (view_form_id, 'form')]
        return action
    
    def action_view_survey_answer(self):
        self.ensure_one()
        view_form_id = self.env.ref('survey.survey_user_input_view_form').id
        tree_form_id = self.env.ref('survey.survey_user_input_view_tree').id
        answer = []
        answer = self.env['survey.user_input'].search([('crm_id', '=', self.id)])
        action = {
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', answer.ids)],
            'view_mode': 'form',
            'name': _('Answer'),
            'res_model': 'survey.user_input',
        }
        if len(answer) == 1:
            action.update({'views': [(view_form_id, 'form')], 'res_id': answer[0].id})
        else:
            action['views'] = [(tree_form_id, 'tree'), (view_form_id, 'form')]
        return action
    
    def redirect_to_website(self):
        website = self.env['website'].search([])
        if website:
            for rec in website:
                rec.sale_order_id = False
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        record_url = base_url + "/shop" 
        return {
            'name': 'Goto Website',
            'type': 'ir.actions.act_url',
            'target': 'new',
            'context': self._context,
            'url': record_url,
        }     
    
class Partner(models.Model):
    _inherit = 'res.partner'
    
    # anniversary = fields.Date("Anniversary")

    @api.model_create_multi
    def create(self, vals_list):
        result = super(Partner, self).create(vals_list)
        for res in result:
            seq = self.env['ir.sequence'].next_by_code('customer.code.seq') or '/'
            res.ref = seq
            mail_template_id = self.env.ref('oi_crm.mail_template_customer_creation')
            self.env['mail.template'].browse(mail_template_id.id).send_mail(res.id, force_send=True)
        return result
    
    
    partner_name = fields.Char('Partner Name', compute='compute_partner_name', store=True)
    
    @api.depends('display_name', 'name')
    def compute_partner_name(self):
        for rec in self:
            if rec.name:
                rec.partner_name = rec.name.replace(' ', '')
        
    
    
    
    
    