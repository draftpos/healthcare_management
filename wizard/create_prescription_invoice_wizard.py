# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import  ValidationError, UserError


class create_prescription_invoice(models.TransientModel):
    _name = 'create.prescription.invoice'
    _description = "Create Prescription Invoice"

    def create_prescription_invoice(self):
        active_ids = self.env.context.get('active_ids')
        active_ids = active_ids or False
        lab_req_obj = self.env['medical.prescription.order']
        account_invoice_obj  = self.env['account.move']
        inv_list =[]
        lab_reqs = lab_req_obj.sudo().browse(active_ids)
        for lab_req in lab_reqs:
            if len(lab_req.prescription_line_ids) < 1:
                raise ValidationError('At least one prescription line is required.')
            if lab_req.is_invoiced == True:
                raise ValidationError('All ready Invoiced.')
            company_id = self.env.user.company_id.id 
            sale_journals = self.env['account.journal'].search([
                ('type', '=', 'sale'),
                ('company_id', '=', company_id)
            ])
            invoice_vals = {
                'name': self.env['ir.sequence'].next_by_code('pres_inv_seq'),
                'invoice_origin': lab_req.name or '',
                'move_type': 'out_invoice',
                'ref': lab_req.name or '',
                'journal_id': sale_journals[0].id if sale_journals else False,
                'partner_id': lab_req.patient_id.patient_id.id,
                'invoice_date': date.today(),
                'partner_shipping_id':lab_req.patient_id.patient_id.id,
                'currency_id':lab_req.patient_id.patient_id.currency_id.id ,
                'invoice_payment_term_id': False,
                'fiscal_position_id': lab_req.patient_id.patient_id.property_account_position_id.id,
                'team_id': False,
                'company_id': self.env.user.company_id.id
            }

            res = account_invoice_obj.create(invoice_vals)
            list_of_vals=[]
            for p_line in lab_req.prescription_line_ids: 
            
                invoice_line_account_id = False
                if p_line.medicament_id.product_id.id:
                    invoice_line_account_id = p_line.medicament_id.product_id.property_account_income_id.id or p_line.medicament_id.product_id.categ_id.property_account_income_categ_id.id or False
                if not invoice_line_account_id:
                    company = self.env.company
                    if hasattr(company, 'default_income_account_id') and company.default_income_account_id:
                        invoice_line_account_id = company.default_income_account_id.id
                    elif sale_journals and sale_journals.default_account_id:
                        invoice_line_account_id = sale_journals.default_account_id.id
                    else:
                        income_account = self.env['account.account'].search([
                            ('account_type', '=', 'income'),
                            ('company_id', '=', company_id)
                        ], limit=1)
                        if income_account:
                            invoice_line_account_id = income_account.id
                if not invoice_line_account_id:
                    raise UserError(
                        _('There is no income account defined for this product: "%s". You may have to install a chart of account from Accounting app, settings menu.') %
                        (p_line.medicament_id.product_id.name,))

                invoice_line_vals = {
                    'name': p_line.medicament_id.product_id.display_name or '',
                    'move_name': p_line.name or '',
                    'account_id': invoice_line_account_id,
                    'price_unit':p_line.medicament_id.product_id.lst_price,
                    'product_uom_id': p_line.medicament_id.product_id.uom_id.id,
                    'quantity': p_line.quantity,
                    'product_id':p_line.medicament_id.product_id.id ,
                }
                list_of_vals.append((0,0,invoice_line_vals))

            inv_list.append(res.id)
            if res:                     
                imd = self.env['ir.model.data']
                lab_reqs.write({'is_invoiced': True}) 
                action = self.env.ref('account.action_move_out_invoice_type')
                list_view_id = imd.sudo()._xmlid_to_res_id('account.view_invoice_tree')
                form_view_id = imd.sudo()._xmlid_to_res_id('account.view_move_form')
                result = {      
                    'name': action.name,
                    'help': action.help,
                    'type': action.type,
                    'views': [ (list_view_id ,'list'),(form_view_id,'form')],
                    'target': action.target,
                    'context': action.context,
                    'res_model': action.res_model,
                }
                if res:
                    result['domain'] = "[('id','in',%s)]" % inv_list
        return result
