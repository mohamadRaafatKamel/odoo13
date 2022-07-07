# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportTrialBalance(models.AbstractModel):
    _name = 'report.trial_balance_report.report_trial_balance_document'
    # _inherit = 'report.odoo_report_xlsx.abstract'

    def _get_accounts(self, accounts, display_account):
        """ compute the balance, debit and credit for the provided accounts
            :Arguments:
                `accounts`: list of accounts record,
                `display_account`: it's used to display either all accounts or those accounts which balance is > 0
            :Returns a list of dictionary of Accounts with following key and value
                `name`: Account name,
                `code`: Account code,
                `credit`: total amount of credit,
                `debit`: total amount of debit,
                `balance`: total amount of balance,
        """

        account_result = {}
        # Prepare sql query base on selected parameters from wizard
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        tables = tables.replace('"', '')
        if not tables:
            tables = 'account_move_line'
        wheres = [""]
        if where_clause.strip():
            wheres.append(where_clause.strip())
        filters = " AND ".join(wheres)
        # compute the balance, debit and credit for the provided accounts
        request = (
                "SELECT account_id AS id, SUM(debit) AS debit, SUM(credit) AS credit, (SUM(debit) - SUM(credit)) AS balance" + \
                " FROM " + tables + " WHERE account_id IN %s " + filters + " GROUP BY account_id")
        params = (tuple(accounts.ids),) + tuple(where_params)
        self.env.cr.execute(request, params)
        for row in self.env.cr.dictfetchall():
            account_result[row.pop('id')] = row

        account_res = []
        for account in accounts:
            res = dict((fn, 0.0) for fn in ['credit', 'debit', 'balance'])
            currency = account.currency_id and account.currency_id or account.company_id.currency_id
            res['code'] = account.code
            res['name'] = account.name
            if account.id in account_result:
                res['debit'] = account_result[account.id].get('debit')
                res['credit'] = account_result[account.id].get('credit')
                res['balance'] = account_result[account.id].get('balance')
            if display_account == 'all':
                account_res.append(res)
            if display_account == 'not_zero' and not currency.is_zero(res['balance']):
                account_res.append(res)
            if display_account == 'movement' and (
                    not currency.is_zero(res['debit']) or not currency.is_zero(res['credit'])):
                account_res.append(res)
        return account_res

    def account_trial_bl(self, data):
        # display array
        lines = []
        # create array for all move before date from
        initSQL = """
            SELECT SUM(debit) as init_d, SUM(credit) as init_c, aa.*, ml.parent_state
            from account_account aa 
            LEFT join account_move_line ml 
            on aa.id = ml.account_id 
            GROUP BY aa.id ,ml.date, ml.parent_state
            HAVING ml.date < '{}'
            and ml.parent_state = '{}'
            ORDER BY aa.code ASC""".format(data['date_from'], "posted")
        self.env.cr.execute(initSQL)
        initAcc = self.env.cr.dictfetchall()
        # create array for all move between date from & to
        filterSQL = """
            SELECT SUM(debit) as filter_d, SUM(credit) as filter_c, aa.*, ml.parent_state
            from account_account aa 
            LEFT join account_move_line ml 
            on aa.id = ml.account_id 
            GROUP BY aa.id ,ml.date, ml.parent_state
            HAVING date between '{}' and '{}'
            and ml.parent_state = '{}'
            ORDER BY aa.code ASC""".format(data['date_from'], data['date_to'], "posted")
        self.env.cr.execute(filterSQL)
        filterAcc = self.env.cr.dictfetchall()
        # create array for all move
        allAccount = """SELECT SUM(debit) as total_d, SUM(credit) as total_c, aa.* from account_account aa 
                   LEFT join account_move_line ml on aa.id = ml.account_id GROUP BY aa.id ORDER BY code ASC"""
        self.env.cr.execute(allAccount)
        allAccount = self.env.cr.dictfetchall()

        # totalSQL = """
        #             SELECT SUM(debit) as total_d, SUM(credit) as total_c, aa.*
        #             from account_account aa
        #             LEFT join account_move_line ml
        #             on aa.id = ml.account_id
        #             GROUP BY aa.id ,ml.date
        #             HAVING ml.date < '{}'
        #             ORDER BY aa.code ASC""".format(data['date_to'])
        #
        # self.env.cr.execute(totalSQL)
        # totalAcc = self.env.cr.dictfetchall()

        # merge three array
        final_row = []
        # counter to move on array init and filter
        init = 0
        filter = 0
        # total = 0

        # sum array
        init_d = init_c = filter_d = filter_c = total_d = total_c = 0
        for x in allAccount:
            # calculate Adjusted Balance
            if x['total_c'] != None or x['total_d'] != None:
                # calculate total balance debit or credit
                # tc = td = 0
                # # check if in range
                # if len(totalAcc) > total:
                #     # check same code
                #     if totalAcc[total]['code'] == x['code']:
                #         # loop on all account in different date
                #         while True:
                #             td += totalAcc[total]['total_d']
                #             tc += totalAcc[total]['total_c']
                #             total += 1
                #             # check if in range
                #             if len(totalAcc) > total:
                #                 # check if have other date for this account
                #                 if totalAcc[total]['code'] != x['code']:
                #                     break
                #             else:
                #                 break

                final_row = {
                    'code': x['code'],
                    'Account': x['name'],
                    'init_d': 0,
                    'init_c': 0,
                    'filter_d': 0,
                    'filter_c': 0,
                    # 'total_d': td,
                    # 'total_c': tc,
                    'total_d': 0,
                    'total_c': 0,
                }

                # check if have same id marge and move one step on initAcc array else skip

                # check if in range
                if len(initAcc) > init:
                    # check same code
                    if initAcc[init]['code'] == x['code']:
                        # if initAcc[init]['parent_state'] == "posted":
                        # loop on all account in different date
                        while True:
                            final_row['init_d'] += initAcc[init]['init_d']
                            final_row['init_c'] += initAcc[init]['init_c']
                            init += 1
                            # check if in range
                            if len(initAcc) > init:
                                # check if have other date for this account
                                if initAcc[init]['code'] != x['code']:
                                    break
                            else:
                                break

                # check if have same id marge and move one step on filterAcc array else skip
                if len(filterAcc) > filter:
                    if filterAcc[filter]['code'] == x['code']:
                        # if filterAcc[filter]['parent_state'] == "posted":
                        while True:
                            final_row['filter_d'] += filterAcc[filter]['filter_d']
                            final_row['filter_c'] += filterAcc[filter]['filter_c']
                            filter += 1
                            if len(filterAcc) > filter:
                                if filterAcc[filter]['code'] != x['code']:
                                    break
                            else:
                                break

                td = final_row['init_d'] + final_row['filter_d']
                tc = final_row['init_c'] + final_row['filter_c']

                tsum = td - tc
                if tsum > 0:
                    td = tsum
                    tc = 0
                elif tsum < 0:
                    td = 0
                    tc = tsum * -1
                elif tsum == 0:
                    td = 0
                    tc = 0

                final_row['total_d'] = td
                final_row['total_c'] = tc

                # add to lines to display
                if final_row['init_d'] != 0 or final_row['init_c'] != 0 or final_row['filter_d'] != 0 or final_row[
                    'filter_c'] != 0:
                    lines.append(final_row)

                # add value to sum
                init_d += final_row['init_d']
                init_c += final_row['init_c']
                filter_d += final_row['filter_d']
                filter_c += final_row['filter_c']
                total_d += final_row['total_d']
                total_c += final_row['total_c']

        # create sum array
        sumArray = {
            'init_d': init_d,
            'init_c': init_c,
            'filter_d': filter_d,
            'filter_c': filter_c,
            'total_d': total_d,
            'total_c': total_c,
        }
        return sumArray, lines

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids', []))
        # display_account = data['form'].get('display_account')
        # accounts = docs if self.model == 'account.account' else self.env['account.account'].search([])
        # account_res = self.with_context(data['form'].get('used_context'))._get_accounts(accounts, display_account)

        account_sum, accountsa_cf = self.account_trial_bl(data['form'])

        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'Accounts_CF': accountsa_cf,
            'account_sum': account_sum,
            # 'Accounts': account_res,
        }


class ReportTrialBalanceXlsx(models.AbstractModel):
    _name = 'report.trial_balance_report.report_trial_balance_document_xlsx'
    _inherit = 'report.odoo_report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        account_sum, accountsa_cf = ReportTrialBalance.account_trial_bl(self, data['form_data'])
        # print(accountsa_cf)
        mydata = data['form_data']
        # print(mydata)
        # style
        bold = workbook.add_format({'bold': True})
        boldCenter = workbook.add_format({'bold': True, 'align': 'center'})
        grayHeader = workbook.add_format({'bold': True, 'bg_color': '#cccccc', 'align': 'center'})
        header = workbook.add_format({'bold': True, 'font_size': 15, 'align': 'center'})
        currency_format = workbook.add_format({'num_format': '#,##0.00'})
        currency_sum = workbook.add_format({'bold': True, 'bg_color': '#cccccc', 'num_format': '#,##0.00'})
        # End Style

        # print(res_company.currency_id)

        name = 'Trial Balance : ' + mydata['company_id'][1]
        target = ''
        if (mydata['target_move'] == 'posted'): target = 'All Posted Entries'
        if (mydata['target_move'] == 'all'): target = 'All Entries'
        display_account = ''
        if (mydata['display_account'] == 'all'): display_account = 'All'
        if (mydata['display_account'] == 'movement'): display_account = 'With movements'
        if (mydata['display_account'] == 'not_zero'): display_account = 'With balance is not equal to 0'
        sheet = workbook.add_worksheet(name)
        sheet.set_column(1, 2, 25)
        sheet.set_column(3, 8, 15)

        # Header
        # 1st row
        sheet.merge_range('D1:F1', name, header)
        # 2nd row
        sheet.write(1, 1, 'Display Account:', bold)
        sheet.write(1, 3, 'Date from:', bold)
        sheet.write(1, 4, mydata['date_from'])
        sheet.write(1, 6, 'Target Moves:', bold)
        # 3nd row
        sheet.write(2, 1, display_account)
        sheet.write(2, 3, 'Date to :', bold)
        sheet.write(2, 4, mydata['date_to'])
        sheet.write(2, 6, target)
        # 4nd row
        # 5nd row
        sheet.merge_range('D5:E5', 'Unadjusted Trial Balance', grayHeader)
        sheet.merge_range('F5:G5', 'Adjustment', grayHeader)
        sheet.merge_range('H5:I5', 'Adjusted Balance', grayHeader)
        # 6nd row
        sheet.write('A6', 'Code', bold)
        sheet.merge_range('B6:C6', 'Account', boldCenter)
        # sheet.merge_range('B5:B6', 'Account', bold)
        sheet.write(5, 3, 'Dr.', boldCenter)
        sheet.write(5, 4, 'Cr.', boldCenter)
        sheet.write(5, 5, 'Dr.', boldCenter)
        sheet.write(5, 6, 'Cr.', boldCenter)
        sheet.write(5, 7, 'Dr.', boldCenter)
        sheet.write(5, 8, 'Cr.', boldCenter)
        # 7th row
        row = 6
        for obj in accountsa_cf:
            # One sheet by partner
            sheet.write(row, 0, obj['code'])
            sheet.merge_range(row, 1, row, 2, obj['Account'])
            sheet.write(row, 3, obj['init_d'], currency_format)
            sheet.write(row, 4, obj['init_c'], currency_format)
            sheet.write(row, 5, obj['filter_d'], currency_format)
            sheet.write(row, 6, obj['filter_c'], currency_format)
            sheet.write(row, 7, obj['total_d'], currency_format)
            sheet.write(row, 8, obj['total_c'], currency_format)

            row += 1

        sheet.write(row, 0, 'Total :', grayHeader)
        sheet.merge_range(row, 1, row, 2, '',grayHeader)
        sheet.write(row, 3, account_sum['init_d'], currency_sum)
        sheet.write(row, 4, account_sum['init_c'], currency_sum)
        sheet.write(row, 5, account_sum['filter_d'], currency_sum)
        sheet.write(row, 6, account_sum['filter_c'], currency_sum)
        sheet.write(row, 7, account_sum['total_d'], currency_sum)
        sheet.write(row, 8, account_sum['total_c'], currency_sum)
