#!/usr/bin/python
# -*- coding: UTF-8 -*-、

# Copyright (c) 2020 Huawei Inc.
#
"""oceanstor_base.py."""

import json
import requests
import logging
import requests.exceptions as r_exc
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

LOG = logging.getLogger(__name__)


class OceanStorBase(object):
    """RestRequests."""

    def __init__(self, base_url, username, password, token=None, verify=False,
                 retries=3, timeout=120, application_type=None):
        """__init__."""
        self.username = username
        self.password = password
        self.verify_ssl = verify
        self.base_url = base_url
        self.headers = {'content-type': 'application/json',
                        'accept': 'application/json',
                        'application-type': application_type}
        self.timeout = 120
        self.retries = retries
        self.session = self._establish_session(username, password, token)

    def _establish_session(self, username, password, token=None):
        """Establish a REST session.
        :returns: session -- object
        """
        session = requests.session()
        session.headers = self.headers
        session.verify = self.verify_ssl
        
        if not token:
            url = "/api/v2/aa/sessions"

            session_url = '{base_url}{url}'.format(base_url=self.base_url, url=url)

            body =  {
                "user_name": username,
                "password": password,
                "scope": 0
            }

            response = session.request(method="POST",
                                       url=session_url,
                                       timeout=self.timeout,
                                       data=json.dumps(body,
                                                       sort_keys=True,
                                                       indent=4))

            if response.json()["result"]["code"] != 0:
                raise Exception("Login Failed {0}".format(response.json()["result"]["description"]))

            token = response.json()['data']['x_auth_token']

        session.headers.update({"X-Auth-Token": token})

        return session

    def request(self, target_url, method, params=None, request_object=None, timeout=None):
        """Send a request to OceanStor target api.
        Valid methods are 'GET', 'POST', 'PUT', 'DELETE'.
        :param target_url: target url --str, url=base_url+target_url
        :param method: method -- str
        :param params: Additional URL parameters -- dict
        :param request_object: request payload -- dict
        :param timeout: optional timeout override -- int
        :returns: server response, status code -- dict, int
        """
        if timeout:
            timeout_val = timeout
        else:
            timeout_val = self.timeout

        if not self.session:
            raise Exception("Please Login")
 
        url = '{base_url}{target_url}'.format(
            base_url=self.base_url, target_url=target_url)
        try:
            if request_object:
                response = self.session.request(
                    method=method, url=url, timeout=timeout_val,
                    data=json.dumps(request_object, sort_keys=True,
                                    indent=4))
            elif params:
                response = self.session.request(method=method, url=url,
                                                params=params,
                                                timeout=timeout_val)
            else:
                response = self.session.request(method=method, url=url,
                                                timeout=timeout_val)
            status_code = response.status_code
            if status_code == 401:
                LOG.error("Unauthentication, please login first")
                raise Exception("Unauthentication, please login first")
            try:
                response = response.json()
            except ValueError:
                response = None
                if not status_code:
                    status_code = None

            LOG.debug('{method} request to {url} has returned with a status '
                      'code of: {sc}.'.format(method=method, url=url,
                                              sc=status_code))
            return response

        except requests.Timeout as error:
            LOG.error(
                'The {method} request to URL {url} timed-out, but may have '
                'been successful. Please check the array. Exception received: '
                '{exc}.'.format(method=method, url=url, exc=error))
            return None

        except r_exc.SSLError as error:
            msg = (
                'The connection to {base} has encountered an SSL error. '
                'Please check your SSL config or supplied SSL cert in Cinder '
                'configuration. SSL Exception message: {m}'.format(
                    base=self.base_url, m=error))
            raise r_exc.SSLError(msg)

        except Exception as error:
            msg = (
                'The connection to {base} has encountered ERROR {m}'.format(
                    base=self.base_url, m=error))
            raise r_exc.BaseHTTPError(msg)


    def rest_request(self, target_url, method,
                     params=None, request_object=None, timeout=None):
        """Send a request to OceanStor target api.
        Valid methods are 'GET', 'POST', 'PUT', 'DELETE'.
        :param target_url: target url --str, url=base_url+target_url
        :param method: method -- str
        :param params: Additional URL parameters -- dict
        :param request_object: request payload -- dict
        :param timeout: optional timeout override -- int
        :returns: server response, status code -- dict, int
        """
        if timeout:
            timeout_val = timeout
        else:
            timeout_val = self.timeout

        if not self.session:
            raise Exception("Please Login")
 
        url = '{base_url}{target_url}'.format(
            base_url=self.base_url, target_url=target_url)
        try:
            if request_object:
                response = self.session.request(
                    method=method, url=url, timeout=timeout_val,
                    data=json.dumps(request_object, sort_keys=True,
                                    indent=4))
            elif params:
                response = self.session.request(method=method, url=url,
                                                params=params,
                                                timeout=timeout_val)
            else:
                response = self.session.request(method=method, url=url,
                                                timeout=timeout_val)
            status_code = response.status_code
            if status_code == 401:
                LOG.error("Unauthentication, please login first")
                raise Exception("Unauthentication, please login first")
            try:
                response = response.json()
            except ValueError:
                response = None
                if not status_code:
                    status_code = None

            LOG.debug('{method} request to {url} has returned with a status '
                      'code of: {sc}.'.format(method=method, url=url,
                                              sc=status_code))
            return response, status_code

        except requests.Timeout as error:
            LOG.error(
                'The {method} request to URL {url} timed-out, but may have '
                'been successful. Please check the array. Exception received: '
                '{exc}.'.format(method=method, url=url, exc=error))
            return None, None

        except r_exc.SSLError as error:
            msg = (
                'The connection to {base} has encountered an SSL error. '
                'Please check your SSL config or supplied SSL cert in Cinder '
                'configuration. SSL Exception message: {m}'.format(
                    base=self.base_url, m=error))
            raise r_exc.SSLError(msg)

        except Exception as error:
            msg = (
                'The connection to {base} has encountered ERROR {m}'.format(
                    base=self.base_url, m=error))
            raise r_exc.BaseHTTPError(msg)

    def close_session(self):
        """Close the current session."""
        self.session.close()
