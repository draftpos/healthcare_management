# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
from odoo.exceptions import ValidationError
from odoo import api, fields, models, _
from datetime import date,datetime,timedelta

class appointment_start_end_wizard(models.TransientModel):
    _name = "appointment.start.end.wizard"
    _description = "Appointment Start End Wizard"

    appointment_start_end_physician_ids = fields.Many2many('medical.physician',string='Name Of Physician')
    speciality_ids = fields.Many2many('medical.speciality',string='Speciality') 
    start_date = fields.Date("Start Date")
    end_date = fields.Date('End Date')

    @api.constrains('start_date', 'end_date')
    def check_dates(self):
        for rec in self:
            if rec.start_date > rec.end_date:
                raise ValidationError(_('The start date of the time off must be earlier than the end date.'))

    @api.onchange('appointment_start_end_physician_ids')
    def onchange_appointment_start_end_physician_ids(self):
        if self.appointment_start_end_physician_ids:
            speciality = self.appointment_start_end_physician_ids.mapped('speciality_id')
            self.speciality_ids = speciality.ids

    def show_record(self):
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']
        
        result = mod_obj._xmlid_lookup("%s.%s" %('healthcare_management','action_medical_appointment'))[1:3]
        id = result and result[1] or False
        if id:
            current_action = act_obj.sudo().browse(id)
            result = current_action.read()[0]
            domain = []        
            if self.start_date:
                from_date = datetime.strptime(str(self.start_date), "%Y-%m-%d")
                from_date = from_date.strftime("%Y-%m-%d %H:%M:%S")
                domain.append(('appointment_date','>=',from_date))
                
            if self.end_date:
                to_date = datetime.strptime(str(self.end_date), "%Y-%m-%d")
                to_date = to_date+timedelta(days=1)
                to_date = to_date.strftime("%Y-%m-%d %H:%M:%S")
                domain.append(('appointment_end','<=',to_date))
            
            if self.appointment_start_end_physician_ids:
                domain.append(('doctor_id','in',self.appointment_start_end_physician_ids.ids))
            if self.speciality_ids:
                domain.append(('speciality_id','in',self.speciality_ids.ids))
            result['domain'] = domain
            result['binding_view_types'] = 'form'
            datas = self.env['medical.appointment'].search(domain)
            return result
