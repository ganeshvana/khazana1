from odoo import api, fields, models, _
class res_partner(models.Model):
    _inherit = "res.partner"

    credit_limit = fields.Integer(string="Credit Limit")
    credit_limit_applicable = fields.Boolean("Credit Limit Applicable", default=True)
    used_credit_limit = fields.Float('Used Credit Limit', compute='compute_credit_limit')    
    remaining_creditlimit = fields.Float('Remaining Credit Limit', compute='compute_credit_limit')

                
    @api.depends('credit_limit', 'total_due', 'total_invoiced', 'sale_order_ids', 'sale_order_ids.invoice_ids', 'sale_order_ids.invoice_ids.state')
    def compute_credit_limit(self):
        child_cl = due = 0.0
        to_invoice_price = 0.0
        sale_total = invoice_total = 0.0
        for rec in self:
            to_invoice_sale =  self.env['sale.order'].search([('partner_id', '=', rec.id),('invoice_status', '=', 'to invoice'),('state', '=', 'sale')])                    
            for sale in to_invoice_sale:
                sale_total += sale.amount_total
                for invoice in sale.invoice_ids:
                    if invoice.payment_state == 'in_payment':
                        invoice_total += invoice
            to_invoice_price = sale_total - invoice_total
            if (to_invoice_price + rec.total_due) == 0.0:
                rec.used_credit_limit = 0.0
            else:
                rec.used_credit_limit = (to_invoice_price + rec.total_due)
            rec.remaining_creditlimit = (rec.credit_limit - rec.used_credit_limit)
                # if rec.company_type == 'person':
                #     individual_unpaid = 0.0
                #     invoice = self.env['account.move'].search([('payment_state', '=','in_payment'),('move_type', '=', 'out_invoice'),('partner_id', '=', rec.id)])
                #     if invoice:
                #         for inv in invoice:
                #             individual_unpaid += inv.amount_residual
                #     to_invoice_sale =  self.env['sale.order'].search([('partner_id', '=', rec.id),('invoice_status', '=', 'to invoice'),('state', '=', 'sale')])                    
                #     for sale in to_invoice_sale:
                #         sale_total += sale.amount_total
                #     if (individual_unpaid + sale_total) == 0.0:
                #         rec.used_credit_limit = 0.0 
                #     else:
                #         rec.used_credit_limit = (individual_unpaid + sale_total)
                #     rec.remaining_creditlimit = (rec.credit_limit - rec.used_credit_limit)    
                
            # if rec.child_ids:  
            #     due = rec.total_due
            #     if due == 0.0:
            #         rec.used_credit_limit = 0.0
            #     else:
            #         rec.used_credit_limit = due
            #     rec.remaining_creditlimit = rec.credit_limit - rec.used_credit_limit

