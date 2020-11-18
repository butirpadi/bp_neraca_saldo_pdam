from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountingReportWizard(models.TransientModel):
    _name = 'accounting.report.wizard'
    _description = 'Wizard for generating Accounting Report : Neraca Saldo, Neraca Lajur, Pencapaian Laba/Rugi'

    date_from = fields.Date(string='Date from', required=True, )
    date_to = fields.Date(string='Date to', required=True, )
    report_type = fields.Selection([("saldo","Neraca Saldo"),("lajur","Neraca Lajur"),("lr","Pencapaian Laba/Rugi")], string='Report Type')

    


    