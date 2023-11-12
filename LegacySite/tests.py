from django.test import TestCase, Client
from LegacySite.models import Card


# Create your tests here.
class MyTest(TestCase):
    # Django's test run with an empty database. We can populate it with
    # data by using a fixture. You can create the fixture by running:
    #    mkdir LegacySite/fixtures
    #    python manage.py dumpdata LegacySite --indent=4> LegacySite/fixtures/testdata.json
    # You can read more about fixtures here:
    #    https://docs.djangoproject.com/en/4.0/topics/testing/tools/#fixture-loading
    # When you create your fixture, remember to uncomment line 14
    # fixtures = ["testdata.json"]

    def setUp(self):
        self.client = Client()

    # Assuming that your database had at least no Card in it,
    # this test should pass.
    def test_get_card(self):
        all_cards = Card.objects.all()
        self.assertEqual(len(all_cards), 0)

    def test_get_request(self):
        response = self.client.get('/buy')
        self.assertEqual(response.status_code, 200)
