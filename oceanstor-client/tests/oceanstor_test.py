"""
Unit tests for OceanStor REST Client
"""

class OceanStorTestBase(object):

    def setup_method(self):
        self.api_token = "12345678-efag"
        self.api_token_data = {"api_token": self.api_token}
        self.target = "1.1.1.1"