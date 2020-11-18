from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ResCompany(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'

    neraca_saldo_report_id = fields.Many2one('account.financial.report', string='Neraca Saldo')
    neraca_lajur_report_id = fields.Many2one('account.financial.report', string='Neraca Lajur')
    laba_rugi_report_id = fields.Many2one('account.financial.report', string='Perbadingan Laba/Rugi')

    