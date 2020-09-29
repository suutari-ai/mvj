from io import StringIO

import pytest
from django.core.management import call_command

from leasing.enums import PlotType
from leasing.models import LeaseArea


@pytest.mark.django_db
def test_lease_area_type_area_attaching_to_lease_area(
    lease_area_factory,
    plan_unit_factory,
    plot_factory,
    area_with_intersects_test_data,
    lease_test_data,
):
    out = StringIO()
    args = []
    opts = {}

    area = area_with_intersects_test_data["area"]
    lease = lease_test_data["lease"]

    # Add lease area to lease
    lease_area = lease_area_factory(
        lease=lease,
        identifier=area_with_intersects_test_data["area"].get_land_identifier(),
        area=1000,
        section_area=1000,
    )

    # Add plan unit to contract
    plan_unit_factory(
        identifier="PU1", area=1000, lease_area=lease_area, in_contract=True
    )

    # Extra plot and plan unit which are not in contracts
    extra_plot = plot_factory(
        identifier="P1", area=1000, type=PlotType.REAL_PROPERTY, lease_area=lease_area
    )
    extra_plan_unit = plan_unit_factory(
        identifier="PU2", area=1000, lease_area=lease_area
    )

    # Geometry data is empty
    assert lease_area.geometry is None

    # Execute command for test
    call_command("attach_areas", stdout=out, *args, **opts)

    # The geometry data has updated for exist lease area
    assert "Lease area FOUND. SAVED" in out.getvalue()
    lease_area = LeaseArea.objects.get(identifier=area.get_land_identifier())
    assert area.geometry == lease_area.geometry

    # Extra plot and plan unit has removed as they are not in contracts
    assert (
        "Cleared existing current Plots ((1, {'leasing.Plot': 1})) and PlanUnits ((1, {'leasing.PlotSearchTarget': 0, 'leasing.PlanUnit': 1})) not in contract"  # noqa: E501
        in out.getvalue()
    )
    assert lease_area.plots.filter(pk=extra_plot.id).count() == 0
    assert lease_area.plan_units.filter(pk=extra_plan_unit.id).count() == 0

    # Plot saved
    assert lease_area.plots.filter(in_contract=False).count() == 1
    plot = lease_area.plots.filter(in_contract=False).first()
    assert (
        "Lease #{} {}: Plot #{} ({}) saved".format(
            lease.id, lease.identifier, plot.id, plot.type
        )
        in out.getvalue()
    )

    # Plan unit saved
    assert lease_area.plan_units.filter(in_contract=False).count() == 1
    plan_unit = lease_area.plan_units.filter(in_contract=False).first()
    assert (
        "Lease #{} {}: PlanUnit #{} saved".format(
            lease.id, lease.identifier, plan_unit.id
        )
        in out.getvalue()
    )

    # Intersection area too small
    assert "intersection area too small" in out.getvalue()

    # No area value in intersect area's metadata
    assert "no 'area' value in metadata" in out.getvalue()