{
    'name': "Workflow",
    'depends': ['base', 'contacts', 'board',
                'financial_modeling'],
    'sequence': '30',
    'author': "FINOUTSOURCE",
    'category': 'Extra Tools',
    'summary': "Module pour le financement",
    # data files always loaded at installation
    'data': [
            'security/security.xml',
            'security/ir.model.access.csv',
            'data/sequence.xml',
            'data/data_agence.xml',
            'data/data_garanties.xml',
            'data/data_product.xml',
            'data/data_activite.xml',
            'data/data_wilaya.xml',
            'data/data_commune.xml',
            'data/data_forme_juridique.xml',
            'data/data_type_demande.xml',
            'data/data_decision_cell.xml',
            'data/data_state.xml',
            'data/api_data.xml',
            'data/other_data.xml',
            'reports/report_global.xml',
            'reports/report_global_dollar.xml',
            'reports/report_risk.xml',
            'reports/mail_template.xml',
            'views/configuration.xml',
            'views/tracking.xml',
            'views/partner_view.xml',
            'views/configuration_risk.xml',
            'views/scoring.xml',
            'views/menu_tems.xml',
            'views/documents_manager.xml',
            'views/workflow_new.xml',
            'views/ocr_inherit.xml',
            'views/wizard_view.xml',
            'views/etape.xml',
            'views/analytic_views.xml',
            'views/res_config.xml',
            #'views/wk_report_one.xml',
            #'views/wk_report_two.xml',
            'views/menu_item.xml',
            'data/data_assign_users.xml'
            ,
            ],
    # data files containing optionally loaded demonstration data
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,

    'assets': {
        'web.assets_backend': [
            'dept_wk/static/src/css/custom_styles.css',
            'dept_wk/static/src/css/custom_font.css',  # Path to your CSS file
        ],
        'web.report_assets_common': [
            'dept_wk/static/src/css/custom_font.css',  # Path to your CSS file
        ],
    },
}
