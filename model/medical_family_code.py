# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class medical_family_code(models.Model):
    _name = "medical.family_code"
    _description = "Medical Family Code"

    name = fields.Char(string="Name", required=True)
    operational_sector_id = fields.Many2one('medical.operational_sector', string="Operational Sector")
    members_ids = fields.Many2many('res.partner',string="Members")
    info = fields.Text(string="Extra info")
    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)
    fam_apgar_help = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Help from family',
        help="Is the patient satisfied with the level of help coming from the family when there is a problem ?",
        sort=False)
    fam_apgar_discussion = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Problems discussion',
        help="Is the patient satisfied with the level talking over the problems as family ?", sort=False)
    fam_apgar_decisions = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Decision making',
        help="Is the patient satisfied with the level of making important decisions as a group ?", sort=False)
    fam_apgar_timesharing = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Time sharing',
        help="Is the patient satisfied with the level of time that they spend together ?", sort=False)
    fam_apgar_affection = fields.Selection([
        ('None', ''),
        ('0', 'None'),
        ('1', 'Moderately'),
        ('2', 'Very much'),
    ], 'Family affection',
        help="Is the patient satisfied with the level of affection coming from the family ?", sort=False)
    
