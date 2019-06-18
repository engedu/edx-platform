define([
    'jquery', 'js/models/settings/notification', 'js/views/settings/notify'
], function($, NotificationDetailModel, NotifyView) {
    'use strict';
    return function(detailsUrl) {
        var model;
        // highlighting labels when fields are focused in
        $('form :input')
            .focus(function() {
                $('label[for="' + this.id + '"]').addClass('is-focused');
            })
            .blur(function() {
                $('label').removeClass('is-focused');
            });

        model = new NotificationDetailModel();
        model.urlRoot = detailsUrl;
        model.fetch({
            success: function(model) {
                var editor = new NotifyView({
                    el: $('.settings-notification'),
                    model: model
                });
                editor.render();
            },
            reset: true
        });
    };
});
