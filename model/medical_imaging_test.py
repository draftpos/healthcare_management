# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
 
class medical_imaging_test(models.Model):
     _name = 'medical.imaging.test'
     _description = "Medical Imaging Test"
 
     name = fields.Char('Name', required = True)
     code = fields.Char('Code', required = True)
     product_id = fields.Many2one('product.product','Service', required = True)
     test_type_id = fields.Many2one('medical.imaging.test.type','Type', required = True)
     
     def _valid_field_parameter(self, field, name):
          return name == 'sort' or super()._valid_field_parameter(field, name)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
