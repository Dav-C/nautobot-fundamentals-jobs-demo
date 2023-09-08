from nautobot.extras.jobs import Job, ChoiceVar, StringVar
from nautobot.extras.models import Status
from nautobot.dcim.models.sites import Region, Site
from django.core.exceptions import ObjectDoesNotExist


name = "Demo Jobs"


class DemoJob(Job):
    """A Demo Job."""

    class Meta:
        name = "Create Site"
        description = "A job used to demonstrate the jobs feature of Nautobot"


    REGION_CHOICES = (
        ('West', 'West'),
        ('Central', 'Central'),
        ('East', 'East'),
    )

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('planned', 'Planned'),
    )

    region_choice = ChoiceVar(
        choices=REGION_CHOICES,
        description="Select the region you would like to add a "
                    "site and to. If the site does not"
                    "exist, it will be created."
    )
    site_status_choice = ChoiceVar(
        choices=STATUS_CHOICES,
        description="The selected status will apply to the new site."
    )

    site_name = StringVar(required=True)

    def run(self, data, commit):
        self.log_info(message=f"Attempting to create a site in the "
                              f"{data.get('region_choice')} region...")

        try:
            # Check for existing Region
            region = Region.objects.get(name=data.get('region_choice'))
            self.log_warning(obj=region,
                             message=f"Region {region} exists and will be used."
                             )
        except ObjectDoesNotExist:
            # Create Region if necessary
            self.log_warning(message=f"A region named {data.get('region_choice')} "
                                     f"does not exist and will be created."
                             )
            new_region = Region.objects.create(
                name=data.get('region_choice'),
                slug=data.get('region_choice').lower(),
            )
            new_region.validated_save()
            self.log_success(
                obj=new_region, message=f"{new_region.name} Region created"
            )
        try:
            # Check for existing Site
            Site.objects.get(
                name=data.get('site_name'),
            )
            self.log_failure(message=f"A Site with the name {data.get('site_name')} "
                                     f"already exists. A new Site will not be "
                                     f"created.")
        except ObjectDoesNotExist:
            # Create Site if unique
            self.log_info(message=f"A Site with the name {data.get('site_name')} "
                                  f"does not exist in Region {data.get('region_choice')} "
                                  f"and will be created.")

            status = Status.objects.get(slug=data.get('site_status_choice'))
            region = Region.objects.get(name=data.get('region_choice'))

            new_site = Site.objects.create(
                name=data.get('site_name'),
                slug=data.get('site_name').lower().replace(" ", "-"),
                region=region,
                status=status,
            )
            new_site.validated_save()
            self.log_success(
                obj=new_site, message=f"{new_site.name} Site created"
            )


jobs = [DemoJob]
