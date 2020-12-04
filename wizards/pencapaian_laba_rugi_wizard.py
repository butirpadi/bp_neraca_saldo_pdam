from calendar import monthrange
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from pprint import pprint
import datetime


class PencapaianLabaRugi(models.TransientModel):
    _name = 'pencapaian.laba.rugi.wizard'
    _inherit = 'report.accounting_pdf_reports.report_financial'
    _description = 'Wizard for generating Accounting Report : Neraca Saldo, Neraca Lajur, Pencapaian Laba/Rugi'

    date_select = fields.Date(
        string='Date', default=fields.Date.today(), required=True)
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
    monthstr = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
                'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

    @api.onchange('date_select')
    def onchange_date_from(self):
        self.update({
            'month_period': self.date_select.strftime("%B")
        })

    def _compute_account_balance(self, account, date_from, date_to):
        res = []
        fields = {'beginig', 'debit', 'credit', 'balance', 'ending'}
        budget_fields = ['bg_jan', 'bg_feb', 'bg_mar', 'bg_apr', 'bg_may',
                         'bg_jun', 'bg_jul', 'bg_aug', 'bg_sep', 'bg_oct', 'bg_nov', 'bg_dec']
        current_move_lines = self.env['account.move.line'].search([
            '&', '&', '&',
            ('move_id.state', '=', 'posted'),
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('account_id', '=', account.id)
        ])
        upto_move_lines = self.env['account.move.line'].search([
            '&', '&',
            ('move_id.state', '=', 'posted'),
            ('date', '<=', date_to),
            ('account_id', '=', account.id)
        ])

        budget_line = self.budget_plan_id.line_ids.filtered(
            lambda x: x.account_id.id == account.id)

        realisasi_bulan = 0
        anggaran_bulan = 0
        penc_bulan = 0
        realisasi_upto = 0
        anggaran_upto = 0
        penc_upto = 0
        anggaran_tahun = 0
        penc_tahun = 0

        if budget_line:
            anggaran_bulan = budget_line[budget_fields[self.date_select.month - 1]]
            penc_bulan = 100 * abs(sum(current_move_lines.mapped('balance'))) / \
                budget_line[budget_fields[self.date_select.month - 1]]

            anggaran_upto = 0
            for i in range(self.date_select.month):
                anggaran_upto += budget_line[budget_fields[i]]
            penc_upto = 100 * \
                abs(sum(upto_move_lines.mapped('balance'))) / anggaran_upto

            anggaran_tahun = budget_line.annual_amount
            penc_tahun = 100 * \
                abs(sum(upto_move_lines.mapped('balance'))) / anggaran_tahun

        res = {
            'realisasi_bulan': sum(current_move_lines.mapped('balance')),
            'anggaran_bulan': anggaran_bulan,
            'penc_bulan': penc_bulan,
            'realisasi_upto': sum(upto_move_lines.mapped('balance')),
            'anggaran_upto': anggaran_upto,
            'penc_upto': penc_upto,
            'anggaran_tahun': anggaran_tahun,
            'penc_tahun':  penc_tahun,
        }
        return res

    def _compute_report_balance(self, report, date_from, date_to):
        res = {
            'realisasi_bulan': 0,
            'anggaran_bulan': 0,
            'penc_bulan': 0,
            'realisasi_upto': 0,
            'anggaran_upto': 0,
            'penc_upto': 0,
            'anggaran_tahun': 0,
            'penc_tahun':  0,
        }
        fields = ['realisasi_bulan',
                  'anggaran_bulan',
                  'penc_bulan',
                  'realisasi_upto',
                  'anggaran_upto',
                  'penc_upto',
                  'anggaran_tahun',
                  'penc_tahun']

        if report.type == 'sum':
            for child in report.children_ids:
                new_res = self._compute_report_balance(
                    child, date_from, date_to)
                for field in fields:
                    res[field] = res[field] + new_res[field]
        elif report.type == 'accounts':
            for account in report.account_ids:
                new_res = self._compute_account_balance(
                    account, date_from, date_to)
                for field in fields:
                    res[field] = res[field] + new_res[field]
        elif report.type == 'account_type':
            for account in self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)]):
                new_res = self._compute_account_balance(
                    account, date_from, date_to)
                for field in fields:
                    res[field] = res[field] + new_res[field]
        elif report.type == 'account_report':
            new_res = self._compute_report_balance(
                report.account_report_id, date_from, date_to)
            for field in fields:
                res[field] = res[field] + new_res[field]

        # add sign
        res['sign'] = report.sign
        
        return res

    def _get_report_line(self):
        last_day = monthrange(self.date_select.year, self.date_select.month)

        first_date = datetime.datetime(
            year=self.date_select.year, month=self.date_select.month, day=1)
        last_date = datetime.datetime(
            year=self.date_select.year, month=self.date_select.month, day=last_day[1])

        report_line = []

        acc_financial_report = self.company_id.laba_rugi_report_id
        current_move_lines = self.env['account.move.line'].search([
            '&', '&',
            ('move_id.state', '=', 'posted'),
            ('date', '>=', first_date.date()),
            ('date', '<=', last_date.date()),
        ])
        # bikinan sendiri
        for report_item in acc_financial_report._get_children_by_order():
            vals = {
                'is_parent': False,
                'code': report_item.represent_account_id.code or '',
                'name': report_item.name,
                'realisasi_bulan': 0,
                'anggaran_bulan': 0,
                'penc_bulan': 0,
                'realisasi_upto': 0,
                'anggaran_upto': 0,
                'penc_upto': 0,
                'anggaran_tahun': 0,
                'penc_tahun':  0,
                'level': report_item.level,
                'has_child': False,
                'sign' : report_item.sign
            }

            if len(report_item.children_ids) > 0:
                vals.update({
                    'has_child': True,
                    'is_parent': True
                })

            if report_item.type == 'sum':
                vals.update(self._compute_report_balance(
                    report_item, first_date.date(), last_date.date()))
                report_line.append(vals.copy())

            elif report_item.type == 'accounts':
                vals.update({
                    'is_parent': True,
                    'name': report_item.name,
                    'level': report_item.level,
                    'has_child': True
                })
                vals.update(self._compute_report_balance(
                    report_item, first_date.date(), last_date.date()))
                report_line.append(vals.copy())

                accounts = report_item.account_ids

                for acc in accounts:
                    vals.update({
                        'is_parent': False,
                        'code': acc.code,
                        'name': acc.name,
                        'level': report_item.level,
                        'has_child': False
                    })

                    vals.update(self._compute_account_balance(
                        acc, first_date.date(), last_date.date()))

                    report_line.append(vals.copy())

            elif report_item.type == 'account_type':
                vals.update({
                    'is_parent': True,
                    'name': report_item.name,
                    'level': report_item.level,
                    'has_child': True
                })
                vals.update(self._compute_report_balance(
                    report_item, first_date.date(), last_date.date()))
                report_line.append(vals.copy())

                accounts = self.env['account.account'].search(
                    [('user_type_id', 'in', report_item.account_type_ids.ids)])

                for acc in accounts:
                    current_move_lines = self.env['account.move.line'].search([
                        '&', '&', '&',
                        ('move_id.state', '=', 'posted'),
                        ('date', '>=', first_date.date()),
                        ('date', '<=', last_date.date()),
                        ('account_id', '=', acc.id)
                    ])
                    vals.update({
                        'is_parent': False,
                        'code': acc.code,
                        'name': acc.name,
                        'level': report_item.level,
                        'has_child': False
                    })

                    vals.update(self._compute_account_balance(
                        acc, first_date.date(), last_date.date()))
                    
                    report_line.append(vals.copy())

            elif report_item.type == 'account_report':
                report_line.append(vals.copy())

            
            pprint(vals)
            print('------------------------------')

        return report_line

    def process_wizard(self):
        # check if neraca saldo is set
        if self.company_id.laba_rugi_report_id:
            # set date periode

            self.month_period = self.date_select.strftime("%B")

            return self.env.ref('bp_neraca_saldo_pdam.action_report_pencapaian_laba_rugi').report_action(self)
        else:
            raise UserError('Pencapaian Laba/Rugi Report is not set.')
