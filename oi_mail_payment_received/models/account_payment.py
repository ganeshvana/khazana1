# -*- coding: utf-8 -*-

from odoo import models, fields
from odoo.http import request

class AccountPayment(models.Model):
    _inherit="account.payment"

    def action_post(self): 
        res = super(AccountPayment,self).action_post()

        template_id = self.env.ref('oi_mail_payment_received.payment_validated')
        if template_id:
            if request.env['ir.config_parameter'].sudo().get_param('payment_mail_notify'):
                for payment in self:
                    print ("ttttttttttttttt",template_id)
                    if payment.partner_type == 'customer':
                        print ("oooooooooooooooooooooooooooo")
                            # print ("ggggggggg")
                        template_id.send_mail(payment.id,force_send=True)
                        # template_id.with_context(local_context).send_mail(payment['id'], force_send=True)
                        
        return res
