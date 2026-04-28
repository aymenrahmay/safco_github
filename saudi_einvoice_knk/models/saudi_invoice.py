# Powered by Kanak Infosystems LLP.
# © 2020 Kanak Infosystems LLP. (<https://www.kanakinfosystems.com>).

import base64
from num2words import num2words
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    invoice_date_supply = fields.Datetime('Date Of Supply')

    def get_product_arabic_name(self, pid):
        IrTranslation = self.env['ir.translation']
        domain = [
            ('name', '=', 'product.product,name'), ('state', '=', 'translated')]
        translation = IrTranslation.search(domain + [('res_id', '=', pid)])
        if translation:
            return translation.value
        else:
            product = self.env['product.product'].browse(int(pid))
            translation = IrTranslation.search(domain + [('res_id', '=', product.product_tmpl_id.id)])
            if translation:
                return translation.value
        return ''

    def amount_word(self, amount):
        language = self.partner_id.lang or 'en'
        language_id = self.env['res.lang'].search([('code', '=', 'ar_AA')])
        if language_id:
            language = language_id.iso_code
        amount_str = str('{:2f}'.format(amount))
        amount_str_splt = amount_str.split('.')
        before_point_value = amount_str_splt[0]
        after_point_value = amount_str_splt[1][:2]
        before_amount_words = num2words(int(before_point_value), lang=language)
        after_amount_words = num2words(int(after_point_value), lang=language)
        amount = before_amount_words + ' ' + after_amount_words
        return amount

    def _amount_total_words(self, amount):
        words_amount = self.currency_id.amount_to_text(amount)
        return words_amount

    @api.model
    def get_qr_code(self):
        def get_qr_encoding(tag, field):
            company_name_byte_array = field.encode('UTF-8')
            company_name_tag_encoding = tag.to_bytes(length=1, byteorder='big')
            company_name_length_encoding = len(company_name_byte_array).to_bytes(length=1, byteorder='big')
            return company_name_tag_encoding + company_name_length_encoding + company_name_byte_array
        for record in self:
            qr_code_str = ''
            seller_name_enc = get_qr_encoding(1, record.company_id.display_name)
            company_vat_enc = get_qr_encoding(2, record.company_id.vat or '')
            # date_order = fields.Datetime.from_string(record.create_date)
            if record.invoice_date_supply:
                time_sa = fields.Datetime.context_timestamp(self.with_context(tz='Asia/Riyadh'), record.invoice_date_supply)
            else:
                time_sa = fields.Datetime.context_timestamp(self.with_context(tz='Asia/Riyadh'), record.create_date)
            timestamp_enc = get_qr_encoding(3, time_sa.isoformat())
            invoice_total_enc = get_qr_encoding(4, str(record.amount_total))
            total_vat_enc = get_qr_encoding(5, str(record.currency_id.round(record.amount_total - record.amount_untaxed)))

            str_to_encode = seller_name_enc + company_vat_enc + timestamp_enc + invoice_total_enc + total_vat_enc
            qr_code_str = base64.b64encode(str_to_encode).decode('UTF-8')
            return qr_code_str


class ResCompany(models.Model):
    _inherit = 'res.company'

    arabic_name = fields.Char('Arabic Name')
    arabic_street = fields.Char('Arabic Street')
    arabic_street2 = fields.Char('Arabic Street2')
    arabic_city = fields.Char('Arabic City')
    arabic_state = fields.Char('Arabic State')
    arabic_country = fields.Char('Arabic Country')
    arabic_zip = fields.Char('Arabic Zip')


class AccountMoveSend(models.AbstractModel):
    _inherit = 'account.move.send'
    _description = "Account Move Send"

    @api.depends('template_id')
    def _compute_mail_attachments_widget(self):
        for wizard in self:
            wizard.mail_attachments_widget = []
            if wizard.mode == 'invoice_single':
                manual_attachments_data = [x for x in wizard.mail_attachments_widget or [] if x.get('custom_field')]
                if wizard.template_id and wizard.template_id.name == 'Invoice Tax: Send by email':
                    result, format = self.env["ir.actions.report"].sudo()._render_qweb_pdf("saudi_einvoice_knk.action_report_tax_invoice", res_ids=wizard.move_ids.ids)
                    data_record = base64.b64encode(result)
                    ir_values = {
                        'name': 'Saudi VAT Invoice.pdf',
                        'type': 'binary',
                        'datas': data_record,
                        'store_fname': data_record,
                        'mimetype': 'application/pdf',
                        'res_model': 'account.move',
                        'res_id': wizard.move_ids.ids[0],
                    }
                    report_attachment = self.env['ir.attachment'].sudo().create(ir_values)
                    wizard.template_id.attachment_ids = [(6, 0, report_attachment.ids)]
                    wizard.mail_attachments_widget = self._get_default_mail_attachments_widget(wizard.move_ids, wizard.template_id) + manual_attachments_data
                else:
                    wizard.mail_attachments_widget = self._get_default_mail_attachments_widget(wizard.move_ids, wizard.template_id) + manual_attachments_data
                if wizard.template_id and wizard.template_id.name == 'Invoice Simplified Tax : Send by email':
                    new_result, format = self.env["ir.actions.report"].sudo()._render_qweb_pdf("saudi_einvoice_knk.action_report_simplified_tax_invoice", res_ids=wizard.move_ids.ids)
                    data_record = base64.b64encode(new_result)
                    ir_values = {
                        'name': 'Saudi Simplified VAT Invoice.pdf',
                        'type': 'binary',
                        'datas': data_record,
                        'store_fname': data_record,
                        'mimetype': 'application/pdf',
                        'res_model': 'account.move',
                        'res_id': wizard.move_ids.ids[0],
                    }
                    new_report_attachment = self.env['ir.attachment'].sudo().create(ir_values)
                    wizard.template_id.attachment_ids = [(6, 0, new_report_attachment.ids)]
                    wizard.mail_attachments_widget = self._get_default_mail_attachments_widget(wizard.move_ids, wizard.template_id) + manual_attachments_data
                else:
                    wizard.mail_attachments_widget = self._get_default_mail_attachments_widget(wizard.move_ids, wizard.template_id) + manual_attachments_data
            else:
                wizard.mail_attachments_widget = []
