{
    'name': 'Account Report',
    'version': '1.0.0',
    'summary': 'Account Report',
    'sequence': 100,
    'category': 'Website',
    'description': 'Account Report',
    'website': 'https://www.code-flex.com/',
    'depends': [
        'accounting_pdf_reports'
    ],
    'data': [
        'report/financial_report_inherit.xml',
        'report/trial_report_inherit.xml',
    ],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'author': 'Code Flex',
    'maintainer': 'MRM',

}
