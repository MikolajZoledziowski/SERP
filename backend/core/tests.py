import json
from django.test import TestCase
from django.urls import reverse
from .models import Query
class SERPViewTests(TestCase):
    def test_no_data(self):
        response = self.client.post(reverse('get_links'))
        self.assertEqual(response.status_code, 500)

    def test_with_query(self):
        response = self.client.post('/core/get_links', {'query': 'facebook'})
        content = json.loads(str(response.content, encoding='utf8'))['data']
        self.assertEqual(len(content['items']), 10)
        self.assertEqual(len(Query.objects.all()), 1)
        self.assertEqual(response.status_code, 200)

    def test_two_query(self):
        response = self.client.post('/core/get_links', {'query': 'facebook'})
        content = json.loads(str(response.content, encoding='utf8'))['data']
        self.assertEqual(len(content['items']), 10)
        self.assertEqual(response.status_code, 200)
        response2 = self.client.post('/core/get_links', {'query': 'facebook'})
        content2 = json.loads(str(response.content, encoding='utf8'))['data']
        self.assertEqual(len(content2['items']), 10)
        self.assertEqual(len(Query.objects.all()), 1)        
        self.assertEqual(response2.status_code, 200)