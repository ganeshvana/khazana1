from odoo import api, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    credit_limit_checked = fields.Boolean("Credit Limit Override", default=False)
    credit_limit = fields.Integer(related='partner_id.credit_limit')
    remaining_creditlimit = fields.Float(related='partner_id.remaining_creditlimit')
    
    def open_payment(self):
        view = self.env.ref('account.view_account_payment_form')
        self = self.with_context(default_partner_id = self.partner_id.id,default_sale_order_id = self.id,
                                default_payment_type = 'inbound', default_partner_type = 'customer',
                                default_move_journal_types = ('bank', 'cash')  )
        
        return {
            'name': 'Payments',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.payment',
            'views': [(view.id, 'form')],
            'target': 'current',
            'context': self._context,
        }

    # def action_confirm(self):
    #     res = super(SaleOrder, self).action_confirm()
    #     invoice_total = 0
    #     payment_total = 0
    #     exceed_amount = 0
    #     remaining_creditlimit = 0.0
    #     to_invoice_price = 0.0
    #     sale_total = invoice_total = 0.0
    #     due = 0
    #     if self.partner_id.credit_limit_applicable:
    #         partner_due = self.partner_id.total_due            
    #         sale_amount = self.amount_total
    #         if self.credit_limit_checked == False:
    #             if self.partner_id.company_type == 'company':
    #                 to_invoice_sale =  self.env['sale.order'].search([('partner_id', '=', self.partner_id.id),('invoice_status', '=', 'to invoice'),('state', '=', 'sale'),('id','!=', self.id)])                    
    #                 for sale in to_invoice_sale:
    #                     sale_total += sale.amount_total
    #                     for invoice in sale.invoice_ids:
    #                         if invoice.payment_state == 'in_payment':
    #                             invoice_total += invoice
    #                 to_invoice_price = sale_total - invoice_total
    #                 if (to_invoice_price + self.partner_id.total_due) == 0.0:
    #                     self.partner_id.used_credit_limit = 0.0
    #                 else:
    #                     self.partner_id.used_credit_limit = (to_invoice_price + self.partner_id.total_due)
    #                 remaining_creditlimit = (self.partner_id.credit_limit - self.partner_id.used_credit_limit)
    #                 if remaining_creditlimit < sale_amount:
    #                     raise UserError(_('Credit Limit exceeded for the customer.'))
    #                 else:
    #                     return res
    #             else:
    #                     return res
    #             if rec.company_type == 'person':
    #                 individual_unpaid = 0.0
    #                 invoice = self.env['account.move'].search([('payment_state', 'in_payment'),('move_type', '=', 'out_invoice'),('partner_id', '=', rec.id)])
    #                 if invoice:
    #                     for inv in invoice:
    #                         individual_unpaid += inv.amount_residual
    #                 to_invoice_sale =  self.env['sale.order'].search([('partner_id', '=', rec.id),('invoice_status', '=', 'to invoice'),('state', '=', 'sale'),('id','!=', self.id)])                    
    #                 for sale in to_invoice_sale:
    #                     sale_total += sale.amount_total
    #                 if (individual_unpaid + sale_total) == 0.0:
    #                     rec.used_credit_limit = 0.0 
    #                 else:
    #                     rec.used_credit_limit = (individual_unpaid + sale_total)
    #                     rec.remaining_creditlimit = (rec.credit_limit - rec.used_credit_limit)
    #             else:
    #                     return res
    #         else:
    #             return res
    #     else:
    #         return res
       
        
class Picking(models.Model):
    _inherit = "stock.picking"

    credit_limit_checked = fields.Boolean("Credit Limit Override", default=False)

    def button_validate(self):
        res = super(Picking, self).button_validate()
        invoice_total = 0
        payment_total = 0
        exceed_amount = 0
        remaining_creditlimit = 0.0
        to_invoice_price = 0.0
        sale_total = invoice_total = 0.0
        due = 0
        if self.partner_id.credit_limit_applicable:
            partner_due = self.partner_id.total_due 
            if self.sale_id:           
                sale_amount = self.sale_id.amount_total
            else:
                sale_amount = 0.0
            if self.credit_limit_checked == False:                    
                if sale_amount > self.partner_id.remaining_creditlimit:
                    raise UserError(_('Credit Limit exceeded for the customer.'))
                else:
                    return res
                
            else:
                return res
        else:
            return res
            

