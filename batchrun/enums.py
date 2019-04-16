from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class EventLogKind(Enum):
    STDOUT = 'stdout'
    STDERR = 'stderr'

    class Labels:
        STDOUT = _('Standard output stream')
        STDERR = _('Standard error stream')
