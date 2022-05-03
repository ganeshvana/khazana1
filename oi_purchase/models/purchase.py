from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError

from collections import defaultdict
import xmlrpc.client


class Purchase(models.Model):
    _inherit = 'purchase.order'
    
    purchase_order_type_id = fields.Many2one('purchase.order.type', "Order Type")
    type = fields.Selection([('appliance', 'Appliance/CT'), ('imports', 'Imports'), ('domestic','Domestic'),('consumbles','Consumbles')])
    
    @api.onchange('purchase_order_type_id')
    def onchange_purchase_order_type_id(self):
        if self.purchase_order_type_id:
            self.type = self.purchase_order_type_id.type
    
    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        # Ensures default picking type and currency are taken from the right company.
        self_comp = self.with_company(company_id)
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            if 'type' in vals:
                if vals['type'] == 'appliance':
                    vals['name'] = self_comp.env['ir.sequence'].next_by_code('appliance.purchase', sequence_date=seq_date) or '/'
                if vals['type'] == 'imports':
                    vals['name'] = self.env['ir.sequence'].next_by_code('imports.purchase', sequence_date=seq_date) or '/'
                if vals['type'] == 'domestic':
                    vals['name'] = self.env['ir.sequence'].next_by_code('domestic.purchase', sequence_date=seq_date) or '/'
                if vals['type'] == 'consumbles':
                    vals['name'] = self.env['ir.sequence'].next_by_code('consumbles.purchase', sequence_date=seq_date) or '/'
                if vals['type'] not in ['consumbles','appliance', 'imports', 'domestic']:
                    vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order', sequence_date=seq_date) or '/'
        vals, partner_vals = self._write_partner_values(vals)
        res = super(Purchase, self_comp).create(vals)
        if partner_vals:
            res.sudo().write(partner_vals)  # Because the purchase user doesn't have write on `res.partner`
        return res
    
    def button_confirm(self):
        res = super(Purchase, self).button_confirm()
        # url = 'localhost:7069'
        # common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        # common.version()
        
        if self.partner_id.name == 'Modular':
            info = xmlrpc.client.ServerProxy('https://ganeshvana-khazana-april-modular-4577685.dev.odoo.com/xmlrpc/2/common')
            url = self.env["ir.config_parameter"].sudo().get_param("module.url")
            url = 'https://ganeshvana-khazana1-modular-4805725.dev.odoo.com'
            common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
            db = self.env["ir.config_parameter"].sudo().get_param("module.db")
            db = 'ganeshvana-khazana1-modular-4805725'
            uid = self.env["ir.config_parameter"].sudo().get_param("module.uid")
            uid = 2
            password = self.env["ir.config_parameter"].sudo().get_param("module.password")
            password = 'admin'
            modells = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
            customer = modells.execute_kw(db, uid, password, 'res.partner', 'search', [[['name', '=', 'Khazana']]])
            sale = modells.execute_kw(db, uid, password, 'sale.order', 'create', [{'partner_id': customer[0],'client_order_ref': self.name}])
            sale_ref = modells.execute_kw(db, uid, password, 'sale.order', 'search', [[['id', '=', sale]]])
            self.partner_ref = sale_ref
            for line in self.order_line:
                product = modells.execute_kw(db, uid, password, 'product.product', 'search', [[['name', '=', line.product_id.name]]], { 'limit': 1})
                saleline = modells.execute_kw(db, uid, password, 'sale.order.line', 'create', [{'product_id': product[0], 'product_uom_qty': line.product_qty, 'price_unit': line.price_unit, 'order_id': sale}])
        return res
    
    
    