{
    'name': 'Automocion Rivera FSM',
    'summary': 'Gestión de órdenes de trabajo para automoción, igual que xtendoo_fsm',
    'version': '1.0',
    'author': 'Tu Empresa',
    'category': 'Services',
    'depends': [
        'base',
        'mail',
        'repair',
        'sale_management'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'views/fsm_order_views.xml',
        'views/menu.xml',
        'views/fsm_stage_views.xml',
        'views/fsm_tag_views.xml',
        'views/sale_order_views.xml',
        'views/res_partner_views.xml',
        'views/fsm_order_views_generated.xml',
        'views/fsm_order_action_repair.xml',
    ],
    #'images': ['static/description/icon.png'],

    'installable': True,
    'application': True,
    'auto_install': False
}
