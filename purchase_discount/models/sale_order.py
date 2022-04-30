# Copyright 2004-2009 Tiny SPRL (<http://tiny.be>).
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2015-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    discount = fields.Float(string="Discount (%)", digits="Discount")

    @api.depends("discount")
    def compute_discount(self):
        for line in self.order_line:
            if line.apply_discount == True and self.discount > 0:
                line.update({'discount':self.discount})
            else:
                line.update({'discount':0})
                
    def action_confirm(self):
        result = super(SaleOrder, self).action_confirm()
        for rec in self:
            for res in rec.order_line:
                if res.product_id.website_id.khazana == True:
                    if res.product_id.intransit:
                        res.product_id.product_tmpl_id.sold_units += res.product_uom_qty
                        res.product_id.out_of_stock_message = str(res.product_id.product_tmpl_id.po_units) + ' ' + str(res.product_id.uom_po_id.name)+ " In Transit" + ' ' + str(res.product_id.product_tmpl_id.sold_units) + ' ' + str(res.product_id.uom_id.name) +  ' Sold'    
                        if res.product_id.product_tmpl_id.sold_units >= res.product_id.product_tmpl_id.po_units:
                            res.product_id.product_tmpl_id.allow_out_of_stock_order = False
                            res.product_id.product_tmpl_id.active = False
                if res.product_id.website_id.khazana == False:
                    if res.product_id.intransit:
                        res.product_id.product_tmpl_id.sold_units += res.product_uom_qty
                        res.product_id.out_of_stock_message = str(res.product_id.product_tmpl_id.po_units) + ' ' + str(res.product_id.uom_po_id.name)+ " In Transit" + ' ' + str(res.product_id.product_tmpl_id.sold_units) + ' ' + str(res.product_id.uom_id.name) +  ' Sold'    
                        if res.product_id.product_tmpl_id.sold_units >= res.product_id.product_tmpl_id.po_units:
                            res.product_id.product_tmpl_id.allow_out_of_stock_order = False
                            res.product_id.product_tmpl_id.active = False
                            # res.product_id.out_of_stock_message = ''
        return result




