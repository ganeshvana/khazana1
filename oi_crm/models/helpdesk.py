from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError


class Helpdesk(models.Model):
    _inherit = 'helpdesk.ticket'

    deadline = fields.Date('Due Date')
    
class project(models.Model):
    _inherit = 'project.project'    
    
    @api.model
    def create(self, vals):
        res = super(project, self).create(vals) 
        if res.sale_order_id:
            name = res.name + ' ' +res.sale_order_id.partner_id.name
        if res.message_follower_ids:
            for line in res.message_follower_ids:
                if line.partner_id == res.partner_id:
                    line.sudo().unlink()
        return res
    
    
    def action_view_survey_answer(self):
        self.ensure_one()
        view_form_id = self.env.ref('survey.survey_user_input_view_form').id
        tree_form_id = self.env.ref('survey.survey_user_input_view_tree').id
        answer = []
        crm = self.sale_order_id.opportunity_id
        if crm:
            answer = self.env['survey.user_input'].search([('crm_id', '=', crm.id)])
            action = {
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', answer.ids)],
                'view_mode': 'form',
                'name': _('Answer'),
                'res_model': 'survey.user_input',
            }
            if len(answer) == 1:
                action.update({'views': [(view_form_id, 'form')], 'res_id': answer[0]})
            else:
                action['views'] = [(tree_form_id, 'tree'), (view_form_id, 'form')]
            return action
        else:
            raise ValidationError(_('No Need Analysis found.'))
        
    def write(self, vals):
        res = super(project, self).write(vals) 
        for res in self:            
            if res.message_follower_ids:
                for line in res.message_follower_ids:
                    if line.partner_id == res.partner_id:
                        line.sudo().unlink()
        return res
    
class Task(models.Model):
    _inherit = 'project.task'
    
    mom = fields.Boolean("MoM Required")
    survey = fields.Boolean("Survey Required")
    survey_id = fields.Many2one('survey.survey', "Survey")
    
    def action_view_survey_answer(self):
        self.ensure_one()
        view_form_id = self.env.ref('survey.survey_user_input_view_form').id
        tree_form_id = self.env.ref('survey.survey_user_input_view_tree').id
        answer = []
        crm = self.project_id.sale_order_id.opportunity_id
        if crm:
            answer = self.env['survey.user_input'].search([('crm_id', '=', crm.id)])
            action = {
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', answer.ids)],
                'view_mode': 'form',
                'name': _('Answer'),
                'res_model': 'survey.user_input',
            }
            if len(answer) == 1:
                action.update({'views': [(view_form_id, 'form')], 'res_id': answer[0]})
            else:
                action['views'] = [(tree_form_id, 'tree'), (view_form_id, 'form')]
            return action
        else:
            raise ValidationError(_('No Need Analysis found.'))
    
    @api.model
    def create(self, vals):
        res = super(Task, self).create(vals) 
        if res.mom == True:
            if not res.attachment_ids:
                raise ValidationError(_('MoM is required for this Task. Attach MoM.!!'))
        if res.message_follower_ids:
            for line in res.message_follower_ids:
                if line.partner_id == res.partner_id:
                    line.sudo().unlink()
        if res.survey == True:
            for employee in res.user_ids:
                mail_template_id = self.env.ref('oi_crm.mail_template_survey_assigned')
                template = self.env['mail.template'].browse(mail_template_id.id)
                template.email_to = employee.email
                self.env['mail.template'].browse(mail_template_id.id).send_mail(res.id, force_send=True)
        return res
    
    def write(self, vals):
        res = super(Task, self).write(vals) 
        for res in self:
            if 'survey_id' in vals:                
                if res.survey == True:
                    for employee in res.user_ids:
                        mail_template_id = self.env.ref('oi_crm.mail_template_survey_assigned')
                        template = self.env['mail.template'].browse(mail_template_id.id)
                        template.email_to = employee.email
                        self.env['mail.template'].browse(mail_template_id.id).send_mail(res.id, force_send=True)
            if 'mom' in vals:     
                if res.mom == True:
                    if not res.attachment_ids:
                        raise ValidationError(_('MoM is required for this Task. Attach MoM.!!'))
            if res.message_follower_ids:
                for line in res.message_follower_ids:
                    if line.partner_id == res.partner_id:
                        line.sudo().unlink()
        return res
    
#     @api.model
#     def write(self, vals):
#         res = super(Task, self).write(vals) 
#         if 'stage_id' in vals:
#             if self.stage_id.is_closed:
#                 if self.survey_id.state
#         return res
    
    
    
    
    