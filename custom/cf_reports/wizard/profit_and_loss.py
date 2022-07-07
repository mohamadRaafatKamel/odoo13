# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.exceptions import ValidationError


class AccountBalanceReport(models.TransientModel):
    # _inherit = "account.common.account.report"
    _name = 'account.profit.and.loss.report'
    _description = 'Profit and Loss Report'

    date_from = fields.Date(string='Start Date')
    date_to = fields.Date(string='End Date')

    #  print report pdf
    def action_print_pl_bln_pdf(self):
        # Check that date must be filled
        data = self.read()[0]
        if not data.get('date_from') or not data.get('date_to'):
            raise ValidationError("You must select date From & To")
        mydata = {
            'form_data': self.read()[0],
        }
        # data = self.pre_print_report(data)
        # records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref('cf_reports.action_profit_and_loss_pdf_report').report_action(self, data=mydata)
        # print(mydata);

    #  print report Xlsx
    def action_print_pl_bln_xlsx(self):
        # Check that date must be filled
        data = self.read()[0]
        if not data.get('date_from') or not data.get('date_to'):
            raise ValidationError("You must select date From & To")
        mydata = {
            'form_data': self.read()[0],
        }
        # print(self.read()[0])
        # data = self.pre_print_report(data)
        # records = self.env[data['model']].browse(data.get('ids', []))
        return self.env.ref('cf_reports.action_profit_and_loss_xlsx_report').report_action(self, data=mydata)
