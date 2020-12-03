from calendar import monthrange
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from pprint import pprint
import datetime


class NeracaSaldoWizard(models.TransientModel):
    _name = 'neraca.saldo.wizard'
    _inherit = 'report.accounting_pdf_reports.report_financial'
    _description = 'Wizard for generating Accounting Report : Neraca Saldo, Neraca Lajur, Pencapaian Laba/Rugi'

    date_from = fields.Date(
        string='Date from', default=fields.Date.today(), required=True)
    date_to = fields.Date(
        string='Date to', default=fields.Date.today(), required=True, )
    report_type = fields.Selection([("saldo", "Neraca Saldo"), ("lajur", "Neraca Lajur"), (
        "lr", "Pencapaian Laba/Rugi")], string='Report Type', required=True, )
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.user.company_id
    )
    with_zero_balance = fields.Boolean(
        string='With zero balance', default=True)
    month_period = fields.Char(string='Month Periode')
    budget_plan_id = fields.Many2one(
        comodel_name='bp.simple.budget',
        string='Budget Plan'
    )

    @api.onchange('date_from')
    def onchange_date_from(self):
        self.update({
            'month_period': self.date_from.strftime("%B")
        })

    def _compute_account_balance(self, account):
        res = []
        fields = {'beginig', 'debit', 'credit', 'balance', 'ending'}
        budget_fields = ['bg_jan', 'bg_feb', 'bg_mar', 'bg_apr', 'bg_may',
                         'bg_jun', 'bg_jul', 'bg_aug', 'bg_sept', 'bg_oct', 'bg_nov', 'bg_dec']
        account_move_lines = self.env['account.move.line'].search([
            '&', '&', '&',
            ('move_id.state', '=', 'posted'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('account_id', '=', account.id)
        ])
        begining_move_lines = self.env['account.move.line'].search([
            '&', '&',
            ('move_id.state', '=', 'posted'),
            ('date', '<', self.date_from),
            ('account_id', '=', account.id)
        ])

        budget_line = self.budget_plan_id.line_ids.filtered(
            lambda x: x.account_id.id == account.id)
        bulan = 0
        per_bulan = 0
        tahun = 0
        per_tahun = 0

        if budget_line:
            bulan = budget_line[budget_fields[self.date_from.month - 1]]
            per_bulan = 100 * sum(account_move_lines.mapped('balance')) / budget_line[budget_fields[self.date_from.month - 1]]
            tahun = budget_line.annual_amount
            per_tahun = 100 * (sum(begining_move_lines.mapped('balance')) + sum(account_move_lines.mapped('balance'))) / budget_line.annual_amount


        res = {
            'begining': sum(begining_move_lines.mapped('balance')),
            'debit': sum(account_move_lines.mapped('debit')),
            'credit': sum(account_move_lines.mapped('credit')),
            'ending': sum(begining_move_lines.mapped('balance')) + sum(account_move_lines.mapped('balance')),
            'bulan':  bulan,
            'per_bulan': per_bulan,
            'tahun':  tahun,
            'per_tahun': per_tahun
        }
        return res

    def _compute_report_balance(self, report):
        res = {
            'begining': 0,
            'debit': 0,
            'credit': 0,
            'ending': 0,
            'bulan': 0,
            'per_bulan': 0,
            'tahun': 0,
            'per_tahun': 0
        }
        fields = ['begining', 'debit', 'credit',
                  'ending', 'bulan', 'tahun', 'per_bulan', 'per_tahun']

        if report.type == 'sum':
            for child in report.children_ids:
                new_res = self._compute_report_balance(child)
                for field in fields:
                    res[field] = res[field] + new_res[field]
        elif report.type == 'accounts':
            for account in report.account_ids:
                new_res = self._compute_account_balance(account)
                for field in fields:
                    res[field] = res[field] + new_res[field]
        elif report.type == 'account_type':
            for account in self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)]):
                new_res = self._compute_account_balance(account)
                for field in fields:
                    res[field] = res[field] + new_res[field]
        elif report.type == 'account_report':
            new_res = self._compute_report_balance(report.account_report_id)
            for field in fields:
                res[field] = res[field] + new_res[field]

        return res

    def _get_report_line(self):
        # print('Inside get report line -------------------')
        # print(self.report_type)
        if self.report_type == 'saldo':
            report_line = []

            acc_financial_report = self.company_id.neraca_saldo_report_id
            account_move_lines = self.env['account.move.line'].search([
                '&', '&',
                ('move_id.state', '=', 'posted'),
                ('date', '>=', self.date_from),
                ('date', '<=', self.date_to),
            ])
            # bikinan sendiri
            for report_item in acc_financial_report._get_children_by_order():
                vals = {
                    'is_parent': False,
                    'code': report_item.represent_account_id.code or '',
                    'name': report_item.name,
                    'begining': 0,
                    'debit': 0,
                    'credit': 0,
                    'balance': 0,
                    'ending': 0,
                    'bulan': 0,
                    'tahun': 0,
                    'per_bulan': 0,
                    'per_tahun': 0,
                    'level': report_item.level,
                    'has_child': False
                }

                if len(report_item.children_ids) > 0:
                    vals.update({
                        'has_child': True,
                        'is_parent': True
                    })

                if report_item.type == 'sum':
                    vals.update(self._compute_report_balance(report_item))
                    report_line.append(vals.copy())

                elif report_item.type == 'accounts':
                    vals.update({
                        'is_parent': True,
                        'name': report_item.name,
                        'begining': 0,
                        'debit': 0,
                        'credit': 0,
                        'balance': 0,
                        'ending': 0,
                        'bulan': 0,
                        'tahun': 0,
                        'per_bulan': 0,
                        'per_tahun': 0,
                        'level': report_item.level,
                        'has_child': True
                    })
                    vals.update(self._compute_report_balance(report_item))
                    report_line.append(vals.copy())

                    accounts = report_item.account_ids

                    for acc in accounts:
                        vals.update({
                            'is_parent': False,
                            'code': acc.code,
                            'name': acc.name,
                            'bulan': 0,
                            'per_bulan': 0,
                            'tahun': 0,
                            'per_tahun': 0,
                            'level': report_item.level,
                            'has_child': False
                        })

                        vals.update(self._compute_account_balance(acc))

                        report_line.append(vals.copy())

                elif report_item.type == 'account_type':
                    vals.update({
                        'is_parent': True,
                        'name': report_item.name,
                        'begining': 0,
                        'debit': 0,
                        'credit': 0,
                        'balance': 0,
                        'ending': 0,
                        'bulan': 0,
                        'per_bulan': 0,
                        'tahun': 0,
                        'per_tahun': 0,
                        'level': report_item.level,
                        'has_child': True
                    })
                    vals.update(self._compute_report_balance(report_item))
                    report_line.append(vals.copy())

                    accounts = self.env['account.account'].search(
                        [('user_type_id', 'in', report_item.account_type_ids.ids)])

                    for acc in accounts:
                        account_move_lines = self.env['account.move.line'].search([
                            '&', '&', '&',
                            ('move_id.state', '=', 'posted'),
                            ('date', '>=', self.date_from),
                            ('date', '<=', self.date_to),
                            ('account_id', '=', acc.id)
                        ])
                        vals.update({
                            'is_parent': False,
                            'code': acc.code,
                            'name': acc.name,
                            'bulan': 0,
                            'per_bulan': 0,
                            'tahun': 0,
                            'per_tahun': 0,
                            'level': report_item.level,
                            'has_child': False
                        })

                        vals.update(self._compute_account_balance(acc))

                        report_line.append(vals.copy())

                elif report_item.type == 'account_report':
                    report_line.append(vals.copy())

            return report_line

    def process_wizard(self):
        # check if neraca saldo is set
        if self.company_id.neraca_saldo_report_id:
            # set date periode
            last_day = monthrange(self.date_from.year, self.date_from.month)

            first_date = datetime.datetime(
                year=self.date_from.year, month=self.date_from.month, day=1)
            last_date = datetime.datetime(
                year=self.date_from.year, month=self.date_from.month, day=last_day[1])

            self.date_to = last_date.date()
            self.date_from = first_date.date()
            self.month_period = self.date_from.strftime("%B")

            return self.env.ref('bp_neraca_saldo_pdam.action_report_neraca_saldo_pdam').report_action(self)
        else:
            raise UserError('Neraca Saldo Report is not set.')
