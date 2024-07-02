from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm, LargeFileForm
import pandas as pd
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile


class TestRegisterView(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse('register')
    def test_register_view_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIsInstance(response.context['form'], CustomUserCreationForm)
    def test_register_view_post_valid_form(self):
        response = self.client.post(self.register_url, {
            'username': 'tester',
            'email': 'tester@gmail.com',
            'password1': 'password123',
            'password2': 'password123'
        })
        self.assertRedirects(response, reverse('custom_login'))
        self.assertTrue(User.objects.filter(username='tester').exists())
    def test_register_view_post_invalid_form(self):
        response = self.client.post(self.register_url, {
            'username': 'testuser',
            'email': 'tester@gmail.com',
            'password1': 'password123',
            'password2': 'differentpassword'  # Invalid password confirmation
        })
        # Check if the form errors are present in the response context
        self.assertEqual(response.status_code, 200)  # Form errors keep the status code 200
        form = response.context['form']
        self.assertFalse(form.is_valid())
        self.assertFormError(form, 'password2', "Password don't match")
class TestCustomLoginView(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('custom_login')
        self.user = User.objects.create_user(username='tester', password='password123')

    def test_login_view_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIsInstance(response.context['form'], AuthenticationForm)

    def test_login_view_post_valid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'tester',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('base'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_view_post_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'tester',
            'password': 'wrongpassword'  # Invalid password
        })
        self.assertEqual(response.status_code, 200)  # Form errors keep the status code 200
        self.assertFalse(response.context['form'].is_valid())
        self.assertIn('Please enter a correct username and password. Note that both fields may be case-sensitive.', response.context['form'].non_field_errors())

class TestCustomLogoutView(TestCase):
    def setUp(self):
        self.client = Client()
        self.logout_url = reverse('custom_logout')
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client.login(username='tester', password='password123')
    def test_logout_view(self):
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, reverse('custom_login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class TestUploadFileView(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_file_url = reverse('upload_file')

    def test_upload_file_view_get(self):
        response = self.client.get(self.upload_file_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'upload-file.html')
        self.assertIsInstance(response.context['form'], LargeFileForm)

    def test_upload_file_view_post_invalid_form(self):
        # Simulate posting invalid data (empty data here, adjust as needed)
        response = self.client.post(self.upload_file_url, {})

        # Check if form errors are present in the response context
        self.assertEqual(response.status_code, 200)  # Form errors keep the status code 200

        # Retrieve the form from the response context
        form = response.context['form']

        # Assert that the form has errors related to the 'file' field
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['file'], ['This field is required.'])




class TestCountRecordsView(TestCase):
    def setUp(self):
        self.client = Client()
        self.count_records_url = reverse('count_records')
        self.csv_file_path = r'C:\Users\Tanay\Desktop\Test\sample\cmp_data1.csv'

    def test_count_records_view_get_method(self):
        # Mock df with data from CSV file
        mock_df = pd.read_csv(self.csv_file_path)
        with patch('sampleapp.views.df', mock_df):
            response = self.client.get(self.count_records_url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['content-type'], 'application/json')
            self.assertIn('count', response.json())

    def test_count_records_view_post_method(self):
        response = self.client.post(self.count_records_url)
        self.assertEqual(response.status_code, 405)  # Method not allowed