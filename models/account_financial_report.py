from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountFinancialReport(models.Model):
    _inherit = 'account.financial.report'

    is_represents_an_account = fields.Boolean(
        string='Represents an account', default=False)
    represent_account_id = fields.Many2one(
        comodel_name='account.account', string='Represented Account')
    post_to = fields.Selection(
        [("lr", "Labar/Rugi"), ("neraca", "Neraca Akhir")], string='Post to', default="neraca")
    report_group_id = fields.Many2one(
        comodel_name='account.financial.report',
        string='Report Group',
        ondelete='restrict'
    )
    show_value = fields.Boolean(string='Show Value', default=True)
    indentation_style = fields.Selection([("0", "Normal"), ("1", "Tab 1"), (
        "2", "Tab 2"), ("3", "Tab 3")], string='Indentation Style', default='0')
