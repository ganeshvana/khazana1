from odoo import models, fields, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
import itertools

class Web(models.Model):
    _inherit = 'website'
    
    khazana = fields.Boolean("Khazana website")

class Variant(models.Model):
    _inherit = 'product.product'

    # @api.depends('product_template_attribute_value_ids')
    # def _compute_combination_indices(self):
    #     for product in self:
    #         if product.product_tmpl_id.create_combination_variant == True:
    #             product.combination_indices = product.product_template_attribute_value_ids._ids2str()
                
    container_no = fields.Char("Container")                
    l10n_in_hsn_code = fields.Char("HSN/SAC Code")
    
    
    
    @api.model_create_multi
    def create(self, vals_list):    
        templates = super(Variant, self).create(vals_list)        
        seq = self.env['ir.sequence'].next_by_code('product.barcode.seq') or '/'
        templates.barcode = seq
        return templates
    
  
    
class Product(models.Model):
    _inherit = 'product.template'

    intransit = fields.Boolean("In Transit")
    create_combination_variant = fields.Boolean("Create Variant Combination")
    container_no = fields.Char("Container")
    # purchase_ok = fields.Boolean('Can be Purchased')
    seller_ids = fields.One2many('product.supplierinfo', 'product_tmpl_id', 'Vendors', depends_context=('company',), help="Define vendor pricelists.", copy=True)
    sold_units = fields.Float("Sold in web")
    po_units = fields.Float("PO in web")
    website_name = fields.Char("Website Product Name", compute='compute_website_name', store=True)
    eta = fields.Date('ETA')
    container = fields.Char("Container")
    
    @api.depends('attribute_line_ids', 'name', 'default_code')
    def compute_website_name(self):
        for rec in self:
            wname = ''
            if rec.default_code:
                wname += rec.default_code + ' '
            if rec.name:
                wname += rec.name
            if rec.attribute_line_ids:
                att = ''
                for line in rec.attribute_line_ids:
                    att += line.value_ids[0].name + ','
                att = att[:-1]    
                wname += '(' + att + ')'
            rec.website_name = wname
    
    # @api.depends('qty_available')
    def check_stock(self):
        products = self.env['product.template'].search([])
        if products:
            for line in products:
                if line.website_id:
                    if line.website_id.khazana == True:
                        if line.detailed_type == 'product' and not line.intransit:
                            if line.qty_available == 0.0:
                                line.active = False
                    if line.website_id.khazana == False:
                        if line.detailed_type == 'product' and not line.intransit:
                            if line.qty_available == 0.0:
                                if not line.intransit:
                                    line.allow_out_of_stock_order = True
                                    line.out_of_stock_message = ''
                    
        # for rec in self:
        #     if rec.website_id.khazana == True:
        #         if rec.qty_available <= 0.0:
        #             rec.website_id = False
            
        
    
    # @api.model
    # def create(self, vals_list):    
    #     var = super(Variant, self).create(vals_list)
    #
    #     if not self.barcode:
    #         self.active = False
    #     return var
    
    # def write(self, vals):        
    #     res = super(Product, self).write(vals)
    #     if 'attribute_line_ids' in vals and self.create_combination_variant == True or (vals.get('active') and len(self.product_variant_ids) == 0):
    #         self._create_variant_ids()
    #     return res
    
    @api.model_create_multi
    def create(self, vals_list):    
        templates = super(Product, self).create(vals_list)
        if templates.detailed_type == 'product' and templates.purchase_ok:
            if not templates.seller_ids:
                raise UserError(_('Update the vendor for Product.'))
        seq = self.env['ir.sequence'].next_by_code('product.barcode.seq') or '/'
        templates.barcode = seq
        return templates
    
    def write(self, vals_list):
        if not self.env.user.has_group('oi_crm.group_hsn_code'):
            if 'l10n_in_hsn_code' in vals_list:
                raise UserError(_('You are not allowed to edit HSN Code.'))
        res = super(Product, self).write(vals_list)
        return res
    
    
class Purchase(models.Model):
    _inherit = 'purchase.order'
    
    def button_confirm(self):
        res = super(Purchase,self).button_confirm()
        for rec in self:
            categ = self.env['product.public.category'].search([('name', '=', 'In Transit')], limit=1)
            if rec.picking_ids:
                for pline in rec.order_line:
                    if pline.product_id.qty_available == 0.0:
                        if pline.product_id.website_id.khazana == True:                            
                            pline.product_id.intransit = True
                            if categ:                                
                                pline.product_id.public_categ_ids = [(4,categ.id)]
                            pline.product_id.product_tmpl_id.intransit = True
                            pline.product_id.product_tmpl_id.eta = rec.date_planned
                            pline.product_id.product_tmpl_id.allow_out_of_stock_order = True
                            pline.product_id.product_tmpl_id.po_units = pline.product_qty
                            pline.product_id.out_of_stock_message = str(pline.product_id.product_tmpl_id.po_units) + ' ' + str(pline.product_id.uom_po_id.name)+ " In Transit" + pline.product_id.product_tmpl_id.eta.strftime("%d/%m/%Y") + ' ' +  rec.name
                        if pline.product_id.website_id.khazana == False:
                            pline.product_id.intransit = True
                            if categ:
                                pline.product_id.public_categ_ids = [(4,categ.id)]
                            pline.product_id.product_tmpl_id.intransit = True
                            pline.product_id.product_tmpl_id.eta = rec.date_planned
                            pline.product_id.product_tmpl_id.allow_out_of_stock_order = True
                            pline.product_id.product_tmpl_id.po_units = pline.product_qty
                            pline.product_id.out_of_stock_message = str(pline.product_id.product_tmpl_id.po_units) + ' ' + str(pline.product_id.uom_po_id.name)+ " In Transit" + pline.product_id.product_tmpl_id.eta.strftime("%d/%m/%Y") + ' ' + rec.name
        return res
                    
class Picking(models.Model):
    _inherit = 'stock.picking'
    
    import_stage = fields.Selection([
        ('shipment', 'Ready for Despatch'),
        ('nncd', 'Estimated time of Despatch'),
        ('eta', 'Estimated time of Arrival'),
        ], string="Import Stages", default='shipment')
    eta = fields.Date("Estimated time of Arrival")
    etd = fields.Date("Estimated time of Delivery")
    rfd = fields.Boolean("Ready for Despatch")
    container = fields.Char("Container")
    
    def button_validate(self):
        res = super(Picking,self).button_validate()
        categ = self.env['product.public.category'].search([('name', '=', 'In Transit')], limit=1)
        stockcateg = self.env['product.public.category'].search([('name', '=', 'In Stock')], limit=1)
        for rec in self:
            if rec.picking_type_code == 'incoming':
                if rec.move_ids_without_package:
                    for pline in rec.move_ids_without_package:
                        if not pline.product_id.l10n_in_hsn_code:
                            raise UserError(_("Update HSN Code in %s", pline.product_id.name))
                        if pline.product_id:
                            if pline.product_id.qty_available > 0.0:
                                pline.product_id.intransit = False
                                if categ:
                                    if categ.id in pline.product_id.public_categ_ids.ids:
                                        pline.product_id.public_categ_ids = [(6, 0,[stockcateg.id])]
                                pline.product_id.product_tmpl_id.intransit = False
                                pline.product_id.product_tmpl_id.allow_out_of_stock_order = False
                                pline.product_id.out_of_stock_message = ''
                                pline.product_id.product_tmpl_id.po_units = 0.0
                                pline.product_id.product_tmpl_id.sold_units = 0.0
                mail_template_id = self.env.ref('oi_crm.mail_template_send_receipt_validate')
                self.env['mail.template'].browse(mail_template_id.id).send_mail(rec.id, force_send=True)
            return res   
    
    def write(self, vals):
        res = super(Picking, self).write(vals)
        if 'eta' or 'container' in vals:
            for rec in self:
                if rec.move_ids_without_package:
                    for line in rec.move_ids_without_package:
                        if line.product_id:
                            if line.product_id.intransit:
                                if rec.eta:
                                    eta = rec.eta.strftime("%d/%m/%Y")
                                else:
                                    eta = ''
                                if rec.container:
                                    container = rec.container
                                else:
                                    container = ''
                                line.product_id.product_tmpl_id.eta = rec.eta
                                line.product_id.product_tmpl_id.container = rec.container
                                line.product_id.product_tmpl_id.out_of_stock_message = str(line.product_id.product_tmpl_id.po_units) + ' ' + str(line.product_id.uom_po_id.name)+ " In Transit ETA:" + eta + ' ' + rec.origin + ' ' + container  
            
    
    
    