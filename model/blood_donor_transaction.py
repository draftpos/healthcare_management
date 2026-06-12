# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BloodDonorsTransaction(models.Model):
    _name = 'blood.donor.transaction'
    _description = "Blood Donors Transaction"
    _rec_name = 'donor_id'

    donor_id = fields.Many2one('blood.donor', string='Donors', required=True)
    type = fields.Selection(string='Type', selection=[
                            ('in', 'In'), ('out', 'Out')], required=True)
    date = fields.Datetime(
        'Date', default=lambda self: fields.Datetime.now(), required=True)
    qty = fields.Float('Quantity')
    product_id = fields.Many2one('product.product', string="Blood Group", domain=[
                                 ('is_blood', '=', True)], required=True)
