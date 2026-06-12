# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import re
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class BloodDonors(models.Model):
    _name = 'blood.donor'
    _description = "Blood Donors"

    name = fields.Char('Name')
    patient_id = fields.Many2one('res.partner', string="Donor", domain=[
                                 ('is_patient', '=', True)])
    date = fields.Datetime(string='Date')
    email = fields.Char('E-mail')
    mobile = fields.Char('Mobile No.')
    is_consent = fields.Boolean(' Consent', default=True)
    product_id = fields.Many2one('product.product', string="Blood Group", required=True, domain=[
                                 ('is_blood', '=', True)])
    transaction_ids = fields.One2many(
        'blood.donor.transaction', 'donor_id', string='Transactions')
    count_in_transaction = fields.Integer(
        'Count Donated Transaction', compute='_compute_donted_transaction')
    count_out_transaction = fields.Integer(
        'Count Taken Blood Transaction', compute='_compute_out_transaction')
    balance = fields.Float('Available Balance', compute='_compute_balance')
    consent = fields.Boolean('Consent', default=True)
    buy_blood_ids = fields.One2many('buy.blood', 'donor_id', string='Buy Blood Orders')
    count_buy_bloods = fields.Integer('Count Buy Blood Order', compute='_count_buy_blood_order')
    my_request_ids = fields.One2many('blood.request', 'provider_id', string='My Request')

    @api.depends('buy_blood_ids')
    def _count_buy_blood_order(self):
        for record in self:
            if record.buy_blood_ids:
                record.count_buy_bloods = len(record.buy_blood_ids)
            else:
                record.count_buy_bloods = 0

    def _compute_balance(self):
        for record in self:
            if record.transaction_ids:
                confirm_orders = 0.0
                in_transaction = sum(record.transaction_ids.filtered(
                    lambda l: l.type == 'in').mapped('qty'))
                out_transaction = sum(record.transaction_ids.filtered(
                    lambda l: l.type == 'out').mapped('qty'))
                confirm_orders = sum(self.my_request_ids.filtered(lambda l: l.state == 'accept').mapped('qty'))
                record.balance = in_transaction - out_transaction - confirm_orders
            else:
                record.balance = 0.0

    @api.depends('transaction_ids')
    def _compute_donted_transaction(self):
        for record in self:
            if record.transaction_ids:
                record.count_in_transaction = len(
                    record.transaction_ids.filtered(lambda l: l.type == 'in'))
            else:
                record.count_in_transaction = 0

    @api.depends('transaction_ids')
    def _compute_out_transaction(self):
        for record in self:
            if record.transaction_ids:
                record.count_out_transaction = len(
                    record.transaction_ids.filtered(lambda l: l.type == 'out'))
            else:
                record.count_out_transaction = 0
    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            partner = self.env['res.partner'].create({'name': val.get('name'), 'is_patient': True, 'company_id': self.env.context.get('allowed_company_ids')[0]})
            if partner:
                val.update({'patient_id': partner.id})
        return super(BloodDonors, self).create(vals_list)

    def write(self, vals):
        for record in self:
            if vals.get('name') and record.patient_id:
                record.patient_id.write({'name': vals.get('name')})
        return super(BloodDonors, self).write(vals)

    def action_open_in_transaction(self):
        if not self.consent:
            raise ValidationError("Consent is necessary!")
        donate_transaction_id = False
        if self.transaction_ids:
            donate_transaction_id = self.transaction_ids.filtered(
                lambda l: l.type == 'in')
        if donate_transaction_id:
            return {
                'name': _("Blood Donated History"),
                'view_mode': 'list,form',
                'res_model': 'blood.donor.transaction',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', donate_transaction_id.ids)],
            }

    def action_open_buy_blood_order(self):
        if self.buy_blood_ids:
            action = {
                'name': _('Blood Buy'),
                'view_type': 'list',
                'view_mode': 'list,form',
                'res_model': 'buy.blood',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'domain': [('id', 'in', self.buy_blood_ids.ids)],
            }
            return action
    
    def action_open_my_request(self):
        if self.my_request_ids:
            action = {
                'name': _('Blood Request'),
                'view_type': 'list',
                'view_mode': 'list',
                'res_model': 'blood.request',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'domain': [('id', 'in', self.my_request_ids.ids)],
            }
            return action

    def action_open_out_transaction(self):
        if not self.consent:
            raise ValidationError("Consent is necessary!")
        donate_transaction_id = False
        if self.transaction_ids:
            donate_transaction_id = self.transaction_ids.filtered(
                lambda l: l.type == 'out')
        if donate_transaction_id:
            return {
                'name': _("Blood Donated History"),
                'view_mode': 'list,form',
                'res_model': 'blood.donor.transaction',
                'type': 'ir.actions.act_window',
                'domain': [('id', 'in', donate_transaction_id.ids)],
            }

    @api.onchange('email')
    def _onchange_email(self):
        if self.email:
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", self.email) == None:
                raise ValidationError('Please enter a valid email address.')

    def action_donate_blood(self):
        if not self.consent:
            raise ValidationError("Consent is necessary!")
        if self:
            return {
                'res_model': 'create.blood.donor.transaction',
                'view_mode': 'form',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'default_donor_id': self.id, 'default_type': 'in', 'default_product_id': self.product_id.id},
            }

    def action_take_blood(self):
        if not self.consent:
            raise ValidationError("Consent is necessary!")
        if self:
            return {
                'name': 'Take Blood',
                'res_model': 'create.blood.donor.transaction',
                'view_mode': 'form',
                'target': 'new',
                'type': 'ir.actions.act_window',
                'context': {'default_donor_id': self.id, 'default_type': 'out', 'default_product_id': self.product_id.id},
            }
