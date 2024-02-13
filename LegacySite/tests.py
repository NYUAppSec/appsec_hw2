import io
import unittest
import json
from django.test import TestCase, Client
from django.db import connection
from LegacySite.models import Card, User
from django.core.files.uploadedfile import SimpleUploadedFile

"""
Test Database Isolation: 
Each test in Django runs in isolation with a separate test database. 
This means that any data created, modified, or deleted in one test will not affect other tests. 
The test database is created at the start of the test run and destroyed at the end.
"""
class MyTest(TestCase):
    # Django's test run with an empty database. We can populate it with
    # data by using a fixture. You can create the fixture by running:
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
        # Register and login our user to correctly handle session
        self.client = Client()
        self.username, self.password = 'test', 'test'
        self.register_user(self.username, self.password)
        self.client.login(username=self.username, password=self.password)


    def register_user(self, username, password):
        endpoint = '/register'
        data = {'uname' : username, 
                'pword': password, 
                'pword2': password}
        self.client.post(path=endpoint, data=data)
        canLogin = self.client.login(username=username, password=password)
        self.assertTrue(canLogin)


    # Assuming that your database had at least no Card in it,
    # this test should pass.
    def test_get_card(self):
        all_cards = Card.objects.all()
        self.assertEqual(len(all_cards), 0)

    
    def test_buy(self):
        # Make requests to our endpoint and ensure it returned status code 200
        response = self.client.get('/buy/0')
        self.assertEqual(response.status_code, 200)

        # Set our endpoint and data 
        response = self.client.post('/buy/0', {'amount': 100})
        self.assertEqual(response.status_code, 200)
        

    def test_check_card_data_using_SQL_query(self):
        # Recall each test runs in isolation
        # Lets buy a card for this test
        self.test_buy()

        # One way to get a card using a raw SQL query
        cursor = connection.cursor()
        card_query = f"select * from LegacySite_card"
        cards = cursor.execute(card_query).fetchall()
        self.assertNotEqual(cards, [])
        card = cards[0]

        print("\nPrinting card found by using raw SQL query")
        print(card)


    def test_check_card_data_using_Django_ORM(self):
        # Lets buy a card for this test
        self.test_buy()
        user = User.objects.get(username=self.username)

        # Another way to get a card using Django ORM
        card = Card.objects.filter(user=user.pk).order_by('-id')[0]
        card_data = card.data.decode()
        card_data_dict = json.loads(card_data)
        signature = card_data_dict['records'][0]['signature']
        print("\nPrinting card found by using Django ORM")
        print("Card ID: " + str(card.id))
        print("Card Data: " + card_data)
        print("Card Used: " + str(card.used))
        print("Card Signature: " + signature)


    def test_buy_and_use_giftcard_by_selecting(self):
        self.test_buy()

        # We bought a card, so it should be in our database
        user = User.objects.get(username=self.username)
        card = Card.objects.filter(user=user.pk).order_by('-id')[0]

        # The user should be able to use a card by selecting it at the /use endpoint
        # The request would look like the following
        response = self.client.post('/use.html', {'card_id': card.id})
        self.assertEqual(response.status_code, 200, msg='Confirm that the POST request to use Giftcard amount 101')


    # You can also skip tests
    @unittest.skip("Skipping test_buy_and_use_giftcard_by_uploading")
    def test_buy_and_use_giftcard_by_uploading(self):
        # Make a request to our endpoint and ensure it returned status code 200
        response = self.client.post('/buy/0', {'amount': 102})
        self.assertEqual(response.status_code, 200)

        # We bought a card, so it should be in our database
        user = User.objects.get(username=self.username)
        card = Card.objects.filter(user=user.pk).order_by('-id')[0]

        # When we buy a card, the site also returns the card data
        card_data = response.content

        # Now we can upload a giftcard
        data = {
            'card_supplied': 'True',
            'card_fname': 'Test',
            'card_data': io.BytesIO(card_data),
            }
        response = self.client.post('/use.html', data)
        self.assertEqual(response.status_code, 200, msg='Confirm that the request to /use Giftcard works')
        
        # We can also verify that the card was used by checking the response and the database
        self.assertIn('Card used!', response.content.decode())
        self.assertTrue(Card.objects.get(pk=card.id).used, msg='Checking the database, it says the giftcard wasn\'t used.')
        

    @unittest.skip("Skipping test_use_unknown_giftcard")
    def test_use_unknown_giftcard(self):
        # We can also manually create giftcard data
        payload = " [sample payload] "
        card_content = f"""{{"merchant_id": "NYU Apparel Card", 
                             "customer_id": "{self.username}", 
                             "total_value": "10", 
                             "records":     [{{ "record_type": "amount_change", 
                                                "amount_added": 2000, 
                                                "signature": "{payload}"}}]}}""".encode('utf-8')
        
        card_data = SimpleUploadedFile('giftcard', card_content)
        data = {'card_data': card_data,
                'card_supplied': True,
                'card_fname': 'card'}
        response = self.client.post('/use', data)
        if 'Card used!' in response.content.decode():
            self.fail("Uh oh! Our site is saying that a nonexistent card was used!")
