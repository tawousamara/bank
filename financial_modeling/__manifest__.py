# -*- coding: utf-8 -*-
{
    'name': "Financial Modeling",

    'summary': """
         - Prévisions de chiffre d`affaire automatique sur la base de données de facturation
         - Prévisions chiffre d`affaire automatique sur la base de données CRM
         - Prévisions de chiffre d`affaire manuelle
         - Analyse Besoins en Fonds de Roulement (BFR) historique
    """,

    'description': """
         - Prévisions de chiffre d`affaire automatique sur la base de données de facturation
         - Prévisions chiffre d`affaire automatique sur la base de données CRM
         - Prévisions de chiffre d`affaire manuelle
         - Analyse Besoins en Fonds de Roulement (BFR) historique
    """,

    'author': "finoutsource group",
    'website': "",

    'category': 'custom',
    'depends': ['base'],

    'data': [
        'data/ir_sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/automatic_revenue_forecast.xml',
        'views/manual_revenue_forecast.xml',
        'views/bfr_analysis.xml',
        'views/stress_testing.xml',
        'views/val_multiple_ebe.xml',
        'views/val_dcf.xml',
        'views/tcr_analysis.xml',
        'views/bilan_actif_passif.xml',
        'views/import_ocr_tcr.xml',
        'views/import_ocr_actif.xml',
        'views/import_ocr_passif.xml',
        'views/scoring_kpi.xml',
        'views/wizard_view.xml',
        'views/scoring_valorisation_cumule.xml',
        'views/menuitem.xml',
        'data/data.xml',
        'data/secteur_data.xml',
    ],

    "images": [],
}
