/** @odoo-module **/

import { BinaryField } from "@web/views/fields/binary/binary_field";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useFileViewer } from "@web/core/file_viewer/file_viewer_hook";
import { useState } from "@odoo/owl";

patch(BinaryField.prototype, {
    setup(...args) {
        super.setup(...args);
        this.store = useService("mail.store");
        this.fileViewer = useFileViewer();
        this.notification = useService("notification");
        this.messaging = useState(useService("mail.messaging"));
    },
    async _onFilePreview(ev){
        ev.preventDefault();
        ev.stopPropagation();
        var self = this;

        var match = self.props.record.data.mimetype.match("(image|video|application/pdf|text)");
        if(match){
            const attachment = self.store.Attachment.insert({
                id: self.props.record.resId,
                filename: self.props.record.data.name,
                name: self.props.record.data.name,
                mimetype: self.props.record.data.mimetype,
            });
            self.fileViewer.open(attachment)
        }else{
            self.notification.add(_t("This file type is not supported."), {
                type: "danger",
            });
        }
    }
})