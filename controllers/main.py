# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
import logging
import werkzeug
import odoo.http as http
from odoo import SUPERUSER_ID, _
from odoo.http import request
from odoo.tools.misc import get_lang


class WebsiteFeedback(http.Controller):

    @http.route('/rate/<string:token>/<int:rate>', type='http', auth="public", website=True)
    def action_open_rating(self, token, rate, **kwargs):
        if rate not in (1, 3, 5):
            raise ValueError(
                _("Incorrect rating: should be 1, 3 or 5 (received %d)"), rate)
        lang = get_lang(request.env).code
        action = request.env['ir.ui.view'].with_context(lang=lang)._render_template('healthcare_management.appointment_rating_external_page_submit', {
            'rate_names': {
                5: _("Satisfied"),
                3: _("Okay"),
                1: _("Dissatisfied"),
            },
            'rate': rate,
            'token': token,
        })
        return action

    @http.route(['/rate/submit_feedback'], type="http", auth="public", methods=['post', 'get'], website=True)
    def action_submit_rating(self, appointment=0, rate=0, **kwargs):
        if request.httprequest.method == "POST":
            rate = int(rate)
            appointment = int(appointment)
            if rate not in (1, 3, 5):
                raise ValueError(
                    _("Incorrect rating: should be 1, 3 or 5 (received %d)"), rate)
            if kwargs.get('token'):
                appointment_id = request.env['medical.appointment'].sudo().search([('access_token', '=', kwargs.get('token'))], limit=1)
                if appointment_id:
                    feedback = 'Normal'
                    if rate == 1:
                        feedback = 'Bad'
                    elif rate == 5:
                        feedback = 'Good'
                    message = f"Doctor get {feedback} Perfomance from this patients."
                    msg = ''
                    if kwargs.get('feedback'):
                        msg = kwargs.get('feedback')
                        message = message + f'Patient Feedback: {msg}'
                    appointment_id.sudo().message_post(body=message)
        lang = get_lang(request.env).code
        return request.env['ir.ui.view'].with_context(lang=lang)._render_template('healthcare_management.appointment_rating_page_view')
