# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class medical_patient_ambulatory_care_medicament(models.Model):
    _name = 'medical.patient.ambulatory_care.medicament'
    _description = "Medical Patient Ambulatory Care Medicament"
    
    medical_medicament_id = fields.Many2one('medical.medicament',string='Medicament',required=True)
    quantity = fields.Integer(string="Quantity")
    lot_id = fields.Many2one('stock.lot',string='Lot',required=True)
    short_comment = fields.Char(string='Comment')
    product_id = fields.Many2one('product.product',string='Product')
    medical_patient_rounding_ambulatory_care_medicament_id = fields.Many2one('medical.patient.ambulatory_care',string="Medicaments") 

