# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Nimisha Muralidhar (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import models, fields, api, _


class PickingBulkUpdate(models.TransientModel):
    _name = 'stock.picking.bulk.update'
    _description = 'Picking Bulk Update'
    
    @api.model
    def default_get(self,vals):
        pickings = []
        vals = super(PickingBulkUpdate,self).default_get(vals)
        if self._context.get('active_model') == 'stock.picking' and self._context.get('active_id', False):
            for line in self._context['active_ids']:
                picking = self.env['stock.picking'].browse(line)
                if picking.picking_type_code == 'incoming':
                    if picking.id not in pickings:
                        pickings.append(picking.id)
        
        vals.update({
            'picking_ids':[(6,0, pickings)],
        })
        return  vals

    picking_ids = fields.Many2many('stock.picking', 'picking_wiz_rel', 'rel_id', 'picking_id', string='Pickings')
    eta = fields.Date("ETA")
    container = fields.Char("Container")
    
    
    def bulk_update_picking(self):
        if self.picking_ids:
            for line in self.picking_ids:
                if line.picking_type_code == 'incoming':
                    if self.eta:
                        line.eta = self.eta
                        mail_template_id = self.env.ref('oi_crm.mail_template_send_eta')
                        self.env['mail.template'].browse(mail_template_id.id).send_mail(self.id, force_send=True)
                    if self.container:
                        line.container = self.container
        return True
    
class PrintPackage(models.TransientModel):
    _name = 'stock.picking.print'
    _description = 'Print Package'
    
    count = fields.Integer("Package Count")
    picking_id = fields.Many2one('stock.picking', "Picking")
    partner_id = fields.Many2one('res.partner', "Partner")
        

    

