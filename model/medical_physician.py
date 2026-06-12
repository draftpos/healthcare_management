# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class medical_physician(models.Model):
    _name = "medical.physician"
    _rec_name = 'name'
    _description = "Medical Physician"

    @api.depends('partner_id')
    def _compute_name(self):
        for rec in self:
            if rec.partner_id:
                rec.name = rec.partner_id.name
            else:
                rec.name = ''

    name = fields.Char('Name', compute='_compute_name')
    partner_id = fields.Many2one('res.partner', 'Physician', required=True, domain=[('is_doctor', '=', True)],)
    institution_partner_id = fields.Many2one(
        'res.partner', domain=[('is_institution', '=', True)], string='Institution')
    speciality_id = fields.Many2one(
        'medical.speciality', 'Speciality', required=True)
    code = fields.Char('Id')
    info = fields.Text('Extra Info')

    def action_open_appointments(self):
        appointments = self.env['medical.appointment'].search(
            [('doctor_id', '=', self.id)])
        if appointments:
            action = {
                'name': _('Blood Buy'),
                'view_type': 'calendar',
                'view_mode': 'calendar,form',
                'res_model': 'medical.appointment',
                'type': 'ir.actions.act_window',
                'context': self.env.context,
                'domain': [('id', 'in', appointments.ids)],
            }
            return action



