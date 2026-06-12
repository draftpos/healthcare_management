# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

class medical_genetic_risk(models.Model):
    _name = 'medical.genetic.risk'
    _rec_name = 'long_name'
    _description = "Medical Genetic Risk"

    name = fields.Char(string="Name")
    chromosome = fields.Char(string="Affected Chromosome",help="Name of the affected chromosome")
    location = fields.Char(string="Affected organ",help="Locus of the chromosome")
    info = fields.Text(string="Information",help="Name of the protein(s) affected")
    long_name = fields.Char(string="Official Long Name")
    dominance = fields.Selection([('dominant','Dominant'),('recessive','Recessive')],string="Dominance")
    gene = fields.Char(string="Gene ID",help="default code from NCBI Entrez database.")

    def _valid_field_parameter(self, field, name):
        return name == 'sort' or super()._valid_field_parameter(field, name)
