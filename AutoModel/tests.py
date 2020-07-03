from django.test import TestCase
from AutoModel.models import Host, Dependency, Result, Source, TestDetail, ComVar,TestReport

# Create your tests here.
class HostModelTests(TestCase):
    """docstring for HostModelTests"""
    def test_host(self):
        self.assertIs(future_question.was_published_recently(), False)