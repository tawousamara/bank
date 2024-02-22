{
    "name": "Portal Document Management System | Portal Documents | Documents Portal Management | Document Management System | Documents Management System",
    "summary": "This module provide simple and very useful functionality to manage documents with directory (folders), tags, export, numbering, versions  and security groups.",
    "version": "17.1",
    "description": """
        This module provide simple and very useful functionality to manage documents with directory (folders), tags, export, numbering, versions  and security groups.
        Directory Views        
        Documents Send Document by mail
        Documents Tags
        Documents numbering
        Documents versions
        Documents Folder Views  
        Documents Export to Zip
        User Group and Manager Group Security
        Folder View Based on Document modules
        Document versions
        Documet numbering
        Filter by tags
        Document Share
        Document Send by Email
        Export Multiple Documents to Zip
        User Documents
        Personal Documents
        Shared Documents
        Portal Documents
        Portal Access for Each Users
        Upload Documents from Portal
        Portal Document Management System
        Portal Documents
        Documents Portal Management
        Document Management System
        Documents Management System
    """,    
    "author": "FINOUTSOURCE",
    "maintainer": "FINOUTSOURCE",
    "license" :  "Other proprietary",
    "website": "www.finoutsource.dz",
    "category": "Sales",
    "depends": [
        "base",
        "mail",
        "portal",
        "dept_wk",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/mail_attachment_data.xml",
        "data/attachment_sequence_data.xml",
        "data/documents_folder_data.xml",
        "views/folders_views.xml",
        "views/ir_attachment_user_views.xml",
        "views/ir_attachment_personal_views.xml",
        "views/ir_attachment_all_views.xml",
        "views/tags_views.xml",            
        "views/res_partner_views.xml",            
        "views/documents_portal_templates.xml",            
        "wizard/ir_attachment_export.xml",        
        "wizard/ir_attachment_share.xml",
        "views/menus_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "/documents_portal_management/static/src/css/style.css",
            "/documents_portal_management/static/src/css/kanban_ribbon.css",
            "/documents_portal_management/static/src/js/kanban_ribbon.js",            
            "/documents_portal_management/static/src/js/ir_attachment_preview.js",
            "/documents_portal_management/static/src/js/ir_attachment_share.js",
            "/documents_portal_management/static/src/xml/*.xml",
        ],
    },    
    "installable": True,
    "application": True,
    "pre_init_hook":  "pre_init_check",
}
