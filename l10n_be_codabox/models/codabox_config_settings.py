# Copyright 2022 Niboo SRL (<https://www.niboo.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class CodaboxConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"
    _description = "Add Codabox config settings page"

    key = fields.Char("CodaBox API Key", required=True)

    username = fields.Char("CodaBox Username")
    password = fields.Char("CodaBox Password")

    prod_environment = fields.Boolean(
        "Environment",
        help="Set to True if your credentials " "are certified for production.",
        readonly=True,
    )

    def set_values(self):
        super(CodaboxConfigSettings, self).set_values()
        IrConfig = self.env["ir.config_parameter"]
        IrConfig.set_param("codabox.api.username", self.username)
        IrConfig.set_param("codabox.api.password", self.password)
        IrConfig.set_param("codabox.api.key", self.key)
        IrConfig.set_param("codabox.api.prod.environment", self.prod_environment)

    def get_values(self):
        res = super(CodaboxConfigSettings, self).get_values()
        res.update(
            {
                "key": self.get_param("codabox.api.key"),
                "username": self.get_param("codabox.api.username"),
                "password": self.get_param("codabox.api.password"),
                "prod_environment": self.get_param("codabox.api.prod.environment"),
            }
        )
        return res

    def toggle_prod_environment(self):
        """
        Changes boolean field saying whether the environment used is prod
        """
        IrConfig = self.env["ir.config_parameter"]
        for setting_page in self:
            setting_page.prod_environment = not setting_page.prod_environment
            IrConfig.set_param(
                "codabox.api.prod.environment", setting_page.prod_environment
            )

    @api.model
    def get_param(self, param):
        """
        :param param: Key of the parameter ir config parameter
        :return: Value of the ir config parameter
        """
        return self.env["ir.config_parameter"].get_param(param)

    def get_codabox_credentials(self):
        """
        Called when pressing the "get_codabox_credentials" button in Codabox
        setting page view.
        :return: a Wizard view
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_id": self.env.ref("codabox.codabox_credentials_wizard").id,
            "name": "Retrieve Credentials",
            "target": "new",
            "res_model": "codabox.credentials.wizard",
            "view_type": "form",
            "view_mode": "form",
        }

    def request_codabox_token(self):
        """
        Called when pressing the "request_codabox_token" button in Codabox
        setting page view.
        :return: a Wizard view
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "view_id": self.env.ref("codabox.codabox_request_token_wizard").id,
            "name": "Request Token",
            "target": "new",
            "res_model": "codabox.credentials.wizard",
            "view_type": "form",
            "view_mode": "form",
        }

    def run_now(self):
        """
        Called when pressing the "run_now" button in Codabox
        setting page view, it fetch Codabox feeds from Codabox API.
        :return: None
        """
        self.env["codabox.feed"].fetch_feed_data()
