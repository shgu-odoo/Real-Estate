{
    'name' : 'Real Estate',
    'category' : 'Sales',
    'application' : True,
    'depends' : ['base' , 'account' , 'website' , 'portal'],
    'data' : [
        'security/estate_property_security.xml',
        'security/ir.model.access.csv',
        'views/estate_menus.xml',
        'views/estate_property_views.xml',
        'views/estate_myproperty_menus.xml',
        'views/estate_property_myproperty_views.xml',
        'wizard/add_offer_views.xml' ,
        'views/estate_index.xml',
        'views/estate_portal_views.xml',

    ],
    'license' : 'LGPL-3',
    'installable' : True,

}