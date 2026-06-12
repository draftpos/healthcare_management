# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
 
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import date,datetime


class medical_inpatient_icu(models.Model):
    _name = 'medical.inpatient.icu'
    _rec_name ='medical_inpatient_registration_id'
    _description = "Medical Inpatient ICU"

    medical_inpatient_registration_id = fields.Many2one('medical.inpatient.registration',string="Registration Code",required=True)
    admitted =fields.Boolean(string="Admitted")
    icu_admission_date = fields.Datetime(string="ICU Admission",required=True)
    icu_stay = fields.Char(string="Duration",required=True,size=128)
    discharged_from_icu =fields.Boolean(string="Discharged")
    icu_discharge_date  = fields.Datetime(string='Discharge Date')
    medical_icu_ventilation_ids = fields.One2many('medical.icu.ventilation','medical_inpatient_icu_id',string='MV History')
    deceased = fields.Boolean('Deceased')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('admit', 'Admitted'),
        ('cancel', 'Cancelled'),
        ('discharge', 'Discharged')
    ], string='Status', required=True, copy=False,
        default='draft')

    @api.onchange('medical_inpatient_registration_id')
    def onchange_patient(self):
        for each in self:
            inpatient_icu_obj = each.env['medical.inpatient.icu']
            inpatient_icu_ids = inpatient_icu_obj.search([('medical_inpatient_registration_id.name','=',each.medical_inpatient_registration_id.name)])
            if len(inpatient_icu_ids) > 1:
                raise UserError(_('Our records indicate that the patient is already admitted at ICU. '))

    def action_admit(self):
        if self.state == 'draft':
            self.state = 'admit'
            self.admitted = True

    def action_discharge(self):
        if self.state == 'admit':
            self.state = 'discharge'
            self.admitted = False
            self.discharged_from_icu = True

    def action_cancel(self):
        if not self.state == 'cancel':
            self.state = 'cancel'
            self.discharged_from_icu = False
            self.admitted = False
