# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BuyBlood(models.Model):
    _name = 'buy.blood'
    _description = "Buy Blood"
    _rec_name = 'donor_id'

    donor_id = fields.Many2one('blood.donor', string='Patient', required=True)
    date = fields.Datetime(
        'Date', default=lambda self: fields.Datetime.now(), required=True)
    qty = fields.Float('Quantity')
    product_id = fields.Many2one('product.product', related='donor_id.product_id', required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('cancel', 'Cancelled')
    ], string='Status', required=True, readonly=True, copy=False,
        default='draft')
    order_request_ids = fields.One2many(
        'blood.request', 'order_id', string='Requestes')
    take_more = fields.Boolean('Take More', default=False)

    @api.onchange('qty', 'product_id')
    def _onchange_qty(self):
        if self.qty and self.product_id and self.state == 'draft':
            if self.donor_id.balance >= self.qty:
                raise ValidationError('you have already sufficient Blood Balance.')
            self.order_request_ids = False
            donors = self.env['blood.donor'].search(
                [('product_id', '=', self.product_id.id)]).filtered(lambda l: l.balance >= self.qty)
            prepare_line = []
            for line in donors:
                prepare_line.append((0, 0, {
                    'provider_id': line.id, 'patient_id': self.donor_id.id,
                    'balance': line.balance, 'product_id': self.product_id.id,
                    'qty': self.qty}))
            self.order_request_ids = prepare_line

    def action_cancel(self):
        self.state = 'cancel'
        return True

    def unlink(self):
        for record in self:
            if record.state == 'confirmed':
                raise ValidationError("Can't delete Confirm process.")
        return super(BuyBlood, self).unlink()
