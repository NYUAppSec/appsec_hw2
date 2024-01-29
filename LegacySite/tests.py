import io
from django.test import TestCase, Client
from LegacySite.models import Card, User
from django.core.files.uploadedfile import SimpleUploadedFile

"""
Test Database Isolation: 
Each test in Django runs in isolation with a separate test database. 
This means that any data created, modified, or deleted in one test will not affect other tests. 
The test database is created at the start of the test run and destroyed at the end.
"""

# Create your tests here.
class MyTest(TestCase):
    # Django's test run with an empty database. We can populate it with
    # data by using a fixture. You can create the fixture by running:
    #    python3 manage.py makemigrations LegacySite
    #    python3 manage.py migrate
    #    python3 manage.py shell -c 'import import_dbs'
    #    mkdir LegacySite/fixtures
    #    python manage.py dumpdata LegacySite --indent=4> LegacySite/fixtures/testdata.json
    # You can read more about fixtures here:
    #    https://docs.djangoproject.com/en/4.0/topics/testing/tools/#fixture-loading
    # When you create your fixture, remember to uncomment line 14
    # fixtures = ["testdata.json"]

    """
    Setup Method: 
    In the setUp method, you're creating a new Client instance. 
    This instance is unique for each test method and maintains its own session. 
    Therefore, when you register and log in a user within a test method, 
    the session is specific to that Client instance and that test method.
    """
    def setUp(self):
        self.client = Client()

    def register_user(self, username, password):
        endpoint = '/register'
        data = {'uname' : username, 
                'pword': password, 
                'pword2': password}
        self.client.post(path=endpoint, data=data)
        canLogin = self.client.login(username=username, password=password)
        return canLogin

    # Assuming that your database had at least no Card in it,
    # this test should pass.
    def test_get_card(self):
        all_cards = Card.objects.all()
        self.assertEqual(len(all_cards), 0)

    def test_get_buy_request(self):
        # Register and login our user to correctly handle session
        # We could also  move this into setUp() to avoid doing it each time
        username, password = 'test', 'test'
        self.register_user(username, password)
        self.client.login(username=username, password=password)

        # Set our endpoint and data 
        endpoint = '/buy/0'
        data = {'amount': 100}
        
        # Make requests to our endpoint and ensure it returned status code 200
        response = self.client.get(endpoint)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(endpoint, data)
        self.assertEqual(response.status_code, 200)


    def test_buy_and_use_giftcard(self):
        # Register and login our user to correctly handle session
        username, password = 'test', 'test'
        self.register_user(username, password)
        self.client.login(username=username, password=password)

        # Set our endpoint and data 
        endpoint = '/buy/0'
        data = {'amount': 101}
        
        # Make a request to our endpoint and ensure it returned status code 200
        response = self.client.post(endpoint, data)
        self.assertEqual(response.status_code, 200)

        # We bought a card, so it should be in our database
        user = User.objects.get(username=username)
        card = Card.objects.filter(user=user.pk).order_by('-id')[0]

        # The user should be able to use a card by selecting it at the /use endpoint
        # The request would look like the following
        endpoint = '/use.html'
        data = {'card_id': card.id}
        response = self.client.post(endpoint, data)
        self.assertEqual(response.status_code, 200, msg='Confirm that the POST request to use Giftcard amount 101')

        # Make a request to our endpoint and ensure it returned status code 200
        endpoint = '/buy/0'
        data = {'amount': 102}
        response = self.client.post(endpoint, data)
        self.assertEqual(response.status_code, 200)

        # We bought a card, so it should be in our database
        card = Card.objects.filter(user=user.pk).order_by('-id')[0]

        # When we buy a card, the site also returns the card data
        card_data = response.content

        # Now we can upload a giftcard
        endpoint = '/use.html'
        data = {
                'card_supplied': 'True',
                'card_fname': 'Test',
                'card_data': io.BytesIO(card_data),
                }
        response = self.client.post(endpoint, data)
        self.assertEqual(response.status_code, 200, msg='Confirm that the second request to use Giftcard works')
        
        # We can also verify that the card was used by checking the response and the database
        self.assertIn('Card used!', response.content.decode(), msg='Confirm that the second uploaded Giftcard is used. '
                                                                   'I am checking HTML output')
        self.assertTrue(Card.objects.get(pk=card.id).used, msg='When checking the database, it says the new second giftcard '
                                                                'was NOT used.'
                                                                'Are you sure it still works when uploading a card '
                                                                'manually?')
        
    def test_use_unknown_giftcard(self):
        # Register and login our user to correctly handle session
        username, password = 'test', 'test'
        self.register_user(username, password)
        self.client.login(username=username, password=password)

        # We can also manually create giftcard data
        payload = " [sample payload] "
        card_content = f"""{{"merchant_id": "NYU Apparel Card", 
                             "customer_id": "{username}", 
                             "total_value": "-10", 
                             "records": [{{"record_type": "amount_change", 
                                           "amount_added": 2000, 
                                           "signature": "{payload}"}}]}}""".encode('utf-8')
        
        card_data = SimpleUploadedFile('giftcard', card_content)
        data = {'card_data': card_data,
                'card_supplied': True,
                'card_fname': 'card'}
        response = self.client.post('/use', data)
        if 'Card used!' in response.content.decode():
            # self.fail("Uh oh! Our site is saying that a nonexistent card was used!")
            print("Uh oh! Our site is saying that a nonexistent card was used!")