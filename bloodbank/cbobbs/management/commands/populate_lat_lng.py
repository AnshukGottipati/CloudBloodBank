from django.core.management.base import BaseCommand
from cbobbs.models import BloodBank

from django.core.management.base import BaseCommand
from cbobbs.models import BloodBank

class Command(BaseCommand):
    help = 'Geocode BloodBank addresses to populate latitude and longitude'

    def handle(self, *args, **kwargs):
        # Get all BloodBank records with missing latitude and longitude
        blood_banks = BloodBank.objects.filter(latitude__isnull=True, longitude__isnull=True)

        for bb in blood_banks:
            full_address = f"{bb.address}, {bb.city}, {bb.state} {bb.zipcode}"
            self.stdout.write(f"Geocoding address: {full_address}")

            # Call geocode method (returns a dict)
            geocoded = bb.geocode_address(full_address)

            if geocoded:
                bb.latitude = geocoded['lat']
                bb.longitude = geocoded['lng']
                bb.save()
                self.stdout.write(f"✅ Updated {bb.name}: {bb.latitude}, {bb.longitude}")
            else:
                self.stdout.write(f"❌ Failed to geocode address for {bb.name}")
