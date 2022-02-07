from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers import portal

class EstateProperty(http.Controller):

    # @http.route('/estate/index1', auth="public")
    # def index(1self, **kw):
    #     return "Real Estate Property"

    # @http.route('/hello_user', auth="user")
    # def hello_user(self, **kw):
    #     return "Hello %s" %(request.env.user.name)

    # @http.route('/estate/index', auth="public")
    # def index(self, **kw):
    #     return http.request.render('estate.index' , {
    #         'name' : ['House' , 'Pentahouse' , 'Apartment']
    #     })

    @http.route('/estate/property', auth="user" , website = True)
    def index(self, **kw):
        estate = http.request.env['estate.property']
        return http.request.render('estate.index' , {
            'properties' : estate.search([])
        })


class MyControllers(portal.CustomerPortal) :

    def _prepare_home_portal_values(self , counters) :
        values =  super()._prepare_home_portal_values(counters)
        Properties = request.env['estate.property']
        values['total_properties'] = Properties.search_count([]) or 0
        return values


    @http.route('/my/properties', auth="user" , website = True)
    def index(self, **kw):
        estate = request.env['estate.property'].search([])
        values = self._prepare_portal_layout_values()
        values.update({
            'properties' : estate ,

        })
        return http.request.render('estate.poratl_my_properties' , values)
