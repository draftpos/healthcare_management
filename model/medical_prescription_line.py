# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class medical_prescription_line(models.Model):
    _name = "medical.prescription.line"
    _description = "Medical Prescription Line"

    name = fields.Many2one('medical.prescription.order','Prescription ID')
    medicament_id = fields.Many2one('medical.medicament','Medicament')
    indication = fields.Char('Indication')
    allow_substitution = fields.Boolean('Allow Substitution')
    form = fields.Char('Form')
    prnt = fields.Boolean('Print')
    route = fields.Many2one('medical.drug.route', string="Administration Route")
    end_treatement = fields.Datetime('Administration Route ')
    dose = fields.Float('Dose')
    dose_unit_id = fields.Many2one('medical.dose.unit', 'Dose Unit')
    qty = fields.Integer('x')
    medication_dosage_id = fields.Many2one('medical.medication.dosage','Frequency')
    admin_times = fields.Char('Admin Hours', size = 128)
    frequency = fields.Integer(' Frequency')
    frequency_unit = fields.Selection([('seconds','Seconds'),('minutes','Minutes'),('hours','hours'),('days','Days'),('weeks','Weeks'),('wr','When Required')], 'Unit')
    duration = fields.Float('Treatment Duration(Min)')
    duration_period = fields.Selection([('minutes','Minutes'),('hours','hours'),('days','Days'),('months','Months'),('years','Years'),('indefine','Indefine')],'Treatment Period')
    quantity = fields.Integer('Quantity')
    review = fields.Datetime('Review')
    refills = fields.Integer('Refills#')
    short_comment = fields.Char('Comment', size=128 )
    end_treatment = fields.Datetime('End of treatment')
    start_treatment = fields.Datetime('Start of treatment')

    @api.constrains('start_treatment', 'end_treatment')
    def check_dates(self):
        for rec in self:
            if rec.start_treatment and rec.end_treatment and rec.start_treatment > rec.end_treatment:
                raise ValidationError(_('The start date of the time off must be earlier than the end date.'))

    @api.onchange('start_treatment', 'end_treatment')
    def _onchange_treatment(self):
        if self.start_treatment and self.end_treatment:
            duration = (self.end_treatment - self.start_treatment).total_seconds()
            if duration:
                self.duration = float(duration/60)