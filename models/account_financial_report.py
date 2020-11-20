from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountFinancialReport(models.Model):
    _inherit = 'account.financial.report'

    is_represents_an_account = fields.Boolean(
        string='Represents an account', default=False)
    represent_account_id = fields.Many2one(
        comodel_name='account.account', string='Represented Account')
