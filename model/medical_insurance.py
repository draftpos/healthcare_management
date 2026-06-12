# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class medical_insurance(models.Model):
    _name = 'medical.insurance'
    _rec_name = 'number'
    _description = "Medical Insurance"

    number = fields.Char('Number')
    medical_insurance_partner_id = fields.Many2one('res.partner',' Owner', required=True)
    patient_id = fields.Many2one('res.partner', 'Owner')
    type =  fields.Selection([('state','State'),('private','Private'),('labour_union','Labour Union/ Syndical')],'Insurance Type')
    member_since= fields.Date('Member Since')
    insurance_compnay_id = fields.Many2one('res.partner',domain=[('is_insurance_company','=',True)],string='Insurance Compnay')
    category = fields.Char('Category')
    notes= fields.Text('Extra Info')
    member_exp = fields.Date('Expiration Date')
    medical_insurance_plan_id = fields.Many2one('medical.insurance.plan','Plan')
    is_file_needed = fields.Boolean('Hospital File')
    is_pf_file = fields.Boolean('PF File ')
    is_pay_slip = fields.Boolean('Pay Slip')
    is_bank_statement = fields.Boolean('Bank Statement')
    is_medical_bill = fields.Boolean('Medical Bill')
