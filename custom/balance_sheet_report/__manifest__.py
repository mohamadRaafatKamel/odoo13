# -*- coding: utf-8 -*-
{
    'name': "balance_sheet_report",
    'summary': """Balance Sheet Report""",
    'description': """Balance Sheet Report""",
    'author': "MRM",
    'website': "",
    'category': 'Invoicing',
    'version': '13.0.0.1',
    'depends': ['base', 'odoo_report_xlsx'],
    'data': [
        # 'reports/report_financial.xml',
        'reports/report.xml',
        'wizard/balance_sheet.xml',
    ]
}
