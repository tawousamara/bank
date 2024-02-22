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
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/tcr_analysis.xml',
        'views/bilan_actif_passif.xml',
        'views/import_ocr_tcr.xml',
        'views/import_ocr_actif.xml',
        'views/import_ocr_passif.xml',
        'views/scoring_kpi.xml',
        'views/scoring_valorisation_cumule.xml',
        'views/wizard_view.xml',
        'views/menuitem.xml',
        'data/data.xml',
        'data/secteur_data.xml',
    ],

    "images": [],
}
