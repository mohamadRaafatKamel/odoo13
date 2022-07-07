# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportProfitAndLossPDF(models.AbstractModel):
    _name = 'report.cf_reports.report_profit_and_loss_document_pdf'

    def account_Profit_and_Loss(self, data):
        # display array
        lines = []
        # create array for all move before date from & to
        moveSQL = """
            SELECT SUM(balance) as balance, ml.parent_state, aa.code, aa.name
             from account_account aa
             LEFT join account_move_line ml
             on aa.id = ml.account_id
             GROUP BY aa.id ,ml.date, ml.parent_state
             HAVING date between '{}' and '{}'
             and ml.parent_state = '{}'
             and CAST(aa.code AS int) > 30000
             ORDER BY aa.code ASC""".format(data['date_from'],data['date_to'], "posted")
        self.env.cr.execute(moveSQL)
        moveAcc = self.env.cr.dictfetchall()

        # Divided array
        revenues_row = []
        other_revenues_row = []
        cost_of_revenues_row = []
        general_expenses_row = []
        depreciation_expenses_row = []
        selling_expenses_row = []
        financing_expenses_row = []

        # sum array
        revenues = other_revenues = total_revenues = 0
        cost_of_revenues = gross_profit = 0
        general_expenses = depreciation_expenses = selling_expenses = financing_expenses = total_expenses = 0
        net_income = 0

        # for last, acc in enumerate(moveAcc):
        i = 0
        arrayLen = len(moveAcc)
        while i < arrayLen:
            if moveAcc[i]['code'][:2] == '31':
                revenues_row.append(moveAcc[i])
                i += 1
                # check if next row have same code
                while True:
                    if i < arrayLen:
                        # if current == next
                        if moveAcc[i - 1]['code'] == moveAcc[i]['code']:
                            revenues_row[-1]['balance'] += moveAcc[i]['balance']
                            i += 1
                        else:
                            break
                    else:
                        break
                revenues += revenues_row[-1]['balance']

            elif moveAcc[i]['code'][:2] == '32':
                other_revenues_row.append(moveAcc[i])
                other_revenues += moveAcc[i]['balance']
                i += 1
                # check if next row have same code
                while True:
                    if i < arrayLen:
                        # if current == next
                        if moveAcc[i - 1]['code'] == moveAcc[i]['code']:
                            other_revenues_row[-1]['balance'] += moveAcc[i]['balance']
                            i += 1
                        else:
                            break
                    else:
                        break
                other_revenues += other_revenues_row[-1]['balance']

            elif moveAcc[i]['code'][:2] == '41':  # -ve value
                cost_of_revenues_row.append(moveAcc[i])
                i += 1
                # check if next row have same code
                while True:
                    if i < arrayLen:
                        # if current == next
                        if moveAcc[i - 1]['code'] == moveAcc[i]['code']:
                            cost_of_revenues_row[-1]['balance'] += moveAcc[i]['balance']
                            i += 1
                        else:
                            break
                    else:
                        break
                cost_of_revenues_row[-1]['balance'] *= -1
                cost_of_revenues += cost_of_revenues_row[-1]['balance']

            elif moveAcc[i]['code'][:2] == '51':  # -ve value
                general_expenses_row.append(moveAcc[i])
                i += 1
                # check if next row have same code
                while True:
                    if i < arrayLen:
                        # if current == next
                        if moveAcc[i - 1]['code'] == moveAcc[i]['code']:
                            general_expenses_row[-1]['balance'] += moveAcc[i]['balance']
                            i += 1
                        else:
                            break
                    else:
                        break
                general_expenses_row[-1]['balance'] *= -1
                general_expenses += general_expenses_row[-1]['balance']

            elif moveAcc[i]['code'][:2] == '52':  # -ve value
                depreciation_expenses_row.append(moveAcc[i])
                i += 1
                # check if next row have same code
                while True:
                    if i < arrayLen:
                        # if current == next
                        if moveAcc[i - 1]['code'] == moveAcc[i]['code']:
                            depreciation_expenses_row[-1]['balance'] += moveAcc[i]['balance']
                            i += 1
                        else:
                            break
                    else:
                        break
                depreciation_expenses_row[-1]['balance'] *= -1
                depreciation_expenses += depreciation_expenses_row[-1]['balance']

            elif moveAcc[i]['code'][:2] == '53':  # -ve value
                selling_expenses_row.append(moveAcc[i])
                i += 1
                # check if next row have same code
                while True:
                    if i < arrayLen:
                        # if current == next
                        if moveAcc[i - 1]['code'] == moveAcc[i]['code']:
                            selling_expenses_row[-1]['balance'] += moveAcc[i]['balance']
                            i += 1
                        else:
                            break
                    else:
                        break
                selling_expenses_row[-1]['balance'] *= -1
                selling_expenses += selling_expenses_row[-1]['balance']

            elif moveAcc[i]['code'][:2] == '54':  # -ve value
                financing_expenses_row.append(moveAcc[i])
                i += 1
                # check if next row have same code
                while True:
                    if i < arrayLen:
                        # if current == next
                        if moveAcc[i - 1]['code'] == moveAcc[i]['code']:
                            financing_expenses_row[-1]['balance'] += moveAcc[i]['balance']
                            i += 1
                        else:
                            break
                    else:
                        break
                financing_expenses_row[-1]['balance'] *= -1
                financing_expenses += financing_expenses_row[-1]['balance']

            else:
                i += 1


        lines.append(revenues_row)
        lines.append(other_revenues_row)
        lines.append(cost_of_revenues_row)
        lines.append(general_expenses_row)
        lines.append(depreciation_expenses_row)
        lines.append(selling_expenses_row)
        lines.append(financing_expenses_row)


        # create sum array
        total_revenues = revenues + other_revenues
        gross_profit = total_revenues + cost_of_revenues
        total_expenses = general_expenses + depreciation_expenses + selling_expenses + financing_expenses
        net_income = gross_profit + total_expenses

        sumArray = {
            'revenues': revenues,
            'other_revenues': other_revenues,
            'total_revenues': total_revenues,
            'cost_of_revenues': cost_of_revenues,
            'gross_profit': gross_profit,
            'general_expenses': general_expenses,
            'depreciation_expenses': depreciation_expenses,
            'selling_expenses': selling_expenses,
            'financing_expenses': financing_expenses,
            'total_expenses': total_expenses,
            'net_income': net_income,
        }
        return sumArray, lines

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form_data') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))

        account_sum, account_pl = self.account_Profit_and_Loss(data['form_data'])
        for x in account_pl:
            print(x)
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form_data'],
            'docs': docs,
            'time': time,
            'account_pl': account_pl,
            'account_sum': account_sum,
        }


class ReportProfitAndLossXLS(models.AbstractModel):
    _name = 'report.cf_reports.report_profit_and_loss_document_xlsx'
    _inherit = 'report.odoo_report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):

        # if not data.get('form_data') or not self.env.context.get('active_model'):
        #     raise UserError(_("Form content is missing, this report cannot be printed."))
        print(data)
        account_sum, account_pl = ReportProfitAndLossPDF.account_Profit_and_Loss(self, data['form_data'])
        # print(accountsa_cf)
        mydata = data['form_data']
        print(mydata)
        # style
        bold = workbook.add_format({'bold': True})
        boldCenter = workbook.add_format({'bold': True, 'align': 'center'})
        grayHeader = workbook.add_format({'bold': True, 'bg_color': '#cccccc'})
        gray = workbook.add_format({'bg_color': '#cccccc'})
        header = workbook.add_format({'bold': True, 'font_size': 15, 'align': 'center'})
        currency_acc = workbook.add_format({'num_format': '#,##0.00'})
        currency_sum = workbook.add_format({'bold': True, 'bg_color': '#cccccc', 'num_format': '#,##0.00'})
        # End Style

        # print(res_company.currency_id)
        # + mydata['company_id'][1]
        name = 'Profit And Loss  '

        sheet = workbook.add_worksheet(name)
        sheet.set_column(1, 2, 25)
        sheet.set_column(3, 8, 15)

        # Header
        # 1st row
        sheet.merge_range('B1:C1', name, header)
        # 2nd row
        sheet.write('B2', 'Date from:', bold)
        sheet.write('B3', mydata['date_from'])
        sheet.write('C2', 'Date to :', bold)
        sheet.write('C3', mydata['date_to'])
        # 3nd row
        # 4nd row
        sheet.write('A5', 'Code', bold)
        sheet.merge_range('B5:C5', 'Account', boldCenter)
        sheet.write('D5', 'Balance', boldCenter)

        # 5nd row
        sheet.merge_range('A6:C6', 'Revenues', grayHeader)
        sheet.write('D6', account_sum['revenues'], currency_sum)

        row = 6
        for obj in account_pl[0]:
            sheet.write(row, 0, obj['code'])
            sheet.merge_range(row, 1, row, 2, obj['name'])
            sheet.write(row, 3, obj['balance'], currency_acc)
            row += 1
        #
        sheet.merge_range(row, 0, row, 2, 'Other Revenues', grayHeader)
        sheet.write(row, 3, account_sum['other_revenues'], currency_sum)
        row += 1

        for obj in account_pl[1]:
            sheet.write(row, 0, obj['code'])
            sheet.merge_range(row, 1, row, 2, obj['name'])
            sheet.write(row, 3, obj['balance'], currency_acc)
            row += 1
        #
        sheet.merge_range(row, 0, row, 2, 'Total Revenues', grayHeader)
        sheet.write(row, 3, "", grayHeader)
        sheet.write(row, 4, account_sum['total_revenues'], currency_sum)
        row += 1
        #
        sheet.merge_range(row, 0, row, 2, 'Cost Of Revenues', grayHeader)
        sheet.write(row, 3, account_sum['cost_of_revenues'], currency_sum)
        row += 1

        for obj in account_pl[2]:
            sheet.write(row, 0, obj['code'])
            sheet.merge_range(row, 1, row, 2, obj['name'])
            sheet.write(row, 3, obj['balance'], currency_acc)
            row += 1
        #
        sheet.merge_range(row, 0, row, 2, 'Gross Profit', grayHeader)
        sheet.write(row, 3, "", grayHeader)
        sheet.write(row, 4, account_sum['gross_profit'], currency_sum)
        row += 1
        #
        sheet.merge_range(row, 0, row, 2, 'General And Administrative Expenses', grayHeader)
        sheet.write(row, 3, account_sum['general_expenses'], currency_sum)
        row += 1

        for obj in account_pl[3]:
            sheet.write(row, 0, obj['code'])
            sheet.merge_range(row, 1, row, 2, obj['name'])
            sheet.write(row, 3, obj['balance'], currency_acc)
            row += 1
        #
        sheet.merge_range(row, 0, row, 2, 'Depreciation Expenses', grayHeader)
        sheet.write(row, 3, account_sum['depreciation_expenses'], currency_sum)
        row += 1

        for obj in account_pl[4]:
            sheet.write(row, 0, obj['code'])
            sheet.merge_range(row, 1, row, 2, obj['name'])
            sheet.write(row, 3, obj['balance'], currency_acc)
            row += 1
        #
        sheet.merge_range(row, 0, row, 2, 'Selling And Marketing Expenses', grayHeader)
        sheet.write(row, 3, account_sum['selling_expenses'], currency_sum)
        row += 1

        for obj in account_pl[5]:
            sheet.write(row, 0, obj['code'])
            sheet.merge_range(row, 1, row, 2, obj['name'])
            sheet.write(row, 3, obj['balance'], currency_acc)
            row += 1
        #
        sheet.merge_range(row, 0, row, 2, 'Financing Expenses', grayHeader)
        sheet.write(row, 3, account_sum['financing_expenses'], currency_sum)
        row += 1

        for obj in account_pl[6]:
            sheet.write(row, 0, obj['code'])
            sheet.merge_range(row, 1, row, 2, obj['name'])
            sheet.write(row, 3, obj['balance'], currency_acc)
            row += 1
        #
        sheet.merge_range(row, 0, row, 2, 'Total Expenses', grayHeader)
        sheet.write(row, 3, "", grayHeader)
        sheet.write(row, 4, account_sum['total_expenses'], currency_sum)
        row += 1
        #
        sheet.merge_range(row, 0, row, 2, 'Net Income', grayHeader)
        sheet.write(row, 3, "", grayHeader)
        sheet.write(row, 4, account_sum['net_income'], currency_sum)
        row += 1
        #
