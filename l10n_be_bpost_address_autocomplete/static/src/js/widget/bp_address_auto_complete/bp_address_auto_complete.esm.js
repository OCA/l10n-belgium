/** @odoo-module */

/**
 * Copyright 2023 ACSONE SA/NV
 */
import {registry} from "@web/core/registry";
import {standardWidgetProps} from "@web/views/widgets/standard_widget_props";

const {Component, onMounted} = owl;

export class BpAddressAutoComplete extends Component {
    setup() {
        super.setup();

        onMounted(() => {
            const element = document.getElementById(this.props.id);
            /**
             * When we receive "onSelectedAddress" event we can autocomplete fields and update record.
             */
            element.addEventListener("onSelectedAddress", (ev) => {
                const value = {};
                if (this.props.fieldStreet !== undefined) {
                    const fiedValues = [];
                    if (ev.detail.streetName !== undefined)
                        fiedValues.push(ev.detail.formatStreetName);
                    if (ev.detail.houseNumber !== undefined)
                        fiedValues.push(ev.detail.formatHouseNumber);
                    if (ev.detail.boxNumber !== undefined)
                        fiedValues.push(ev.detail.formatBoxNumber);
                    value[this.props.fieldStreet] = fiedValues.join(" ");
                }
                if (this.props.fieldLocality !== undefined) {
                    value[this.props.fieldLocality] = ev.detail.locality;
                }
                if (this.props.fieldPostalCode !== undefined) {
                    value[this.props.fieldPostalCode] = ev.detail.postalCode;
                }
                if (this.props.fieldLatitude !== undefined) {
                    value[this.props.fieldLatitude] = ev.detail.latitude;
                }
                if (this.props.fieldLongitude !== undefined) {
                    value[this.props.fieldLongitude] = ev.detail.longitude;
                }
                this.props.record.update(value);
            });
        });
    }
}
BpAddressAutoComplete.template =
    "l10n_be_bpost_address_autocomplete.BpAddressAutoComplete";
BpAddressAutoComplete.props = {
    ...standardWidgetProps,
    id: {type: String, optional: true},
    fieldStreet: {type: String, optional: true},
    fieldLocality: {type: String, optional: true},
    fieldPostalCode: {type: String, optional: true},
    fieldLatitude: {type: String, optional: true},
    fieldLongitude: {type: String, optional: true},
};
BpAddressAutoComplete.extractProps = ({attrs}) => {
    return {
        id: attrs.id,
        fieldStreet: attrs.fieldStreet,
        fieldLocality: attrs.fieldLocality,
        fieldPostalCode: attrs.fieldPostalCode,
        fieldLatitude: attrs.fieldLatitude,
        fieldLongitude: attrs.fieldLongitude,
    };
};
registry
    .category("view_widgets")
    .add("bp_address_auto_complete", BpAddressAutoComplete);
