import unittest
from shorten_url_service import *
from parameterized import parameterized
import sqlite3
from decouple import config


class ShortenURLServiceTest(unittest.TestCase):

    def setUp(self):
        """ Runs before every test """
        self.test_client = app.test_client()
        connection = sqlite3.connect('database.db')
        with open(config("SCHEMA_PATH")) as f:
            connection.executescript(f.read())
        connection.commit()
        connection.close()

    def test_shorten_no_url(self):
        response = self.test_client.post('/shorten')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["error_message"], "Url not present")
        self.assertEqual(response.json["status_code"], 400)

    @parameterized.expand(["ewx123_ewx1233", "ewx1233", "e_33", "3e", ""])
    def test_invalid_size_shortCode(self, shortcode):
        response = self.test_client.post('/shorten', json={"url": "https://www.energyworx.com/",
                                                           "shortcode": shortcode})

        self.assertEqual(response.status_code, 412)
        self.assertEqual(response.json["error_message"], "The provided shortcode is invalid")
        self.assertEqual(response.json["status_code"], 412)

    @parameterized.expand(["3drf)r", "ewx!33", "Aret)T", "Y67d/t", "Y67d/ "])
    def test_invalid_symbol_shortCode(self, shortcode):
        response = self.test_client.post('/shorten', json={
            "url": "https://www.energyworx.com/",
            "shortcode": shortcode})

        self.assertEqual(response.status_code, 412)
        self.assertEqual(response.json["error_message"], "The provided shortcode is invalid")
        self.assertEqual(response.json["status_code"], 412)

    def test_random_shortCode(self):
        response_1 = self.test_client.post('/shorten', json={
            "url": "https://www.energyworx.com/"})
        response_2 = self.test_client.post('/shorten', json={
            "url": "https://www.energyworx.com/"})
        shortcode_1 = response_1.json["shortcode"]
        shortcode_2 = response_2.json["shortcode"]

        self.assertEqual(response_1.status_code, 201)
        self.assertEqual(response_2.status_code, 201)
        self.assertTrue(re.match(r"^[A-Za-z0-9_]+$", shortcode_1) and len(shortcode_1) == 6)
        self.assertTrue(re.match(r"^[A-Za-z0-9_]+$", shortcode_2) and len(shortcode_2) == 6)
        self.assertTrue(shortcode_1 != shortcode_2)

    @parameterized.expand(["3dEfRt", "eWx_33", "AAAAAA", "097867", "______"])
    def test_valid_shortCode(self, shortcode):
        response = self.test_client.post('/shorten', json={
            "url": "https://www.energyworx.com/",
            "shortcode": shortcode})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["shortcode"], shortcode)

    def test_duplicated_shortCode(self):
        response = self.test_client.post('/shorten', json={
            "url": "https://www.energyworx.com/",
            "shortcode": "4fEfRt"})

        response_2 = self.test_client.post('/shorten', json={
            "url": "https://www.energyworx.com/",
            "shortcode": "4fEfRt"})

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["shortcode"], "4fEfRt")
        self.assertEqual(response_2.status_code, 409)
        self.assertEqual(response_2.json["error_message"], "Shortcode already in use")
        self.assertEqual(response_2.json["status_code"], 409)

    @parameterized.expand(["_3rTfT", "eWx4_3"])
    def test_get_nonexistent_shortcode(self, shortcode):
        response = self.test_client.get('/' + str(shortcode))

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error_message"], "Shortcode not found")
        self.assertEqual(response.json["status_code"], 404)

    def test_get_shortcode(self):
        self.test_client.post('/shorten', json={
            "url": "https://www.energyworx.com/",
            "shortcode": "4dEfRt"})

        response = self.test_client.get('/4dEfRt')

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["location"], "https://www.energyworx.com/")

    @parameterized.expand(["3dE_Rt", "eWx_33"])
    def test_get_invalid_shortcode_stats(self, shortcode):
        response = self.test_client.get('/' + str(shortcode) + '/stats')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json["error_message"], "Shortcode not found")
        self.assertEqual(response.json["status_code"], 404)

    def test_get_shortcode_stats_no_redirect(self):
        before_create = dt.datetime.utcnow().isoformat()
        self.test_client.post('/shorten', json={
            "url": "https://www.energyworx.com/",
            "shortcode": "3_EERt"})

        after_create = dt.datetime.utcnow().isoformat()
        response = self.test_client.get('/3_EERt/stats')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["redirectCount"], 0)
        self.assertTrue(before_create < response.json["created"] < after_create)
        self.assertEqual(response.json["lastRedirect"], None)

    def test_get_shortcode_stats_with_redirect(self):
        before_create = dt.datetime.utcnow().isoformat()
        self.test_client.post('/shorten', json={
            "url": "https://www.energyworx.com/",
            "shortcode": "3dEERt"})
        after_create = dt.datetime.utcnow().isoformat()
        self.test_client.get('3dEERt')
        after_get = dt.datetime.utcnow().isoformat()
        response = self.test_client.get('/3dEERt/stats')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["redirectCount"], 1)
        self.assertTrue(before_create < response.json["created"] < after_create)
        self.assertTrue(after_create < response.json["lastRedirect"] < after_get)
