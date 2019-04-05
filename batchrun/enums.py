from django.utils.translation import ugettext_lazy as _
from enumfields import Enum


class EventLogKind(Enum):
    STDOUT = 'stdout'
    STDERR = 'stderr'

    class Labels:
        STDOUT = _('Standard output stream')
        STDERR = _('Standard error stream')


class DstHandling(Enum):
    SKIP = 'skip'
    DST_ON = 'dst_on'
    DST_OFF = 'dst_off'

    class Labels:
        SKIP = _('')
        DST_ON = _('')
        DST_OFF = _('')
