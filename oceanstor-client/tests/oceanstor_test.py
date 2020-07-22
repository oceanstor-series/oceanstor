"""
Unit tests for OceanStor REST Client
"""
from oceanstor.oceanstor_add_storage import OceanStorStorage


class OceanStorTestBase(object):

    def setup_method(self):
        self.api_token = "12345678-efag"
        self.api_token_data = {"api_token": self.api_token}
        self.target = "1.1.1.1"
        self.client = OceanStorStorage(self.target, "admin", "***",
                                       self.api_token)

    def test_setup_oceanstor_client(self):
        pass
