from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    payment_detail_ids = fields.One2many('payment.details', 'sale_order_id',"Payment Details")
    crm_stage_id = fields.Many2one('crm.stage', "CRM Stage")
    reserved = fields.Boolean("Reserved")
            
    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        res.state = 'draft'
        if res.payment_term_id:
            payterm_vals = []
            if res.payment_detail_ids:
                for pay in res.payment_detail_ids:
                    pay.sudo().unlink()
            for line in res.payment_term_id.line_ids:
                payterm_vals.append(Command.create({
                        'payment_term_id': res.payment_term_id.id,
                        'payment_term_line_id': line.id,
                    }))
            res.update({'payment_detail_ids': payterm_vals})
        # if res.website_id:
            # res.website_id.sale_order_id = False
            # res.website_id.crm_id = False
            # lead = self.env['crm.lead'].search([('type','=','opportunity')], order='id desc', limit=1)
            # if lead:
            #     res.opportunity_id = lead.id
            #     res.partner_id = lead.partner_id.id
        return res
    
    def write(self, vals):
        result = super(SaleOrder, self).write(vals)
        res = self
        if 'payment_term_id' in vals:
            if res.payment_term_id:
                payterm_vals = []
                if res.payment_detail_ids:
                    for pay in res.payment_detail_ids:
                        pay.sudo().unlink()
                for line in res.payment_term_id.line_ids:
                    payterm_vals.append(Command.create({
                            'payment_term_id': res.payment_term_id.id,
                            'payment_term_line_id': line.id,
                        }))
                res.update({'payment_detail_ids': payterm_vals})
        if 'crm_stage_id' in vals:
            if res.crm_stage_id:
                res.opportunity_id.stage_id = res.crm_stage_id.id
        if 'opportunity_id' in vals:
            if res.opportunity_id:
                res.partner_id = res.opportunity_id.partner_id.id
        # if res.team_id.name == 'Website':
            # res.partner_id = res.opportunity_id.partner_id.id
        return result
    
    def open_cart_detail(self):
        self.website_id.sale_order_id = self.id
        self.action_draft()
        baseurl = self.env.company.get_base_url() + '/shop/cart?access_token=' + self.access_token
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': baseurl,
            'target': 'new',
        }
        
    def unreserve_delivery(self):
        picking_ids = self.picking_ids.filtered(lambda m: m.state == 'assigned')
        for picking in picking_ids:
            picking.move_lines._do_unreserve()
            picking.package_level_ids.filtered(lambda p: not p.move_ids).unlink()
        self.action_cancel()
        self.action_draft()
        self.reserved = False
    
    def reserve_delivery(self):
        picking_ids = self.picking_ids.filtered(lambda m: m.state == 'confirmed')
        for picking in picking_ids:
            picking.action_assign()
        self.action_confirm()
        readypicking_ids = self.picking_ids.filtered(lambda m: m.state == 'assigned')
        if readypicking_ids:
            self.reserved = True
            # picking.filtered(lambda picking: picking.state == 'draft').action_confirm()
            # moves = picking.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
            # if not moves:
            #     raise UserError(_('Nothing to check the availability for.'))
            # # If a package level is done when confirmed its location can be different than where it will be reserved.
            # # So we remove the move lines created when confirmed to set quantity done to the new reserved ones.
            # package_level_done = self.mapped('package_level_ids').filtered(lambda pl: pl.is_done and pl.state == 'confirmed')
            # package_level_done.write({'is_done': False})
            # moves._action_assign()
            # package_level_done.write({'is_done': True})
            #
            # return True
        
    def reserve(self):
        return True
    
class PaymentDetails(models.Model):
    _name = 'payment.details'
    _description = 'Payment Details'
    
    sale_order_id = fields.Many2one('sale.order', "Sale Order")
    purchase_order_id = fields.Many2one('purchase.order', "Purchase Order")
    payment_term_id = fields.Many2one('account.payment.term', "Payment Term")
    payment_term_line_id = fields.Many2one('account.payment.term.line', "Milestone")
    payment_ids = fields.Many2many('account.payment', 'payment_sale_rel', 'pay_id', 'sale_id', "Payment")
    currency_id = fields.Many2one(related='sale_order_id.currency_id', string="Currency")
    payment_amount = fields.Monetary("Payment Amount")
    actual_amount = fields.Monetary("Actual Amount", compute='compute_actual_amount', store=True)
    balance_amount = fields.Monetary("Balance Amount", compute='compute_balance_amount', store=True)
    amount_total = fields.Monetary(related='sale_order_id.amount_total', store=True)
    
    @api.depends('amount_total', 'payment_term_line_id', 'payment_term_line_id.value_amount')
    def compute_actual_amount(self):
        total_percent = 0.0
        for rec in self:
            if rec.payment_term_line_id:
                if rec.payment_term_line_id.value == 'percent':
                    total_percent += rec.payment_term_line_id.value_amount
        for rec in self:            
            if rec.payment_term_line_id:
                if rec.payment_term_line_id.value == 'percent' and rec.payment_term_line_id.value_amount > 0.0:
                    rec.actual_amount = rec.amount_total * (rec.payment_term_line_id.value_amount / 100)
                if rec.payment_term_line_id.value == 'balance':
                    rec.actual_amount = rec.amount_total - (rec.amount_total * (total_percent / 100))
                    
    @api.depends('payment_amount', 'actual_amount', 'payment_term_line_id.value_amount')
    def compute_balance_amount(self):
        for rec in self:
            rec.balance_amount = rec.actual_amount - rec.payment_amount
    
class Payterm(models.Model):
    _inherit = "account.payment.term.line"    
    
    def name_get(self):
        result = []
        string = ''
        for line in self:
            if line.value:
                if line.value == 'balance':
                    string = 'Balance'
                if line.value == 'percent':
                    string = str(line.value_amount) + ' Percentage'                    
                if line.value == 'fixed':
                    string = str(line.value_amount) + ' Fixed'  
                name =  string
            else:
                name =  'Payment Term Line'
            result.append((line.id, name))
        return result
    
