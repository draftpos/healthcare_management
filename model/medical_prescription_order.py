# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date, datetime


class medical_prescription_order(models.Model):
    _name = "medical.prescription.order"
    _description = "Medical Prescription Order"

    name = fields.Char('Prescription ID')
    patient_id = fields.Many2one('medical.patient', 'Patient')
    prescription_date = fields.Datetime(
        'Prescription Date', default=fields.Datetime.now())
    user_id = fields.Many2one(
        'res.users', 'Login User', readonly=True, default=lambda self: self.env.user)
    no_invoice = fields.Boolean('Invoice exempt')
    inv_id = fields.Many2one('account.move', 'Invoice')
    invoice_to_insurer = fields.Boolean('Invoice to Insurance')
    doctor_id = fields.Many2one('medical.physician', 'Prescribing Doctor')
    medical_appointment_id = fields.Many2one(
        'medical.appointment', 'Appointment ')
    state = fields.Selection(
        [('invoiced', 'To Invoiced'), ('tobe', 'To Be Invoiced')], 'Invoice Status')
    pharmacy_partner_id = fields.Many2one(
        'res.partner', domain=[('is_pharmacy', '=', True)], string='Pharmacy')
    prescription_line_ids = fields.One2many(
        'medical.prescription.line', 'name', 'Prescription Line')
    invoice_done = fields.Boolean('Invoice Done')
    notes = fields.Text('Prescription Note')
    appointment_id = fields.Many2one('medical.appointment')
    is_invoiced = fields.Boolean(copy=False, default=False)
    insurer_id = fields.Many2one('medical.insurance', 'Insurer')
    is_file_needed = fields.Boolean(
        'Hospital File', related='insurer_id.is_file_needed')
    is_pf_file = fields.Boolean('PF File', related='insurer_id.is_pf_file')
    is_pay_slip = fields.Boolean('Pay Slip', related='insurer_id.is_pay_slip')
    is_bank_statement = fields.Boolean(
        'Bank Statement', related='insurer_id.is_bank_statement')
    is_medical_bill = fields.Boolean(
        'Medical Bill', related='insurer_id.is_medical_bill')
    file = fields.Binary('File')
    file_name = fields.Char('File Name')
    pf_file = fields.Binary('PF  File')
    pf_file_name = fields.Char('File  Name')
    payslip_file = fields.Binary('Pay Slip File')
    payslip_file_name = fields.Char('Play Slip File Name')
    bank_statement_file = fields.Binary('Bank Statement File')
    bank_statement_file_name = fields.Char('Bank Statement File Name')
    medical_bill_file = fields.Binary('Medical Bill File')
    medical_bill_file_name = fields.Char('Medical Bill File Name')
    policy_no = fields.Char('Policy Number')
    is_shipped = fields.Boolean(default=False, copy=False)
    count_picking = fields.Integer(
        "Count Invoice", compute="_compute_count_picking")
    count_invoice = fields.Integer(
        "Count Invoice ", compute="_compute_count_invoice")
    image_ids = fields.One2many(
        'medical.imaging.test.request', 'prescription_id', string='Images')
    lab_test_ids = fields.One2many(
        'medical.patient.lab.test', 'prescription_id', string='Tests')

    def _compute_count_picking(self):
        for record in self:
            orders = self.env['sale.order'].search([('prescription_id', '=', self.id)])
            pickings = orders.mapped('picking_ids') if 'picking_ids' in self.env['sale.order']._fields else []
            if pickings:
                record.count_picking = len(pickings)
            else:
                record.count_picking = 0

    def _compute_count_invoice(self):
        for record in self:
            if record.is_invoiced:
                record.count_invoice = len(self.env['account.move'].search(
                    [('invoice_origin', '=', record.name)]))
            else:
                record.count_invoice = 0

    def _prepare_invoice_line(self, line):
        return {
            'product_id': line.product_id.id,
            'name': line.product_id.display_name or '',
            'product_uom_id': line.product_id.uom_id.id,
            'move_name': line.product_id.name or '',
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'medical.prescription.order') or '/'
        return super(medical_prescription_order, self).create(vals_list)

    def prescription_report(self):
        return self.env.ref('healthcare_management.report_print_prescription').report_action(self)

    @api.onchange('name')
    def onchange_name(self):
        ins_obj = self.env['medical.insurance']
        ins_record = ins_obj.search(
            [('medical_insurance_partner_id', '=', self.patient_id.patient_id.id)])
        self.insurer_id = ins_record.id or False

    def action_open_invoices(self):
        action = {
            'name': _('Prescription Invoice'),
            'view_type': 'list',
            'view_mode': 'list',
            'views': [[False, 'list'], [False, 'form']],
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
            'domain': [('invoice_origin', '=', self.name)],
        }
        return action

    def action_open_picking(self):
        orders = self.env['sale.order'].search([('prescription_id', '=', self.id)])
        pickings = orders.mapped('picking_ids')
        if pickings:
            action = {
                'name': _('Prescription Picking'),
                'view_type': 'list',
                'view_mode': 'list',
                'views': [[False, 'list'], [False, 'form']],
                'res_model': 'stock.picking',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'domain': [('id', 'in', pickings.ids)],
            }
            return action
