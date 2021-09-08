# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class BilssProfit(models.AbstractModel):
    _name = 'report.account_dynamic_reports.bills_profit'

    @api.model
    def render_html(self, docids, data=None):
        print"render html called \n\n\n\n\n",self.env.context.get('from_js')
        if self.env.context.get('from_js'):
            if data.get('js_data'):
                docargs = {'Ledger_data': data.get('js_data')[1],
                             'Filters': data.get('js_data')[0],
                             }
                print"docargs00 ",docargs
                return self.env['report'].render('account_dynamic_reports.bills_profit', docargs)

        docargs = {'Ledger_data': data.get('Ledger_data'),
                             'Filters': data.get('Filters'),
                             }
        print"docargs11 ",docargs                             
        return self.env['report'].render('account_dynamic_reports.bills_profit', docargs)