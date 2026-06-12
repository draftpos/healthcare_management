# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CreateBloodDonorTransaction(models.TransientModel):
    _name = 'create.blood.donor.transaction'
    _description = "Create Blood Donor Transaction"

    donor_id = fields.Many2one('blood.donor', string='Donors', required=True)
    type = fields.Selection(string='Type', selection=[
                            ('in', 'In'), ('out', 'Out')], required=True)
    date = fields.Datetime(
        'Date', default=lambda self: fields.Datetime.now(), required=True)
    qty = fields.Float('Quantity')
    product_id = fields.Many2one('product.product', string="Blood Group", domain=[
                                 ('is_blood', '=', True)], required=True)
    more_buy = fields.Boolean('More Buy', default=False)

    @api.onchange('qty')
    def _onchange_qty(self):
        if self.type == 'out' and self.donor_id:
            current = self.donor_id.balance - self.qty
            if current < 0:
                self.more_buy = True
            else: 
                self.more_buy = False

    def action_create_blood_donor_transaction(self):
        if self.more_buy:
            raise ValidationError('Please go for buy blood.')
        if not self.donor_id or not self.type or not self.date or self.qty <= 0 or not self.product_id:
            raise ValidationError('Enter Validate Data!')
        self.env['blood.donor.transaction'].create(
            {'donor_id': self.donor_id.id,
             'type': self.type,
             'date': self.date,
             'qty': self.qty,
             'product_id': self.product_id.id})
        return True
