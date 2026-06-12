# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BloodRequest(models.Model):
    _name = 'blood.request'
    _description = "Blood Request"
    _rec_name = 'provider_id'

    provider_id = fields.Many2one('blood.donor', string='Donor', required=True)
    order_id = fields.Many2one(
        'buy.blood', string='Ragister Order')
    patient_id = fields.Many2one(
        'blood.donor', string='Patient', related='order_id.donor_id')
    date = fields.Datetime(
        'Date', default=lambda self: fields.Datetime.now(), required=True)
    qty = fields.Float('Quantity')
    balance = fields.Float('Balance')
    product_id = fields.Many2one('product.product', string="Blood Group", domain=[
                                 ('is_blood', '=', True)])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('accept', 'Accept'),
        ('cancel', 'Cancelled')
    ], string='Status', required=True, copy=False,
        default='draft')
    
    def action_accept_donate(self):
        if not self.state == 'accept' and self.state == 'draft':
            self.state = 'accept'
            others_orders = self.order_id.order_request_ids.filtered(lambda l: l.state == 'draft')
            if others_orders:
                others_orders.unlink()
            self.order_id.state = 'confirmed'
        return True

    def action_cancel_donate(self):
        if not self.state == 'draft':
            raise ValidationError('Order not in draft!\n Some action was already performed.')
        self.state = 'cancel'
        self.unlink()
        return True