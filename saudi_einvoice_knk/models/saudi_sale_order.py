# -*- coding: utf-8 -*-
# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import base64
from num2words import num2words
from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_quotation_send(self):
        """ Opens a wizard to compose an email, with relevant mail template loaded by default """
        self.ensure_one()
        self.order_line._validate_analytic_distribution()
        lang = self.env.context.get('lang')
        mail_template= self.env.ref('saudi_einvoice_knk.email_template_edi_sale_order', raise_if_not_found=False)
        if mail_template and mail_template.lang:
            lang = mail_template._render_lang(self.ids)[self.id]
        ctx = {
            'default_model': 'sale.order',
            'default_res_id': self.id,
            'default_use_template': bool(mail_template),
            'default_template_id': mail_template.id if mail_template else None,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True,
            'default_email_layout_xmlid': 'mail.mail_notification_layout_with_responsible_signature',
            'proforma': self.env.context.get('proforma', False),
            'force_email': True,
            'model_description': self.with_context(lang=lang).type_name,
        }
        return {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(False, 'form')],
            'view_id': False,
            'target': 'new',
            'context': ctx,
        }

    def action_sale_order_report(self):
        self.ensure_one()
        template = self.env.ref('saudi_einvoice_knk.email_template_edi_sale_order', raise_if_not_found=False)
        lang = False
        if template:
            lang = template._render_lang(self.ids)[self.id]
        if not lang:
            lang = get_lang(self.env).code
        compose_form = self.env.ref('sales.sale_order_send_wizard_form', raise_if_not_found=False)
        ctx = dict(
            default_model='sale.order',
            default_res_id=self.id,
            active_ids=[self.id],
            default_res_model='account.move',
            default_use_template=bool(template),
            default_template_id=template and template.id or False,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="mail.mail_notification_paynow",
            model_description=self.with_context(lang=lang).type_name,
            force_email=True
        )
        return {
            'name': _('Send Commercial offer'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sale.order.send',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }

    def get_product_arabic_name(self, pid):
        IrTranslation = self.env['ir.translation']
        domain = [
            ('name', '=', 'product.product,name'), ('state', '=', 'translated')]
        translation = IrTranslation.search(domain+[('res_id', '=', pid)])
        if translation:
            return translation.value
        else:
            product = self.env['product.product'].browse(int(pid))
            translation = IrTranslation.search(domain + [('res_id', '=', product.product_tmpl_id.id)])
            if translation:
                return translation.value
        return ''
