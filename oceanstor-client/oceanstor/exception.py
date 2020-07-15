
class OceanStorError(Exception):
    """Exception type raised by OceanStor object.
    """
    def __init__(self, reason):
        self.reason = reason
        super(OceanStorError, self).__init__(reason)

    def __str__(self):
        return "OceanStorError: {0}".format(self.reason)

class OceanStorParamError(OceanStorError):
    """Exception type raised by OceanStor param.
    """
    def __init__(self, param):
        self.param = param
        super(OceanStorParamError, self).__init__(param)

    def __str__(self):
        return "OceanStorError Rest API param error: {0}".format(self.param)


class OceanStorHTTPError(OceanStorError):
    """Exception raised as a result of response status code.

    """
    def __init__(self, target, response):
        super(OceanStorHTTPError, self).__init__(response["data"])
        self.target = target
        self.code = response["result"]["code"]
        self.description = response["result"]["description"]
        self.suggestion = response["result"]["suggestion"]

    def __str__(self):
        msg = ("OceanStorHTTPError status code {0} returned by REST API"
               "Target URL {1}\nDescription: {2}\nSuggestion {3}")
        return msg.format(self.code, self.target,
                          self.description, self.suggestion)