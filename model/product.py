# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_blood = fields.Boolean('Blood Type')

class ProductProductInherit(models.Model):
    _inherit = 'product.product'

    is_blood = fields.Boolean(related='product_tmpl_id.is_blood', readonly=False)
