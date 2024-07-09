from odoo import http


class Test(http.Controller):

    @http.route('/test', type='http', auth="none", csrf=False, methods=['GET'])
    def test(self, **kwargs):
        return 'TEST'
