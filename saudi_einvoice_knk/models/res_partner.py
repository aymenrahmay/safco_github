from odoo import api, fields, models, exceptions
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import config


class ResPartner(models.Model):
    _inherit = "res.partner"

    name = fields.Char(required=True,store=True, readonly=False,translate= False)
    street = fields.Char(translate=False)
    street2 = fields.Char(translate=False)
    city = fields.Char(translate=False)

