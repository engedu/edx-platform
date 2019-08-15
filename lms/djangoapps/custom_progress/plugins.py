from django.utils.translation import ugettext_noop
from xmodule.tabs import CourseTab


class CustomProgressTab(CourseTab):
    """
    The representation of the course teams view type.
    """
    type = "custom_progress"
    name = "Ranking Score"
    title = ugettext_noop("Ranking Score")
    view_name = "custom_progress_view"
    is_default = True
    is_hideable = True

    @classmethod
    def is_enabled(cls, course, user=None):
        return True
