{
    'name': 'CF Reports',
    'version': '1.0.0',
    'summary': 'Profit and Loss',
    'sequence': 100,
    'category': 'Website',
    'description': 'Profit and Loss',
    'website': 'https://www.code-flex.com/',
    'depends': [
        'account',
        'odoo_report_xlsx'
    ],
    'data': [
        'security/ir.model.access.csv',

        'reports/report_profit_and_loss.xml',
        'reports/report.xml',

        'wizard/profit_and_loss.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'author': 'Code Flex',
    'maintainer': 'MRM',

}
