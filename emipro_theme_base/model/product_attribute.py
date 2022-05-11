# -*- coding: utf-8 -*-
"""
    This model is used to create a quick filter boolean field and icon style for color type in attributes
"""

from odoo import fields, models


class ProductAttribute(models.Model):
    _inherit = ['product.attribute']
    
    is_quick_filter = fields.Boolean(string='Quick Filter', help="It will show this attribute in quick filter")
    website_ids = fields.Many2many('website', help="You can set the filter in particular website.")
    icon_style = fields.Selection(selection=[('round', "Round"), ('square', "Square"), ], string="Icon Style", default='round', help="Here, Icon size is 40*40")
    is_swatches = fields.Boolean(string='Use Swatch Image', help="It will show the icon column to set the swatches", default=True)
    allow_search = fields.Boolean(string='Allow Search',help="Enable the attribute value search option in product attribute's filters")
