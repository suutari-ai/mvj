from django.utils.encoding import force_text
from enumfields.drf import EnumField
from rest_framework.fields import DecimalField
from rest_framework.metadata import SimpleMetadata
from rest_framework.relations import PrimaryKeyRelatedField

from field_permissions.metadata import FieldPermissionsMetadataMixin
from leasing.models import Contact, Decision, Lease
from users.models import User


class FieldsMetadata(FieldPermissionsMetadataMixin, SimpleMetadata):
    """Returns metadata for all the fields and the possible choices in the
    serializer even when the fields are read only.

    Additionally adds decimal_places and max_digits info for DecimalFields."""

    def determine_metadata(self, request, view):
        metadata = super().determine_metadata(request, view)

        serializer = view.get_serializer()
        metadata["fields"] = self.get_serializer_info(serializer)

        # TODO: experiment
        if hasattr(serializer, 'Meta') and serializer.Meta.model:
            methods = {
                'GET': False,
                'OPTIONS': False,
                'HEAD': False,
                'POST': False,
                'PUT': False,
                'PATCH': False,
                'DELETE': False,
            }

            for permission in view.get_permissions():
                if not hasattr(permission, 'get_required_permissions'):
                    continue

                for method in methods.keys():
                    perms = permission.get_required_permissions(method, serializer.Meta.model)
                    methods[method] = request.user.has_perms(perms)

            metadata['methods'] = methods

        return metadata

    def get_field_info(self, field):
        field_info = super().get_field_info(field)

        if isinstance(field, DecimalField):
            field_info['decimal_places'] = field.decimal_places
            field_info['max_digits'] = field.max_digits

        if isinstance(field, PrimaryKeyRelatedField) or isinstance(field, EnumField):
            # TODO: Make configurable
            if hasattr(field, 'queryset') and field.queryset.model in (User, Lease, Contact, Decision):
                return field_info

            field_info['choices'] = [{
                'value': choice_value,
                'display_name': force_text(choice_name, strings_only=True)
            } for choice_value, choice_name in field.choices.items()]

        return field_info
