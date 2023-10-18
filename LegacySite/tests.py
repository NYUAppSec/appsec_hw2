from django.test import TestCase,Client
from LegacySite.models import Card
import io
from LegacySite.models import User

# Create your tests here.

class MyTest(TestCase):
    # Django's test run with an empty database. We can populate it with
    # data by using a fixture. You can create the fixture by running:
    #    mkdir LegacySite/fixtures
    #    python manage.py dumpdata LegacySite > LegacySite/fixtures/testdata.json
    # You can read more about fixtures here:
    #    https://docs.djangoproject.com/en/4.0/topics/testing/tools/#fixture-loading
    fixtures = ["testdata.json"]

    def setUp(self):
        self.client = Client()

    # Assuming that your database had at least one Card in it, this
    # test should pass.
    def test_get_card(self):
        allcards = Card.objects.all()
        self.assertNotEqual(len(allcards), 0)

    def test_xss(self):
        att = "<script>alert('no xss protection available!')</script>"
        atp = {'director': att}
        response = self.client.get('/buy.html', atp)
        if response.status_code==400:
            print("xss not successful")

    def test_xsrf(self):
        self.client = Client(enforce_csrf_checks=True)
        response = self.client.post('/gift/0', {'username':'test2','amount':'123456'})
        if response.status_code==302:
            print("XSRF attack not successful! Forbidden error")

    def test_sqlinjection(self):
        client= Client()
        client.login(username='test2',password='attack1@')
        with open('part1/sqlattack.gftcrd','rb') as f:
            response = client.post('/use.html',
            {
                'card_supplied': 'True',
                'card_fname':'sqlattack.gftcrd',
                'card_data': f
            }
            )
        self.assertTrue(response.status_code,200)
        self.assertTemplateUsed(response, 'use-card.html')
        self.assertNotContains(response,'78d2')

    def test_commandinjection(self):
        client=Client()
        client.login(username='test2',password='attack1@')
        with open('part1/cmdi.gftcrd','rb') as f:
            response = client.post('/use.html',
            {
                'card_supplied': 'True',
                'card_fname':'appsec & touch test.txt ;',
                'card_data': f
            }
            )
        try:
            with open('test.txt', 'rb' ) as f:
                raise "Error"
        except:
            pass
    
    def test_buy_and_use(self):
        client = Client()
        client.login(username='test2', password='attack1@')
        user = User.objects.get(username='test2')
        response = client.post('/buy/4', {'amount': 1337})
        self.assertEqual(response.status_code, 200)
        # Get the card that was returned
        card = Card.objects.filter(user=user.pk).order_by('-id')[0]
        card_data = response.content
        response = client.post('/use.html',
            {
                'card_supplied': 'True',
                'card_fname': 'Test',
                'card_data': io.BytesIO(card_data),
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Card used!', response.content)
        self.assertTrue(Card.objects.get(pk=card.id).used)
