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

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for line in self.order_line:
            if not line.product_id.bom_ids:
                raise UserError(_('There is no BOM attached for the product.'))
        return res
        
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
            

