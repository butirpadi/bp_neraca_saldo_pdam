# -*- coding: utf-8 -*-
{
    'name': "Neraca Saldo PDAM Kota Madiun",

    'summary': """
        Neraca Saldo PDAM Kota Madiun""",

    'description': """
        Neraca Saldo PDAM Kota Madiun

        Author: butirpadi
        Phone : 0823-9837-1825

        Call us for custom module and reporting
    """,

    'author': "butirpadi",
    'website': "https://www.github.com/butirpadi",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'accounting_pdf_reports', 'om_account_budget'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
