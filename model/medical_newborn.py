# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date,datetime
from odoo.exceptions import ValidationError


class medical_newborn(models.Model):
    _name = 'medical.newborn'
    _description = "Medical Newborn"

    name = fields.Char('Name', readonly = True)
    patient_id = fields.Many2one('medical.patient', string="Patient")
    mother_patient_id = fields.Many2one('medical.patient','Mother',required=True, domain="[('sex', '=', 'f')]")
    birth_date  = fields.Date('Date of Birth', required = True)
    length = fields.Float('Length', )
    cephalic_perimeter = fields.Integer('Cephalic Perimeter')
    baby_name  = fields.Char('Baby\'s name')
    sex  = fields.Selection([('m','Male'), ('f','Female'),('a','Ambiguous Genitalia ')], required = True ) 
    dismissed  = fields.Datetime('Discharged')
    weight = fields.Float('Weight')
    responsible_physician_id = fields.Many2one('medical.physician','Doctor in charge')
    photo = fields.Binary('Picture')
    meconium = fields.Boolean('Meconium')
    neonatal_ambiguous_genitalia = fields.Boolean('Ambiguous Genitalia')
    neonatal_babinski_reflex = fields.Boolean('Babinski Reflex')
    neonatal_barlow = fields.Boolean('Positive Barlow')
    neonatal_blink_reflex = fields.Boolean('Blink Reflex')
    neonatal_erbs_palsy = fields.Boolean('Erbs Palsy')
    neonatal_grasp_reflex =fields.Boolean('Grasp Reflex')
    neonatal_hematoma = fields.Boolean('Hematomas')
    neonatal_hernia = fields.Boolean('Hernia')
    neonatal_moro_reflex = fields.Boolean('Moro Reflex')
    neonatal_ortolani = fields.Boolean('Positive Ortolani')
    neonatal_palmar_crease = fields.Boolean('Transversal Palmar Crease')
    neonatal_polydactyly = fields.Boolean('Polydactyly')
    neonatal_rooting_reflex = fields.Boolean('Rooting Reflex')
    neonatal_stepping_reflex = fields.Boolean('Stepping Reflex')
    neonatal_sucking_reflex = fields.Boolean('Sucking Reflex')
    neonatal_swimming_reflex = fields.Boolean('Swimming Reflex')
    neonatal_syndactyly = fields.Boolean('Syndactyly')
    neonatal_talipes_equinovarus = fields.Boolean('Talipes Equinovarus')
    neonatal_tonic_neck_reflex = fields.Boolean('Tonic Neck Reflex')
    died_at_delivery = fields.Boolean('Died at delivery room')
    mother_died_at_delivery = fields.Boolean('Mother Died at delivery room')
    died_being_transferred = fields.Boolean('Died at Transfered')
    mother_died_being_transferred = fields.Boolean('Mother Died at Transfered')
    died_at_the_hospital = fields.Boolean('Died at the hospital')
    mother_died_at_the_hospital = fields.Boolean('Mother Died at the hospital')
    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('hospitalized', 'Hospitalized'), ('icu', 'I.C.U'), ('cancel', 'Cancel'),
         ('done', 'Discharged')], string="State", default="draft")
    reanimation_aspiration = fields.Boolean('Aspiration')
    reanimation_intubation = fields.Boolean('Intubation')
    reanimation_mask = fields.Boolean('Mask')
    reanimation_oxygen = fields.Boolean('Oxygen')
    reanimation_stimulation = fields.Boolean('Stimulation')
    test_audition = fields.Boolean('Audition')
    test_billirubin = fields.Boolean('Billirubin')
    test_chagas = fields.Boolean('Chagas')
    test_metabolic = fields.Boolean('Metabolic ("heel stick screening")')
    test_toxo = fields.Boolean('Toxoplasmosis')
    test_vdrl = fields.Boolean('VDRL')
    still_birth = fields.Boolean('Stillbirth')
    mother_still_birth = fields.Boolean('Mother Stillbirth')
    time_of_death = fields.Datetime('Time of Death')
    mother_time_of_death = fields.Datetime('Mother Time of Death')
    notes = fields.Text('Notes')
    cause_of_death = fields.Many2one('medical.pathology','Cause Of Death')
    mother_cause_of_death = fields.Many2one('medical.pathology','Mother Cause Of Death')
    congenital_disease_ids = fields.One2many('medical.patient.disease', 'new_born_id')
    medication_ids = fields.One2many('medical.patient.medication', 'new_born_id')
    apgar_score_ids = fields.One2many('medical.neomatal.apgar', 'new_born_id')
    medical_hospital_bed_id = fields.Many2one('medical.hospital.bed', string="Hospital Bed")
    ward_id = fields.Many2one('medical.hospital.ward', string='Ward')
    blood_type = fields.Selection([('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('O', 'O')], string="Blood Type")
    rh = fields.Selection([('-+', '+'), ('--', '-')], string="Rh")
    count_invoice = fields.Integer("Count Invoice", compute="_compute_count_invoice")            

    def _compute_count_invoice(self):
        for record in self:
            record.count_invoice = len(self.env['account.move'].search([('invoice_origin', '=', record.name)]))

    @api.onchange('medical_hospital_bed_id')
    def _onchange_medical_hospital_bed_id(self):
        if self.medical_hospital_bed_id and self.medical_hospital_bed_id.medical_hospital_ward_d:
            self.ward_id = self.medical_hospital_bed_id.medical_hospital_ward_d.id

    @api.model_create_multi
    def create(self,vals):
        for val in vals:
            val['name'] = self.env['ir.sequence'].next_by_code('new_born_seq')
            if val.get('baby_name'):
                patient = self.env['medical.patient'].create({'patient_name': val.get('baby_name')})
                if patient:
                    val['patient_id'] = patient.id
        return super(medical_newborn, self).create(vals)

    def write(self, vals):
        for record in self:
            if vals.get('baby_name') and record.patient_id:
                record.patient_id.write({'patient_name': vals.get('baby_name')})
        return super(medical_newborn, self).write(vals)

    def print_card(self):
        return self.env.ref('healthcare_management.report_print_newborn_card').report_action(self)

    def registration_confirm(self):
        self.write({'state': 'confirmed'})

    def registration_admission(self):
        self.write({'state': 'hospitalized'})
        if not self.medical_hospital_bed_id:
            raise ValidationError('First You have to select Bed!')
        self.medical_hospital_bed_id.write({'state': 'occuiped'})

    def registration_cancel(self):
        self.write({'state': 'cancel'})
        self.medical_hospital_bed_id.write({'state': 'free'})

    def patient_discharge(self):
        self.write({'state': 'done', 'dismissed': fields.Datetime.now()})
        self.medical_hospital_bed_id.write({'state': 'free'})
        sale_journals = self.env['account.journal'].sudo().search([('type','=','sale')])
        if self.state == 'done':
            invoice = self.env['account.move'].create({
                'name': self.env['ir.sequence'].next_by_code('pres_inv_seq'),
                'invoice_origin': self.name or '',
                'move_type': 'out_invoice',
                'ref': self.name or '',
                'journal_id':sale_journals and sale_journals[0].id or False ,
                'partner_id': self.patient_id.patient_id.id,
                'invoice_date': date.today(),
                'partner_shipping_id':self.patient_id.patient_id.id,
                'currency_id':self.patient_id.patient_id.currency_id.id or self.env.user.currency_id.id,
                'invoice_payment_term_id': False,
                'fiscal_position_id': self.patient_id.patient_id.property_account_position_id.id,
                'team_id': False,
                'company_id':self.patient_id.patient_id.company_id.id or False ,
            })
            if self.medical_hospital_bed_id and self.medical_hospital_bed_id.hospital_bed_product_id:
                invoice.write({'invoice_line_ids': [
                    (0,0, {
                        'product_id':self.medical_hospital_bed_id.hospital_bed_product_id.id,
                        'name': self.medical_hospital_bed_id.hospital_bed_product_id.display_name or '',
                        'product_uom_id': self.medical_hospital_bed_id.hospital_bed_product_id.uom_id.id,
                        'price_unit': self.medical_hospital_bed_id.hospital_bed_product_id.lst_price,
                        'move_name': self.medical_hospital_bed_id.hospital_bed_product_id.name or '',
                })]})
            if invoice:
                invoice.action_post()

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