# -*- coding: utf-8 -*-
import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class FinancialReport(models.AbstractModel):
    _inherit = "report.accounting_pdf_reports.report_financial"

    def getDetails(self, id):
        print("ff")

    def get_bs_account_lines(self):
        lines = []
        # FixedAssets = self.env['account.account'].search([('user_type_id', '=', 8)])

        allGroub = "SELECT SUM(balance) as balance, aa.group_id " \
                   "from account_account aa " \
                   "LEFT join account_move_line ml " \
                   "on aa.id = ml.account_id " \
                   "GROUP BY aa.group_id "
        self.env.cr.execute(allGroub)
        account = self.env.cr.dictfetchall()

        allAcc = "SELECT SUM(balance) as balance, aa.* " \
                   "from account_account aa " \
                   "LEFT join account_move_line ml " \
                   "on aa.id = ml.account_id " \
                   "GROUP BY aa.id " \
                 "ORDER BY aa.code ASC"
        self.env.cr.execute(allAcc)
        allAccount = self.env.cr.dictfetchall()
        # "LEFT join account_group ag " \
        # "on aa.group_id= ag.id "\
        # "GROUP BY gname "



        groupp = []
        for group in account:
            acc = self.env['account.account'].search([('group_id', '=', group.get('group_id'))])
            grp = self.env['account.group'].search([('id', '=', group.get('group_id'))])
            if group.get('balance') == None:
                bl = 0.0
            else:
                bl = group.get('balance')
            row = {
                'gname': grp.name,
                'gcode': grp.code_prefix,
                'balance': bl,
                'level': '3',
                'account_type': acc[0].user_type_id
            }
            groupp.append(row)

        ### Start Assets

        # get account type Fixed Assets id = 8
        fixedAssetsBL = 0
        fixedAssetsAcc = []
        for x in groupp:
            if x['account_type']['id'] == 8:
                fixedAssetsBL += x['balance']
                fixedAssetsAcc.append(x)
        # get account type Account Receivable id = 1
        ReceivableBL = 0
        for x in groupp:
            if x['account_type']['id'] == 1:
                ReceivableBL += x['balance']
        # get account type Bank and Cash id = 3
        bankAndCachBL = 0
        bankAndCachAcc = []
        for x in groupp:
            if x['account_type']['id'] == 3:
                bankAndCachBL += x['balance']
                bankAndCachAcc.append(x)
        # get account type others Current Assets id = 5
        ocurrentAssetsBL = 0
        ocurrentAssetsAcc = []
        for x in groupp:
            if x['account_type']['id'] == 5:
                ocurrentAssetsBL += x['balance']
                ocurrentAssetsAcc.append(x)

        CurrentAssetsBL = ReceivableBL + bankAndCachBL + ocurrentAssetsBL
        AssetsBL = fixedAssetsBL + CurrentAssetsBL
        ### End Assets

        ### Start Liabilities and Equity

        # get group by name
        # print('vvvv')
        for x in groupp:
            print(x)
            if x['gname'] != False:
                if "Tax Authority" in x['gname']:
                    taxAuthBl = 0
                    taxAuthAcc = []
                    taxAuthAcc = x
                    taxAuthBl = x['balance']
                elif "Others Credit Accounts" in x['gname']:
                    OthersCreditAccountsAcc = []
                    OthersCreditAccountsBl = 0
                    OthersCreditAccountsAcc = x
                    OthersCreditAccountsBl = x['balance']
                elif "Consignments With Others" in x['gname']:
                    ConsignmentsWithOthersAcc = []
                    ConsignmentsWithOthersBl = 0
                    ConsignmentsWithOthersAcc = x
                    ConsignmentsWithOthersBl = x['balance']
                elif "Accumulated Depreciation" in x['gname']:
                    AccumulatedDepreciationAcc = []
                    AccumulatedDepreciationBl = 0
                    AccumulatedDepreciationAcc = x
                    AccumulatedDepreciationBl = x['balance']
                elif "Retained Eranings" in x['gname']:
                    RetainedEarningAcc = []
                    RetainedEarningBl = 0
                    RetainedEarningAcc = x
                    RetainedEarningBl = x['balance']
                    # get group by name
        for x in allAccount:
            if "Accrued Salaries & Wages" in x['name']:
                AccruedSalariesWagesBlAcc = {
                    'gname': x['name'],
                    'gcode': x['code'],
                    'balance': x['balance'],
                    'level': '5',
                    'account_type': ''
                }
                if x['balance'] == None: AccruedSalariesWagesBl = 0
                else: AccruedSalariesWagesBl = x['balance']
            elif "Social Insurance Board" in x['name']:
                SocialInsuranceBoardAcc = {
                    'gname': x['name'],
                    'gcode': x['code'],
                    'balance': x['balance'],
                    'level': '5',
                    'account_type': ''
                }
                if x['balance'] == None: SocialInsuranceBoardBl = 0
                else: SocialInsuranceBoardBl = x['balance']
            elif "Accrued Expenses" in x['name']:
                AccruedExpensesAcc = {
                    'gname': x['name'],
                    'gcode': x['code'],
                    'balance': x['balance'],
                    'level': '5',
                    'account_type': ''
                }
                if x['balance'] == None: AccruedExpensesBl = 0
                else: AccruedExpensesBl = x['balance']
            elif "Legal Reserve" in x['name']:
                LegalReservesAcc = {
                    'gname': x['name'],
                    'gcode': x['code'],
                    'balance': x['balance'],
                    'level': '3',
                    'account_type': ''
                }
                if x['balance'] == None: LegalReservesBl = 0
                else: LegalReservesBl = x['balance']


        # get account type account Payable id = 2
        PayableBL = 0
        for x in groupp:
            if x['account_type']['id'] == 2:
                PayableBL += x['balance']
        # get account type Non Current Liabilities id = 10
        nonCurrentLiabilitiesBL = 0
        for x in groupp:
            if x['account_type']['id'] == 10:
                nonCurrentLiabilitiesBL += x['balance']


        OthersCreditAccountsFullBalance = 0
        #
        # OthersCreditAccountsBl = 0
        # ConsignmentsWithOthersBl = 0
        # taxAuthBl = 0
        # AccumulatedDepreciationBl = 0
        # RetainedEarningBl = 0
        #
        OthersCreditAccountsFullBalance = OthersCreditAccountsBl + ConsignmentsWithOthersBl + AccruedSalariesWagesBl + SocialInsuranceBoardBl + AccruedExpensesBl + AccumulatedDepreciationBl
        CurrentLiabilitiesBalance = OthersCreditAccountsFullBalance + PayableBL + taxAuthBl
        LiabilitiesBl = CurrentLiabilitiesBalance + nonCurrentLiabilitiesBL
        EquityBl = int(RetainedEarningBl) + int(LegalReservesBl)
        LiabilitiesAndEquityBl= EquityBl + LiabilitiesBl


        ### End Liabilities and Equity




        # Start display #########################
        finalrow = {
            'gname': "Assets",
            'gcode': '',
            'balance': AssetsBL,
            'level': '1',
            'account_type': ''
        }
        lines.append(finalrow)
        finalrow = {
            'gname': "Fixed Assets",
            'gcode': '',
            'balance': fixedAssetsBL,
            'level': '2',
            'account_type': ''
        }
        lines.append(finalrow)
        for z in fixedAssetsAcc:
            lines.append(z)
        finalrow = {
            'gname': "Current Assets",
            'gcode': '',
            'balance': CurrentAssetsBL,
            'level': '2',
            'account_type': ''
        }
        lines.append(finalrow)
        finalrow = {
            'gname': "Account Receivable",
            'gcode': '',
            'balance': ReceivableBL,
            'level': '3',
            'account_type': ''
        }
        lines.append(finalrow)
        finalrow = {
            'gname': "Cash & Banks",
            'gcode': '',
            'balance': bankAndCachBL,
            'level': '3',
            'account_type': ''
        }
        lines.append(finalrow)
        for z in bankAndCachAcc:
            z['level'] = '4'
            lines.append(z)
        finalrow = {
            'gname': "Others Current Assets",
            'gcode': '',
            'balance': ocurrentAssetsBL,
            'level': '3',
            'account_type': ''
        }
        lines.append(finalrow)
        for z in ocurrentAssetsAcc:
            z['level'] = '4'
            lines.append(z)
        #
        finalrow = {
            'gname': "Liabilities and Equity",
            'gcode': '',
            'balance': LiabilitiesAndEquityBl,
            'level': '1',
            'account_type': ''
        }
        lines.append(finalrow)
        finalrow = {
            'gname': "Liabilities",
            'gcode': '',
            'balance': LiabilitiesBl,
            'level': '2',
            'account_type': ''
        }
        lines.append(finalrow)
        finalrow = {
            'gname': "Current Liabilities",
            'gcode': '',
            'balance': CurrentLiabilitiesBalance,
            'level': '3',
            'account_type': ''
        }
        lines.append(finalrow)
        finalrow = {
            'gname': "Account Payable",
            'gcode': '',
            'balance': PayableBL,
            'level': '4',
            'account_type': ''
        }
        lines.append(finalrow)
        taxAuthAcc['level']= '4'
        lines.append(taxAuthAcc)
        OthersCreditAccountsAcc['level'] = '4'
        OthersCreditAccountsAcc['balance'] = OthersCreditAccountsFullBalance
        lines.append(OthersCreditAccountsAcc)
        ConsignmentsWithOthersAcc['level'] = '5'
        lines.append(ConsignmentsWithOthersAcc)
        lines.append(AccruedSalariesWagesBlAcc)
        lines.append(SocialInsuranceBoardAcc)
        lines.append(AccruedExpensesAcc)
        AccumulatedDepreciationAcc['level'] = '5'
        lines.append(AccumulatedDepreciationAcc)
        finalrow = {
            'gname': "Non-Current Liabilities",
            'gcode': '',
            'balance': nonCurrentLiabilitiesBL,
            'level': '3',
            'account_type': ''
        }
        lines.append(finalrow)
        finalrow = {
            'gname': "Equity",
            'gcode': '',
            'balance': EquityBl,
            'level': '2',
            'account_type': ''
        }
        lines.append(finalrow)
        lines.append(LegalReservesAcc)
        # lines.append(RetainedEarningAcc)



        # End display #########################

        for c in lines:
            print(c)
            # typeAsset = self.env['account.account.type'].search([('internal_group', '=', 'asset')])
            #
            # for acc in groupp:
            #     if acc['account_type'] in typeAsset['id']:
            #         print(acc)
            #

            # get all type
            # unique_list = []
            # for x in groupp:
            #     # check if exists in unique_list or not
            #     if x['account_type'] not in unique_list:
            #         unique_list.append(x)
            # print(groupp)

        return lines

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or not self.env.context.get('active_model') or not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, this report cannot be printed."))

        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        report_lines = self.get_account_lines(data.get('form'))
        bs_report_lines = self.get_bs_account_lines()
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_account_lines': report_lines,
            'bs_report_lines': bs_report_lines,
        }

# self.env['account.move.line']._query_get()
#                 accounts = self.env['account.account'].search([('user_type_id', 'in', report.account_type_ids.ids)])
#         account_report = self.env['account.financial.report'].search([('id', '=', data['account_report_id'][0])])
#                     account = self.env['account.account'].browse(account_id)
