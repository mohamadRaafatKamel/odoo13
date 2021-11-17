# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FinancialReport(models.AbstractModel):
    _inherit = "report.accounting_pdf_reports.report_trialbalance"

    # Big O = n2
    def account_trial_bl_n2(self, data):
        # display array
        lines = []
        # create array for all move before date from
        initSQL = """
            SELECT SUM(debit) as init_d, SUM(credit) as init_c , account_id 
            from account_move_line GROUP BY account_id ,date  HAVING date < '{}' """.format(
            str(datetime.strptime(data['date_from'], '%Y-%m-%d'))
        )
        self.env.cr.execute(initSQL)
        initAcc = self.env.cr.dictfetchall()
        # create array for all move between date from & to
        filterSQL = "SELECT SUM(debit) as filter_d, SUM(credit) as filter_c , account_id " \
                    "from account_move_line " \
                    "GROUP BY account_id ,date " \
                    "HAVING date between '" + str(
            datetime.strptime(data['date_from'], '%Y-%m-%d')) + "' and '" + str(
            datetime.strptime(data['date_to'], '%Y-%m-%d')) + "'"
        self.env.cr.execute(filterSQL)
        filterAcc = self.env.cr.dictfetchall()
        # create array for all move
        totalSQL = "SELECT SUM(debit) as total_d, SUM(credit) as total_c, aa.* from account_account aa " \
                   "LEFT join account_move_line ml on aa.id = ml.account_id GROUP BY aa.id ORDER BY code ASC"
        self.env.cr.execute(totalSQL)
        totalAcc = self.env.cr.dictfetchall()

        # merge three array
        final_row = []
        for x in totalAcc:
            if x['total_c'] != None or x['total_d'] != None:
                if x['total_d'] == None:
                    td = 0
                else:
                    td = x['total_d']

                if x['total_c'] == None:
                    tc = 0
                else:
                    tc = x['total_c']

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

                final_row = {
                    'code': x['code'],
                    'Account': x['name'],
                    'init_d': 0,
                    'init_c': 0,
                    'filter_d': 0,
                    'filter_c': 0,
                    'total_d': td,
                    'total_c': tc,
                }

                for z in initAcc:
                    if x['id'] == z['account_id']:
                        if z['init_d'] == None:
                            id = 0
                        else:
                            id = z['init_d']

                        if z['init_c'] == None:
                            ic = 0
                        else:
                            ic = z['init_c']
                        final_row['init_d'] = id
                        final_row['init_c'] = ic

                for z in filterAcc:
                    if x['id'] == z['account_id']:
                        if z['filter_d'] == None:
                            fd = 0
                        else:
                            fd = z['filter_d']

                        if z['filter_c'] == None:
                            fc = 0
                        else:
                            fc = z['filter_c']
                        final_row['filter_d'] = fd
                        final_row['filter_c'] = fc

                lines.append(final_row)

        for s in filterAcc:
            print(s)

        return lines

    # Big O = n
    def account_trial_bl(self, data):
        # display array
        lines = []
        # create array for all move before date from
        initSQL = """
            SELECT SUM(debit) as init_d, SUM(credit) as init_c, aa.*
            from account_account aa 
            LEFT join account_move_line ml 
            on aa.id = ml.account_id 
            GROUP BY aa.id ,ml.date
            HAVING ml.date < '{}'
            ORDER BY aa.code ASC""".format(data['date_from'])
        self.env.cr.execute(initSQL)
        initAcc = self.env.cr.dictfetchall()
        # create array for all move between date from & to
        filterSQL = """
            SELECT SUM(debit) as filter_d, SUM(credit) as filter_c, aa.*
            from account_account aa 
            LEFT join account_move_line ml 
            on aa.id = ml.account_id 
            GROUP BY aa.id ,ml.date
            HAVING date between '{}' and '{}'
            ORDER BY aa.code ASC""".format(data['date_from'], data['date_to'])
        self.env.cr.execute(filterSQL)
        filterAcc = self.env.cr.dictfetchall()
        # create array for all move
        totalSQL = """SELECT SUM(debit) as total_d, SUM(credit) as total_c, aa.* from account_account aa 
                   LEFT join account_move_line ml on aa.id = ml.account_id GROUP BY aa.id ORDER BY code ASC"""
        self.env.cr.execute(totalSQL)
        totalAcc = self.env.cr.dictfetchall()

        # merge three array
        final_row = []
        # counter to move on array init and filter
        init = 0
        filter = 0
        for x in totalAcc:
            if x['total_c'] != None or x['total_d'] != None:
                # calculate total balance debit or credit
                tsum = x['total_d'] - x['total_c']
                if tsum > 0:
                    td = tsum
                    tc = 0
                elif tsum < 0:
                    td = 0
                    tc = tsum * -1
                elif tsum == 0:
                    td = 0
                    tc = 0

                final_row = {
                    'code': x['code'],
                    'Account': x['name'],
                    'init_d': 0,
                    'init_c': 0,
                    'filter_d': 0,
                    'filter_c': 0,
                    'total_d': td,
                    'total_c': tc,
                }

                # check if have same id marge and move one step on initAcc array else skip
                if len(initAcc) != 0:
                    if initAcc[init]['code'] == x['code']:
                        final_row['init_d'] = initAcc[init]['init_d']
                        final_row['init_c'] = initAcc[init]['init_c']
                        init += 1
                # check if have same id marge and move one step on filterAcc array else skip
                if len(filterAcc) != 0:
                    if filterAcc[filter]['code'] == x['code']:
                        final_row['filter_d'] = filterAcc[filter]['filter_d']
                        final_row['filter_c'] = filterAcc[filter]['filter_c']
                        filter += 1
                # add to lines to display
                lines.append(final_row)
        return lines

    def account_trial_sum(self, data):
        # sum array
        init_d = init_c = filter_d = filter_c = total_d = total_c = 0
        for row in data:
            init_d += row['init_d']
            init_c += row['init_c']
            filter_d += row['filter_d']
            filter_c += row['filter_c']
            total_d += row['total_d']
            total_c += row['total_c']
        return {
            'init_d': init_d,
            'init_c': init_c,
            'filter_d': filter_d,
            'filter_c': filter_c,
            'total_d': total_d,
            'total_c': total_c,
        }

    @api.model
    def _get_report_values(self, docids, data=None):
        accountsa_cf = self.account_trial_bl(data['form'])
        account_sum = self.account_trial_sum(accountsa_cf)
        print(account_sum)
        return {
            'data': data['form'],
            'Accounts_CF': accountsa_cf,
            'account_sum': account_sum,
        }
