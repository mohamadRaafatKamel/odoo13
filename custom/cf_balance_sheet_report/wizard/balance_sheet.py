# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields


class AccountFinancialReport(models.Model):
    _name = "balance.sheet.report"
    _description = "Account Report"
