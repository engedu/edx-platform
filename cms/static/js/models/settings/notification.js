define(['backbone', 'underscore', 'gettext', 'js/models/validation_helpers', 'js/utils/date_utils'],
    function(Backbone, _, gettext, ValidationHelpers, DateUtils) {
        var NotificationDetail = Backbone.Model.extend({
            defaults: {
                notification: []
            }
        });

        return NotificationDetail;
    }); // end define()
