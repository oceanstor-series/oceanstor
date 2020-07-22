# (c) 2020, Huawei, Inc
# BSD-3 Clause (see COPYING or https://opensource.org/licenses/BSD-3-Clause)
from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible_collections.oceanstor_series.oceanstor.plugins.modules.hw_oceanstor_manage import HuaweiOceanStorManage
from units.modules.utils import ModuleTestCase, set_module_args


class HuaweiOceanStorManageTest(ModuleTestCase):

    REQUIRED_PARAMS = {
        "api_url": "192.168.10.11",
        "api_port": 8088,
        "api_username": "admin",
        "api_password": "password"
    }

    def _set_args(self, args=None):
        module_args = self.REQUIRED_PARAMS.copy()
        if args is not None:
            module_args.update(args)
        set_module_args(module_args)

    def test_get_token_success(self):
        self._set_args()
        HuaweiOceanStorManage()
