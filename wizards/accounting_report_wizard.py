from calendar import monthrange
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from pprint import pprint
import datetime


class AccountingReportWizard(models.TransientModel):
    _name = 'accounting.report.wizard'
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

    @api.onchange('date_from')
    def onchange_date_from(self):
        self.month_period = self.date_from.strftime("%B")

    # def _get_child_financial_report(self, parent_report_item, report_line):
    #     # print(parent_report_item.name)
    #     # print(parent_report_item._get_children_by_order())
    #     # print(parent_report_item.name)
    #     vals = {
    #         'is_parent': False,
    #         'code': '',
    #         'name': parent_report_item.name,
    #         'begining': 0,
    #         'debit': 0,
    #         'credit': 0,
    #         'ending': 0,
    #         'anggaran_bulan': 0,
    #         'pencapaian_bulan': 0,
    #         'anggaran_tahun': 0,
    #         'pencapaian_tahun': 0,
    #         'level': parent_report_item.level
    #     }

    #     if parent_report_item.type == 'sum':
    #         # print('Sum of report')
    #         x = ''
    #     elif parent_report_item.type in ['accounts', 'account_type']:
    #         if parent_report_item.type == 'accounts':
    #             accounts = parent_report_item.account_ids
    #         else:
    #             accounts = self.env['account.account'].search(
    #                 [('user_type_id', 'in', parent_report_item.account_type_ids.ids)])

    #         for account in accounts:
    #             vals['code'] = account.code
    #             vals['name'] = account.name
    #     elif parent_report_item.type == 'account_report':
    #         # print('get value of report')
    #         x = ''

    #     if len(parent_report_item.children_ids):
    #         # if len(parent_report_item.children_ids) > 0:
    #         vals['is_parent'] = True
    #         for child_item in parent_report_item.children_ids:
    #             self._get_child_financial_report(child_item, report_line)

    #     report_line.append(vals.copy())

    #     # return report_line

    # def get_account_lines(self, data):
    #     lines = []
    #     account_report = self.env['account.financial.report'].search(
    #         [('id', '=', data['account_report_id'][0])])
    #     child_reports = account_report._get_children_by_order()
    #     res = self.with_context(data.get('used_context')
    #                             )._compute_report_balance(child_reports)
    #     if data['enable_filter']:
    #         comparison_res = self.with_context(
    #             data.get('comparison_context'))._compute_report_balance(child_reports)
    #         for report_id, value in comparison_res.items():
    #             res[report_id]['comp_bal'] = value['balance']
    #             report_acc = res[report_id].get('account')
    #             if report_acc:
    #                 for account_id, val in comparison_res[report_id].get('account').items():
    #                     report_acc[account_id]['comp_bal'] = val['balance']

    #     for report in child_reports:
    #         vals = {
    #             'name': report.name,
    #             'balance': res[report.id]['balance'] * report.sign,
    #             'type': 'report',
    #             'level': bool(report.style_overwrite) and report.style_overwrite or report.level,
    #             # used to underline the financial report balances
    #             'account_type': report.type or False,
    #         }
    #         if data['debit_credit']:
    #             vals['debit'] = res[report.id]['debit']
    #             vals['credit'] = res[report.id]['credit']

    #         if data['enable_filter']:
    #             vals['balance_cmp'] = res[report.id]['comp_bal'] * report.sign

    #         lines.append(vals.copy())
    #         if report.display_detail == 'no_detail':
    #             # the rest of the loop is used to display the details of the financial report, so it's not needed here.
    #             continue

    #         if res[report.id].get('account'):
    #             sub_lines = []
    #             for account_id, value in res[report.id]['account'].items():
    #                 # if there are accounts to display, we add them to the lines with a level equals to their level in
    #                 # the COA + 1 (to avoid having them with a too low level that would conflicts with the level of data
    #                 # financial reports for Assets, liabilities...)
    #                 flag = False
    #                 account = self.env['account.account'].browse(account_id)
    #                 vals = {
    #                     'code': account.code,
    #                     'name': account.name,
    #                     'balance': value['balance'] * report.sign or 0.0,
    #                     'type': 'account',
    #                     'level': report.display_detail == 'detail_with_hierarchy' and 4,
    #                     'account_type': account.internal_type,
    #                 }
    #                 if data['debit_credit']:
    #                     vals['debit'] = value['debit']
    #                     vals['credit'] = value['credit']
    #                     if not account.company_id.currency_id.is_zero(vals['debit']) or not account.company_id.currency_id.is_zero(vals['credit']):
    #                         flag = True
    #                 if not account.company_id.currency_id.is_zero(vals['balance']):
    #                     flag = True
    #                 if data['enable_filter']:
    #                     vals['balance_cmp'] = value['comp_bal'] * report.sign
    #                     if not account.company_id.currency_id.is_zero(vals['balance_cmp']):
    #                         flag = True
    #                 if flag:
    #                     sub_lines.append(vals.copy())
    #             lines += sorted(sub_lines,
    #                             key=lambda sub_line: sub_line['name'])
    #     return lines

    # def _compute_report_balance(self,account_financial_report):
    #     balance = {}
    #     if account_financial_report.type == 'sum':
    #         print('report item is sum')
    #         for child in account_financial_report.children_ids:
    #             print(child.name)
    #             new_balance = self._compute_account_balance(child)
    #             balance['debit'] += new_balance['debit']
    #             balance['credit'] += new_balance['credit']
    #             balance['balance'] += new_balance['balance']
    #     elif account_financial_report.type in ['accounts','account_type']:
    #         print('account is account or account_type')
    #         if account_financial_report.type == 'accounts':
    #             accounts = self.env['account.account'].search([('id','in',account_financial_report.account_ids.ids)])
    #         else:
    #             accounts = self.env['account.account'].search([('user_type_id','in',account_financial_report.account_type_ids.ids)])

    #         account_move_lines = self.env['account.move.line'].search([
    #             '&', '&',
    #             ('move_id.state', '=', 'posted'),
    #             ('date', '>=', self.date_from),
    #             ('date', '<=', self.date_to),
    #         ])

    #         debit = 0
    #         credit = 0
    #         for acc in accounts:
    #             print(acc.name)
    #             aml = account_move_lines.filtered(lambda x: x.account_id.id == acc.id)
    #             pprint(aml)
    #             debit = debit + account_move_lines.filtered(lambda x: x.account_id.id == acc.id).mapped('debit')
    #             credit = credit + account_move_lines.filtered(lambda x: x.account_id.id == acc.id).mapped('credit')
    #         balance = debit-credit
    #         balance['debit'] = debit
    #         balance['credit'] = credit
    #         balance['balance'] = balance

    #     return balance

    def _compute_account_balance(self, account):
        res = []
        fields = {'beginig', 'debit', 'credit', 'balance', 'ending'}
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
        res = {
            'begining': sum(begining_move_lines.mapped('balance')),
            'debit': sum(account_move_lines.mapped('debit')),
            'credit': sum(account_move_lines.mapped('credit')),
            'ending': sum(begining_move_lines.mapped('balance')) + sum(account_move_lines.mapped('balance')),
        }
        return res

    def _compute_report_balance(self, report):
        res = {
            'begining': 0,
            'debit': 0,
            'credit': 0,
            'ending': 0,
        }
        fields = ['begining','debit','credit','ending']

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

            if self.company_id.neraca_saldo_report_id:
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
                        'anggaran_bulan': 0,
                        'pencapaian_bulan': 0,
                        'anggaran_tahun': 0,
                        'pencapaian_tahun': 0,
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
                            'anggaran_bulan': 0,
                            'pencapaian_bulan': 0,
                            'anggaran_tahun': 0,
                            'pencapaian_tahun': 0,
                            'level': report_item.level,
                            'has_child': True
                        })
                        report_line.append(vals.copy())

                        accounts = report_item.account_ids

                        for acc in accounts:
                            vals.update({
                                'is_parent': False,
                                'code': acc.code,
                                'name': acc.name,
                                # 'begining': 0,
                                # 'debit': sum(account_move_lines.mapped('debit')),
                                # 'credit': sum(account_move_lines.mapped('credit')),
                                # 'balance': sum(account_move_lines.mapped('debit')) - sum(account_move_lines.mapped('credit')),
                                # 'ending': 0,
                                'anggaran_bulan': 0,
                                'pencapaian_bulan': 0,
                                'anggaran_tahun': 0,
                                'pencapaian_tahun': 0,
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
                            'anggaran_bulan': 0,
                            'pencapaian_bulan': 0,
                            'anggaran_tahun': 0,
                            'pencapaian_tahun': 0,
                            'level': report_item.level,
                            'has_child': True
                        })
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
                                # 'begining': 0,
                                # 'debit': sum(account_move_lines.mapped('debit')),
                                # 'credit': sum(account_move_lines.mapped('credit')),
                                # 'balance': sum(account_move_lines.mapped('debit')) - sum(account_move_lines.mapped('credit')),
                                # 'ending': 0,
                                'anggaran_bulan': 0,
                                'pencapaian_bulan': 0,
                                'anggaran_tahun': 0,
                                'pencapaian_tahun': 0,
                                'level': report_item.level,
                                'has_child': False
                            })

                            vals.update(self._compute_account_balance(acc))

                            report_line.append(vals.copy())

                    elif report_item.type == 'account_report':
                        report_line.append(vals.copy())

                return report_line

            else:
                raise UserError('Neraca Saldo Report is not set.')

    def process_wizard(self):

        # set date periode
        last_day = monthrange(self.date_from.year, self.date_from.month)

        first_date = datetime.datetime(
            year=self.date_from.year, month=self.date_from.month, day=1)
        last_date = datetime.datetime(
            year=self.date_from.year, month=self.date_from.month, day=last_day[1])

        self.date_to = last_date.date()
        self.date_from = first_date.date()

        return self.env.ref('bp_neraca_saldo_pdam.action_report_neraca_saldo_pdam').report_action(self)
