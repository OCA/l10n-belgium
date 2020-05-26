# -*- coding: utf-8 -*-
# Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
# Author: Adrien Peiffer
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import urllib
import logging

from lxml import etree

from odoo import models, tools
from odoo.osv import orm

SUPERUSER_ID = 1

logger = logging.getLogger(__name__)


class res_partner(models.Model):
    _inherit = 'res.partner'

    def companyweb_information(self, vat_number):
        irconfigparam = self.env['ir.config_parameter']
        login = irconfigparam.get_param('companyweb.login', False)
        pswd = irconfigparam.get_param('companyweb.pswd', False)
        if login is False or pswd is False:
            raise orm.except_orm(
                'Warning !', "Credentials are not set")

        url = "http://odm.outcome.be/alacarte_onvat.asp?login=" + \
              login + "&pswd=" + pswd + "&vat=" + vat_number
        context = self.env.context
        if context.get('lang', '').startswith('fr'):
            url = url + "&lang=1"
        elif context.get('lang', '').startswith('nl'):
            url = url + "&lang=2"

        try:
            p = etree.XMLParser(no_network=False)
            tree = etree.parse(url, parser=p)
        except:
            logging.error("Error parsing companyweb url %s", url,
                          exc_info=True)
            raise orm.except_orm('Warning !',
                                 "System error loading Companyweb data.\n"
                                 "Please retry and contact your "
                                 "system administrator if the error persists.")

        message = tree.xpath("/Companies")[0].get("Message")
        if message:
            raise orm.except_orm('Warning !',
                                 "Error loading Companyweb data:\n%s.\n"
                                 "\n"
                                 "Please check your credentials in settings/"
                                 "configuration/Companyweb.\n"
                                 "\n"
                                 "Login on www.companyweb.be with login "
                                 "'cwacsone' and password 'demo' "
                                 "to obtain test credentials." % message)

        if tree.xpath("/Companies")[0].get("Count") == "0":
            raise orm.except_orm(
                'Warning !', "VAT number of this company is not known in the "
                             "Companyweb database")

        firm = tree.xpath("/Companies/firm")

        startDate = firm[0].xpath("StartDate")[0].text
        endDate = firm[0].xpath("EndDate")[0].text
        if endDate == "0":
            endDate = False
            endOfActivity = False
        else:
            endOfActivity = True

        warningstxt = ""
        for warning in firm[0].xpath("Warnings/Warning"):
            warningstxt = warningstxt + "- " + warning.text + "\n"

        if endOfActivity:
            fichier = "barometer_stop.png"
            im = urllib.urlopen(
                'http://www.companyweb.be/img/barometer/' + fichier)
            source = im.read()
        elif len(firm[0].xpath("Score")) > 0:
            score = firm[0].xpath("Score")[0].text
            if score[0] == '-':
                signe = "neg-"
                if len(score) == 2:
                    chiffre = "0" + score[1:]
                else:
                    chiffre = score[1:]
            else:
                signe = "pos-"
                if len(score) == 1:
                    chiffre = "0" + score[0:]
                else:
                    chiffre = score[0:]

            fichier = signe + chiffre + ".png"
            im = urllib.urlopen(
                'http://www.companyweb.be/img/barometer/' + fichier)
            source = im.read()
        else:
            img_path = 'static/images/barometer_none.png'
            with open(img_path, 'rb') as f:
                source = f.read()

        image = tools.image_resize_image_medium(source.encode('base64'))

        dicoRoot = dict()
        for Element in firm[0]:
            dicoRoot[Element.tag] = Element.text
        balance_year = ""
        if len(firm[0].xpath("Balans/Year")) > 0:
            balance_year = firm[0].xpath("Balans/Year")[0].get("value")
            for Element2 in firm[0].xpath("Balans/Year")[0]:
                if Element2.text:
                    dicoRoot[Element2.tag] = Element2.text

        def getValue(attr):
            return dicoRoot.get(attr, 'N/A')

        def getFloatValue(attr):
            r = dicoRoot.get(attr)
            if r:
                return float(r)
            else:
                return False

        valeur = {
            'name': getValue('Name'),
            'jur_form': getValue('JurForm'),
            'vat_number': "BE0" + getValue('Vat'),
            'street': getValue('Street') + ", " + getValue('Nr'),
            'zip': getValue('PostalCode'),
            'city': getValue('City'),
            'creditLimit': getFloatValue('CreditLimit'),
            'startDate': startDate,
            'endDate': endDate,
            'image': image,
            'warnings': warningstxt,
            'url': dicoRoot['Report'],
            'vat_liable': getValue('VATenabled') == "True",
            'balance_year': balance_year,
            'equityCapital': getFloatValue('Rub10_15'),
            'addedValue': getFloatValue('Rub9800'),
            'turnover': getFloatValue('Rub70'),
            'result': getFloatValue('Rub9904'),
        }

        wizard_id = self.env['account.companyweb.wizard'].create(
            valeur)

        return {
            'name': "Companyweb Informations",
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.companyweb.wizard',
            'res_id': wizard_id.id,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'new',
            'domain': '[]',
            'context': context,
        }

    def button_companyweb(self):
        for partner in self:
            if not partner.vat:
                raise orm.except_orm(
                    'Error!', "This company has no VAT number")
            vat = partner.vat

        vat_country = vat[:2].lower()
        vat_number = vat[2:].replace(' ', '')

        if vat_country == "be":
            company_information = self.companyweb_information(vat_number)
            return company_information
        else:
            raise orm.except_orm(
                'Error!', "Companyweb is only available for companies with a "
                          "Belgian VAT number")
