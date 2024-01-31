from nautobot.apps.jobs import Job, ChoiceVar, StringVar, register_jobs
from nautobot.extras.models import Status
from nautobot.dcim.models.locations import Location, LocationType
from django.core.exceptions import ObjectDoesNotExist


name = "Demo Jobs"


class DemoJob(Job):
    """A Demo Job."""

    class Meta:
        name = "Create Site"
        description = "A job used to demonstrate the jobs feature of Nautobot"

    REGION_CHOICES = (
        ("West", "West"),
        ("Central", "Central"),
        ("East", "East"),
    )

    STATUS_CHOICES = (
        ("Active", "Active"),
        ("Planned", "Planned"),
    )

    region_choice = ChoiceVar(
        choices=REGION_CHOICES,
        description="Select the region you would like to add a site to. If it does not exist, it will be created.",
    )

    site_status_choice = ChoiceVar(
        choices=STATUS_CHOICES,
        description="The selected status will apply to the new site.",
    )

    site_name = StringVar(required=True)

    def run(self, region_choice, site_status_choice, site_name):
        self.logger.info(
            msg=f"Attempting to create a new site in the {region_choice} region..."
        )

        location_types = [
            {"name": "Region", "parent": None},
            {"name": "Site", "parent": "Region"}
        ]

        # Verify that the required Location Types exist; if not, create them.
        for lt in location_types:
            try:
                # Check for existing Location Type
                location_type = LocationType.objects.get(name=lt["name"])
                self.logger.info(
                    msg=f"Location Type {location_type.name} exists and will be used",
                    extra={"object": location_type}
                )
            except ObjectDoesNotExist:
                # Create Location Type if necessary
                self.logger.warning(
                    msg=f"Location Type {lt['name']} does not exist and will be created."
                )
                location_type = LocationType.objects.create(
                    name=lt["name"],
                    parent=LocationType.objects.get(name=lt["parent"]) if lt["parent"] else None
                )
                location_type.validated_save()
                self.logger.info(
                    msg=f"Location Type {location_type.name} was created.",
                    extra={"object": location_type}
                )

        # Handle Region
        try:
            # Check for existing Region
            region = Location.objects.get(name=region_choice)
            self.logger.info(
                msg=f"Region {region.name} exists and will be used.",
                extra={"object": region}
            )
        except ObjectDoesNotExist:
            # Create Region if necessary
            self.logger.warning(
                msg=f"Region {region_choice} does not exist and will be created."
            )
            region = Location.objects.create(
                name=region_choice,
                location_type=LocationType.objects.get(name="Region"),
                status=Status.objects.get(name=site_status_choice)
            )
            region.validated_save()
            self.logger.info(
                msg=f"Region {region.name} was created.",
                extra={"object": region}
            )

        # Handle Site
        try:
            # Check for existing Site
            site = Location.objects.get(name=site_name)
            self.logger.error(
                message=f"Site {site_name} already exists! Stopping Job!"
            )
        except ObjectDoesNotExist:
            # Create Site if unique
            self.logger.info(
                msg=f"Site {site_name} does not exist and will be created."
            )
            site = Location.objects.create(
                name=site_name,
                location_type=LocationType.objects.get(name="Site"),
                status=Status.objects.get(name=site_status_choice),
                parent=region
            )
            site.validated_save()
            self.logger.info(
                msg=f"Site {site.name} was created",
                extra={"object": site}
            )

register_jobs(DemoJob)
