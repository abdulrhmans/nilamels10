# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from openerp import fields, models, api, _

class sale_config_settings(models.TransientModel):
    _inherit = "sale.config.settings"

    collector_based = fields.Boolean("Collector Based", help='if checked,generates the weekly report Cash collection based on Collector')
    salesman_based = fields.Boolean("Salesman Based", help='if checked,generates the weekly report Cash collection based on Salesman')

    @api.model
    def default_get(self, fields_list):
        res = super(sale_config_settings, self).default_get(fields_list)
        res.update({'collector_based': 1})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: