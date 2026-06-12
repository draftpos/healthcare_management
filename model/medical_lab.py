# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime


class medical_lab(models.Model):
    _name = 'medical.lab'
    _description = "Medical Lab"

    name = fields.Char('ID', default=lambda self: _('New'))
    test_id = fields.Many2one('medical.test_type', 'Test Type', required=True)
    date_analysis = fields.Datetime(
        'Date of the Analysis', default=datetime.now())
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)
    date_requested = fields.Datetime('Date requested', default=datetime.now())
    medical_lab_physician_id = fields.Many2one(
        'medical.physician', 'Pathologist')
    requestor_physician_id = fields.Many2one(
        'medical.physician', 'Physician', required=True)
    critearea_ids = fields.One2many(
        'medical_test.critearea', 'medical_lab_id', 'Critearea')
    results = fields.Text('Results')
    diagnosis = fields.Text('Diagnosis')
    is_invoiced = fields.Boolean(copy=False, default=False)
    group_id = fields.Many2one(
        'medical.pathology.group', string="Pathology Group")
    count_invoice = fields.Integer(
        "Count Invoice", compute="_compute_count_invoice")

    def _compute_count_invoice(self):
        for record in self:
            if record.is_invoiced:
                record.count_invoice = len(self.env['account.move'].search(
                    [('invoice_origin', '=', record.name)]))
            else:
                record.count_invoice = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('ltest_seq') or _('New')
        result = super(medical_lab, self).create(vals_list)
        for val in vals_list:
            if val.get('test_id'):
                critearea_obj = self.env['medical_test.critearea']
                criterea_ids = critearea_obj.search(
                    [('test_id', '=', val['test_id'])])
                for critearea in criterea_ids:
                    critearea.write({'medical_lab_id': result.id})

        return result

    @api.onchange('critearea_ids')
    def onchange_critearea_ids(self):
        for line in self.critearea_ids and self.critearea_ids[0]:
            if len(self.critearea_ids) > 1:
                line.seq = len(self.critearea_ids)
            else:
                line.seq = 1

    def action_open_invoices(self):
        action = {
            'name': _('Invoice'),
            'view_type': 'list',
            'view_mode': 'list',
            'views': [[False, 'list'], [False, 'form']],
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'domain': [('invoice_origin', '=', self.name)],
        }
        return action
