# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import uuid
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError, ValidationError


class medical_appointment(models.Model):
    _name = "medical.appointment"
    _inherit = 'mail.thread'
    _description = "Medical Appointment"

    @api.model
    def _default_access_token(self):
        return uuid.uuid4().hex

    name = fields.Char(string="Appointment ID", readonly=True, copy=True)
    is_invoiced = fields.Boolean(copy=False, default=False)
    institution_partner_id = fields.Many2one(
        'res.partner', domain=[('is_institution', '=', True)], string="Health Center")
    inpatient_registration_id = fields.Many2one(
        'medical.inpatient.registration', string="Inpatient Registration")
    patient_status = fields.Selection([
        ('ambulatory', 'Ambulatory'),
        ('outpatient', 'Outpatient'),
        ('inpatient', 'Inpatient'),
    ], 'Patient status', sort=False, default='outpatient')
    patient_id = fields.Many2one('medical.patient', 'Patient', required=True)
    urgency_level = fields.Selection([
        ('a', 'Normal'),
        ('b', 'Urgent'),
        ('c', 'Medical Emergency'),
    ], 'Urgency Level', sort=False, default="b")
    appointment_date = fields.Datetime(
        'Appointment Date', required=True, default=fields.Datetime.now())
    appointment_end = fields.Datetime('Appointment End', required=True)
    doctor_id = fields.Many2one('medical.physician', string='Physician', required=True)
    speciality_id = fields.Many2one(
        'medical.speciality', 'Speciality', required=True)
    no_invoice = fields.Boolean(string='Invoice exempt', default=True)
    validity_status = fields.Selection([
        ('invoice', 'Invoice'),
        ('tobe', 'To be Invoiced'),
    ], 'Status', sort=False, readonly=True, default='tobe')
    appointment_validity_date = fields.Datetime('Validity Date')
    consultations_id = fields.Many2one(
        'product.product', 'Consultation Service', required=True)
    comments = fields.Text(string="Info")
    state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirm'), (
        'cancel', 'Cancel'), ('done', 'Done')], string="State", default='draft')
    invoice_to_insurer = fields.Boolean('Invoice to Insurance')
    medical_patient_psc_ids = fields.Many2many(
        'medical.patient.psc', string='Pediatrics Symptoms Checklist')
    medical_prescription_order_ids = fields.One2many(
        'medical.prescription.order', 'appointment_id', string='Prescription')
    insurer_id = fields.Many2one('medical.insurance', 'Insurer')
    duration = fields.Integer('Duration')
    is_notified = fields.Boolean('Notification', default=False)
    count_invoice = fields.Integer("Count Invoice", compute="_compute_count_invoice")
    is_file_needed = fields.Boolean('Hospital File', related='insurer_id.is_file_needed')
    is_pf_file = fields.Boolean('PF File', related='insurer_id.is_pf_file')
    is_pay_slip = fields.Boolean('Pay Slip', related='insurer_id.is_pay_slip')
    is_bank_statement = fields.Boolean('Bank Statement', related='insurer_id.is_bank_statement')
    is_medical_bill = fields.Boolean('Medical Bill', related='insurer_id.is_medical_bill')
    file = fields.Binary('File')
    file_name = fields.Char('File Name')
    pf_file = fields.Binary(' PF File')
    pf_file_name = fields.Char(' File Name')
    payslip_file = fields.Binary('Pay Slip File')
    payslip_file_name = fields.Char('Play Slip File Name')
    bank_statement_file = fields.Binary('Bank Statement File')
    bank_statement_file_name = fields.Char('Bank Statement File Name')
    medical_bill_file = fields.Binary('Medical Bill File')
    medical_bill_file_name = fields.Char('Medical Bill File Name')
    policy_no = fields.Char('Policy Number')
    access_token = fields.Char('Security Token', default=_default_access_token)
    need_to_revisit = fields.Boolean('Need to Re-visit')
    next_visit_date = fields.Date('Next Visit Date')
    next_visit_charge = fields.Float('Visit Charge')
    total_no_of_visits = fields.Integer("Total Visits")

    @api.constrains('appointment_date', 'appointment_end')
    def check_dates(self):
        for rec in self:
            if rec.appointment_date > rec.appointment_end:
                raise ValidationError(_('The start date of the time off must be earlier than the end date.'))

    def _compute_count_invoice(self):
        for record in self:
            if record.is_invoiced:
                record.count_invoice = len(self.env['account.move'].search([('invoice_origin', '=', record.name)]))
            else:
                record.count_invoice = 0

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)

    @api.onchange('patient_id')
    def onchange_name(self):
        ins_obj = self.env['medical.insurance']
        ins_record = ins_obj.search(
            [('medical_insurance_partner_id', '=', self.patient_id.patient_id.id)])
        if len(ins_record) >= 1:
            self.insurer_id = ins_record[0].id
        else:
            self.insurer_id = False

    def action_close_alert(self):
        self.is_notified = False

    @api.model_create_multi
    def create(self, val_list):
        for vals in val_list:
            if vals.get('doctor_id') and vals.get('appointment_date') and vals.get('appointment_end'):
                start_val = vals.get('appointment_date')
                end_val = vals.get('appointment_end')

                start_date = start_val if isinstance(start_val, datetime) else datetime.strptime(start_val,"%Y-%m-%d %H:%M:%S")
                end_date = end_val if isinstance(end_val, datetime) else datetime.strptime(end_val,"%Y-%m-%d %H:%M:%S")

                appointment = self.search([('doctor_id', '=', vals.get('doctor_id'))])
                if appointment.filtered(lambda l: l.appointment_date < start_date and l.appointment_end > end_date):
                    raise ValidationError('Appointment Not Available in this slot.')
                elif appointment.filtered(lambda l: start_date < l.appointment_date < end_date and l.appointment_end > end_date):
                    raise ValidationError('Appointment Not Available in this slot.')
                elif appointment.filtered(lambda l: l.appointment_date < start_date and l.appointment_end < end_date and l.appointment_end > start_date):
                    raise ValidationError('Appointment Not Available in this slot.')
                elif appointment.filtered(lambda l: l.appointment_date > start_date and l.appointment_end < end_date):
                    raise ValidationError('Appointment Not Available in this slot.')
                elif appointment.filtered(lambda l: l.appointment_date == start_date or l.appointment_end == end_date or l.appointment_end == start_date):
                    raise ValidationError('Appointment Not Available in this slot.')
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'medical.appointment') or 'APT'
            msg_body = 'Appointment created'
            for msg in self:
                msg.message_post(body=msg_body)
        res = super(medical_appointment, self).create(val_list)
        if res:
            res.is_notified = True
        return res

    @api.onchange('doctor_id')
    def onchange_doctor(self):
        if not self.doctor_id:
            self.speciality_id = ""
        else:
            self.speciality_id = self.doctor_id.speciality_id

    @api.onchange('inpatient_registration_id')
    def onchange_patient(self):
        if not self.inpatient_registration_id:
            self.patient_id = ""
        inpatient_obj = self.env['medical.inpatient.registration'].browse(
            self.inpatient_registration_id.id)
        self.patient_id = inpatient_obj.patient_id.id

    def confirm(self):
        self.write({'state': 'confirmed'})

    def done(self):
        self.write({'state': 'done'})

    def cancel(self):
        self.write({'state': 'cancel'})

    def print_prescription(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'done'})
        if not self.medical_prescription_order_ids:
            raise UserError(_(' No Prescription Added  '))
        return self.env.ref('healthcare_management.report_print_prescription').report_action(self)

    def view_patient_invoice(self):
        self.write({'state': 'cancel'})

    def create_invoice(self):
        lab_req_obj = self.env['medical.appointment']
        account_invoice_obj = self.env['account.move']
        account_invoice_line_obj = self.env['account.move.line']
        lab_req = lab_req_obj
        if lab_req.is_invoiced and not lab_req.need_to_revisit:
            raise UserError(_(' Invoice is Already Exist'))
        if (lab_req.no_invoice and lab_req.need_to_revisit) or not lab_req.is_invoiced:
            res = account_invoice_obj.create({'partner_id': lab_req.patient_id.patient_id.id,
                                              'invoice_date': date.today()})
            if not lab_req.need_to_revisit:
                invoice_line_vals = {
                    'name': lab_req.consultations_id.name or '',
                    'account_id': invoice_line_account_id,
                    'price_unit': lab_req.consultations_id.lst_price,
                    'product_uom_id': lab_req.consultations_id.uom_id.id,
                    'quantity': 1,
                    'product_id': lab_req.consultations_id.id,
                }
            else:
                invoice_line_vals = {
                    'product_id': lab_req.consultations_id.id,
                    'name': lab_req.consultations_id.name or '',
                    'account_id': invoice_line_account_id,
                    'price_unit': lab_req.consultations_id.lst_price,
                    'product_uom_id': lab_req.consultations_id.uom_id.id,
                    'quantity': 1,
                }
            res1 = res.write({'invoice_line_ids': ([(0, 0, invoice_line_vals)])})
            if res:
                lab_req.write({'is_invoiced': True})
                imd = self.env['ir.model.data']
                action = self.env.ref('account.action_move_out_invoice_type')
                list_view_id = imd.sudo()._xmlid_to_res_id('account.view_move_form')
                result = {
                    'name': action.name,
                    'help': action.help,
                    'type': action.type,
                    'views': [[list_view_id, 'form']],
                    'target': action.target,
                    'context': action.context,
                    'res_model': action.res_model,
                    'res_id': res.id,
                }
                if res:
                    result['domain'] = "[('id','=',%s)]" % res.id
        else:
            raise UserError(_(' The Appointment is invoice exempt'))
        return result

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

    def action_send_revisit_reminder(self):
        today = fields.Date.today()
        before_today = today - timedelta(days=1)
        after_today = today + timedelta(days=1)
        template = self.env.ref(
            'healthcare_management.revisit_reminder_mail_template_medical_appointment', raise_if_not_found=False)
        before_records = self.search([('need_to_revisit', '=', True), ('next_visit_date', '=', before_today)])
        after_records = self.search([('need_to_revisit', '=', True), ('next_visit_date', '=', after_today)])
        records = after_records + before_records
        if records and template:
            for record in records:
                mail = template.send_mail(int(record.id))
                if mail:
                    mail_id = self.env['mail.mail'].browse(mail)
                    mail_id.sudo().send()
