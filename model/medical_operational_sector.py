# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class medical_operational_sector(models.Model):
    _name = 'medical.operational_sector'
    _description = "Medical Operation Sector"
    
    name = fields.Char(string="Name",required=True,size=128)
    info = fields.Text(string="Extra Info")
    operational_area_id = fields.Many2one('medical.operational_area',string="Operational Area")
