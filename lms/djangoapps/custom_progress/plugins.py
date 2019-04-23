from django.utils.translation import ugettext_noop
from courseware.tabs import EnrolledTab
from django.conf import settings


class CustomProgressTab(EnrolledTab):
    """
    The representation of the course teams view type.
    """
    type = "custom_progress"
    name = "Custom Progress"
    title = ugettext_noop("Custom Progress")
    view_name = "custom_progress_view"
    is_default = False
    is_hideable = True

    @classmethod
    def is_enabled(cls, course, user=None):
        return True
