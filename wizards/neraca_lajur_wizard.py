from calendar import monthrange
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from pprint import pprint
import datetime


class NeracaLajurWizard(models.TransientModel):
    _name = 'neraca.lajur.wizard'

    date_period = fields.Date(
        string='Date from', default=fields.Date.today(), required=True)
    date_from = fields.Date(
        string='Date from', default=fields.Date.today(), required=True)
    date_to = fields.Date(
        string='Date from', default=fields.Date.today(), required=True)
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        required=True,
        default=lambda self: self.env.user.company_id
    )
    with_zero_balance = fields.Boolean(
        string='With zero balance', default=True)
    month_period = fields.Char(string='Month Periode')

    @api.onchange('date_period')
    def onchange_date_period(self):
        self.update({
            'month_period': self.date_period.strftime("%B %Y")
        })

    def _compute_account_balance(self, account):
        res = []
        fields = {'begining_debit','begining_credit', 'debit', 'credit',  'ending_debit', 'ending_credit'}
        
        begining_move_lines = self.env['account.move.line'].search([
            '&', '&',
            ('move_id.state', '=', 'posted'),
            ('date', '<', self.date_from),
            ('account_id', '=', account.id)
        ])
        begining_debit = sum(begining_move_lines.mapped('debit'))
        begining_credit = sum(begining_move_lines.mapped('credit'))

        account_move_lines = self.env['account.move.line'].search([
            '&', '&', '&',
            ('move_id.state', '=', 'posted'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('account_id', '=', account.id)
        ])
        current_debit = sum(account_move_lines.mapped('debit'))
        current_credit = sum(account_move_lines.mapped('credit'))

        res = {
            'begining_debit': begining_debit,
            'begining_credit': begining_credit,
            'debit': current_debit,
            'credit': current_credit,
            'ending_debit': begining_debit + current_debit,
            'ending_credit': begining_credit + current_credit,
        }
        return res

    def _compute_report_balance(self, report):
        res = {
            'begining_debit': 0,
            'begining_credit': 0,
            'debit': 0,
            'credit': 0,
            'ending_debit': 0,
            'ending_credit': 0,
        }
        fields = {'begining_debit','begining_credit', 'debit', 'credit',  'ending_debit', 'ending_credit'}

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
        report_line = []

        acc_financial_report = self.company_id.neraca_lajur_report_id
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
                'begining_debit': 0,
                'begining_credit': 0,
                'debit': 0,
                'credit': 0,
                
                'ending_debit': 0,
                'ending_credit': 0,
                'lr_debit': 0,
                'lr_creidt': 0,
                'neraca_debit': 0,
                'neraca_credit': 0,
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
                    'begining_debit': 0,
                    'begining_credit': 0,
                    'debit': 0,
                    'credit': 0,
                    
                    'ending_debit': 0,
                    'ending_credit': 0,
                    'lr_debit': 0,
                    'lr_credit': 0,
                    'neraca_debit': 0,
                    'neraca_credit': 0,
                    'level': report_item.level,
                    'has_child': True
                })
                vals.update(self._compute_report_balance(report_item))
                report_line.append(vals.copy())

            elif report_item.type == 'account_type':
                vals.update({
                    'is_parent': True,
                    'name': report_item.name,
                    'begining_debit': 0,
                    'begining_credit': 0,
                    'debit': 0,
                    'credit': 0,
                    
                    'ending_debit': 0,
                    'ending_credit': 0,
                    'lr_debit': 0,
                    'lr_credit': 0,
                    'neraca_debit': 0,
                    'neraca_credit': 0,
                    'level': report_item.level,
                    'has_child': True
                })
                vals.update(self._compute_report_balance(report_item))
                report_line.append(vals.copy())

            elif report_item.type == 'account_report':
                report_line.append(vals.copy())

        return report_line

    def action_submit(self, doc_type):
        if self.company_id.neraca_lajur_report_id:
            # set date periode
            last_day = monthrange(self.date_from.year, self.date_from.month)

            first_date = datetime.datetime(
                year=self.date_period.year, month=self.date_from.month, day=1)
            last_date = datetime.datetime(
                year=self.date_period.year, month=self.date_from.month, day=last_day[1])

            self.date_from = first_date.date()
            self.date_to = last_date.date()
            self.month_period = self.date_from.strftime("%B %Y")

            if doc_type == 'pdf':
                return self.env.ref('bp_neraca_saldo_pdam.action_report_neraca_lajur_pdam').report_action(self)
            elif doc_type == 'excel':
                print('cetak excel')
            elif doc_type == 'html':
                return self.env.ref('bp_neraca_saldo_pdam.action_report_neraca_lajur_pdam_html').report_action(self)
        else:
            raise UserError('Neraca Lajur Report is not set.')

    def action_pdf(self):
        return self.action_submit('pdf')

    def process_wizard(self):
        return self.action_submit('html')
