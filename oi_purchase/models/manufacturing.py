from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError

from collections import defaultdict


class Manufacturing(models.Model):
    _inherit = 'mrp.production'
    
    def send_date_of_issue(self):
        mrp = self.env['mrp.production'].search([('state', 'in', ['draft', 'confirmed', 'progress', 'to_close'])])
        if mrp:            
            for mo in mrp:
                if mo.date_planned_start.date() +  timedelta(days=-1) >= fields.Date.today():  
                    mail_template_id = self.env.ref('oi_purchase.mail_template_send_date_of_issue_reminder')
                    self.env['mail.template'].browse(mail_template_id.id).send_mail(mo.id, force_send=True) 
    
    
    