# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    visiting_card = fields.Integer('Number Of Visiting Card', default=1)
