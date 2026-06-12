# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date, datetime


class medical_inpatient_registration(models.Model):
    _name = 'medical.inpatient.registration'
    _description = "Medical Inpatient Registration"

    name = fields.Char(string="Registration Code",
                       copy=False, readonly=True, index=True, default=lambda self: _('New'))
    patient_id = fields.Many2one(
        'medical.patient', string="Patient", required=True)
    medical_hospital_bed_id = fields.Many2one(
        'medical.hospital.bed', string="Hospital Bed", required=True)
    hospitalization_date = fields.Datetime(
        string="Hospitalization date", required=True)
    discharge_date = fields.Datetime(string="Discharge date", required=True)
    attending_physician_id = fields.Many2one(
        'medical.physician', string="Attending Physician")
    operating_physician_id = fields.Many2one(
        'medical.physician', string="Operating Physician")
    admission_type = fields.Selection(
        [('routine', 'Routine'), ('maternity', 'Maternity'), ('elective', 'Elective'), ('urgent', 'Urgent'),
         ('emergency', 'Emergency  ')], required=True, string="Admission Type")
    medical_pathology_id = fields.Many2one(
        'medical.pathology', string="Reason for Admission")
    info = fields.Text(string="Extra Info")
    bed_transfers_ids = fields.One2many(
        'bed.transfer', 'inpatient_id', string='Transfer Bed', readonly=True)
    medical_diet_belief_id = fields.Many2one(
        'medical.diet.belief', string='Belief')
    therapeutic_diets_ids = fields.One2many('medical.inpatient.diet', 'medical_inpatient_registration_id',
                                            string='Therapeutic_diets')
    diet_vegetarian = fields.Selection([('none', 'None'), ('vegetarian', 'Vegetarian'), ('lacto', 'Lacto Vegetarian'),
                                        ('lactoovo', 'Lacto-Ovo-Vegetarian'), ('pescetarian',
                                                                               'Pescetarian'),
                                        ('vegan', 'Vegan')], string="Vegetarian")
    nutrition_notes = fields.Text(string="Nutrition notes / Directions")
    state = fields.Selection(
        [('free', 'Free'), ('confirmed', 'Confirmed'), ('hospitalized', 'Hospitalized'), ('icu', 'I.C.U'), ('cancel', 'Cancel'),
         ('done', 'Discharged')], string="State", default="free")
    nursing_plan = fields.Text(string="Nursing Plan")
    discharge_plan = fields.Text(string="Discharge Plan")
    icu = fields.Boolean(string="ICU")
    medication_ids = fields.One2many('medical.inpatient.medication', 'medical_inpatient_registration_id',
                                     string='Medication')
    icu_admissions_ids = fields.One2many('medical.inpatient.icu', 'medical_inpatient_registration_id', string='ICU Ids',
                                         readonly=True)
    ward_id = fields.Many2one('medical.hospital.ward', string='Ward')

    @api.onchange('medical_hospital_bed_id')
    def _onchange_medical_hospital_bed_id(self):
        if self.medical_hospital_bed_id and self.medical_hospital_bed_id.medical_hospital_ward_d:
            self.ward_id = self.medical_hospital_bed_id.medical_hospital_ward_d.id

    @api.model
    def default_get(self, fields):
        result = super(medical_inpatient_registration,
                       self).default_get(fields)
        patient_id = self.env['ir.sequence'].next_by_code(
            'medical.inpatient.registration')
        if patient_id:
            result.update({
                'name': patient_id,
            })
        return super().default_get(fields)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', _('New')) == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'medical.inpatient.registration') or _('New')
        return super(medical_inpatient_registration, self).create(vals_list)

    def registration_confirm(self):
        self.write({'state': 'confirmed'})

    def registration_admission(self):
        self.write({'state': 'hospitalized'})
        self.medical_hospital_bed_id.write({'state': 'occuiped'})

    def registration_cancel(self):
        self.write({'state': 'cancel'})
        self.medical_hospital_bed_id.write({'state': 'free'})

    def patient_discharge(self):
        self.write({'state': 'done', 'discharge_date': fields.Datetime.now()})
        self.medical_hospital_bed_id.write({'state': 'free'})
