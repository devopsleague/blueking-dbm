# -*- coding: utf-8 -*-
"""
TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-DB管理系统(BlueKing-BK-DBM) available.
Copyright (C) 2017-2023 THL A29 Limited, a Tencent company. All rights reserved.
Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at https://opensource.org/licenses/MIT
Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""

import logging
from collections import defaultdict
from typing import Any, Dict, List, Optional

from django.utils.translation import ugettext as _
from iam.resource.utils import FancyDict

from backend.components.mysql_priv_manager.client import DBPrivManagerApi
from backend.core.encrypt.constants import AsymmetricCipherConfigType
from backend.core.encrypt.handlers import AsymmetricHandler
from backend.db_services.dbpermission.constants import AccountType
from backend.db_services.dbpermission.db_account.dataclass import AccountMeta, AccountRuleMeta
from backend.db_services.dbpermission.db_account.signals import create_account_signal
from backend.db_services.mysql.open_area.models import TendbOpenAreaConfig
from backend.db_services.mysql.permission.exceptions import DBPermissionBaseException

logger = logging.getLogger("root")


class AccountHandler(object):
    """
    封装账号相关的处理操作
    """

    def __init__(self, bk_biz_id: int, account_type: AccountType, operator: str = None, context: Dict = None):
        """
        @param bk_biz_id: 业务ID
        @param account_type: 账号类型，目前区分与mysql和tendbcluster
        @param operator: 操作者
        @param context: 上下文数据
        """
        self.bk_biz_id = int(bk_biz_id)
        self.account_type = account_type
        self.operator = operator
        self.context = context

    @staticmethod
    def _decrypt_password(password: str) -> str:
        """
        - 获取saas侧私钥，将password利用私钥解密
        :param password: 待解密密码
        """
        return AsymmetricHandler.decrypt(
            name=AsymmetricCipherConfigType.PASSWORD.value, content=password, salted=False
        )

    def _format_account_rules(self, account_rules_list: Dict) -> Dict:
        """格式化账号权限列表信息"""
        for account_rules in account_rules_list["items"]:
            account_rules["account"]["account_id"] = account_rules["account"].pop("id")

            for rule in account_rules["rules"]:
                rule["rule_id"] = rule.pop("id")
                rule["access_db"] = rule.pop("dbname")
                rule["privilege"] = rule.pop("priv")

        return account_rules_list

    def create_account(self, account: AccountMeta) -> Optional[Any]:
        """
        - 新建一个账号
        @param account: 账号元信息
        """
        resp = DBPrivManagerApi.create_account(
            {
                "cluster_type": self.account_type,
                "bk_biz_id": self.bk_biz_id,
                "operator": self.operator,
                "user": account.user,
                "psw": account.password,
            }
        )
        # 获取新建账号信息 TODO: 这段逻辑在create_account返回账号信息后可以去掉
        account_data = DBPrivManagerApi.get_account(
            params={"bk_biz_id": self.bk_biz_id, "cluster_type": self.account_type, "user_like": account.user}
        )["results"]
        account = {info["user"]: info for info in account_data}.get(account.user)
        account.update(account_type=self.account_type)
        create_account_signal.send(sender=None, account=FancyDict(account))

        return resp

    def delete_account(self, account: AccountMeta) -> Optional[Any]:
        """
        - 删除账号(仅在账号不存在存量规则时)
        @param account: 账号元信息
        """
        resp = DBPrivManagerApi.delete_account(
            {
                "bk_biz_id": self.bk_biz_id,
                "operator": self.operator,
                "cluster_type": self.account_type,
                "id": account.account_id,
            }
        )
        return resp

    def update_password(self, account: AccountMeta) -> Optional[Any]:
        """
        - 修改账号密码
        @param account: 账号元信息
        """
        resp = DBPrivManagerApi.update_password(
            {
                "cluster_type": self.account_type,
                "bk_biz_id": self.bk_biz_id,
                "operator": self.operator,
                "id": account.account_id,
                "psw": account.password,
            }
        )
        return resp

    def add_account_rule(self, account_rule: AccountRuleMeta) -> Optional[Any]:
        """
        - 添加账号规则
        @param account_rule: 账号规则元信息
        """
        resp = DBPrivManagerApi.add_account_rule(
            {
                "bk_biz_id": self.bk_biz_id,
                "creator": self.operator,
                "cluster_type": self.account_type,
                "account_id": account_rule.account_id,
                "priv": account_rule.privilege,
                "dbname": account_rule.access_db,
            }
        )
        return resp

    def query_account_rules(self, account_rule: AccountRuleMeta):
        """查询某个账号下的权限"""

        account_rules_list = DBPrivManagerApi.list_account_rules(
            {"bk_biz_id": self.bk_biz_id, "cluster_type": self.account_type}
        )
        account_rules_list = self._format_account_rules(account_rules_list)

        # 根据账号名和准许db过滤规则
        filter_account_rules_list: List[Dict[str, Any]] = []
        for account_rules in account_rules_list["items"]:
            if account_rule.user != account_rules["account"]["user"]:
                continue

            filter_rules = []
            for rule in account_rules["rules"]:
                if not account_rule.access_dbs or (rule["access_db"] in account_rule.access_dbs):
                    filter_rules.append(rule)

            filter_account_rules_list.append({"account": account_rules["account"], "rules": filter_rules})

        return {"count": len(filter_account_rules_list), "results": filter_account_rules_list}

    def list_account_rules(self, rule_filter: AccountRuleMeta) -> Dict:
        """列举规则清单"""

        # 如果是通过id过滤的，则不管集群类型
        if rule_filter.rule_ids:
            rules_list = DBPrivManagerApi.list_account_rules(
                {"bk_biz_id": self.bk_biz_id, "ids": rule_filter.rule_ids}
            )
        else:
            rules_list = DBPrivManagerApi.list_account_rules(
                {"bk_biz_id": self.bk_biz_id, "cluster_type": self.account_type}
            )

        account_rules_list = self._format_account_rules(rules_list)
        # 不存在过滤条件则直接返回
        if not (rule_filter.user or rule_filter.access_db or rule_filter.privilege):
            return {"count": len(account_rules_list["items"]), "results": account_rules_list["items"]}

        # 根据条件过滤规则
        filter_account_rules_list: List[Dict[str, Any]] = []
        for account_rules in account_rules_list["items"]:
            # 按照账号名称筛选(模糊匹配)
            if rule_filter.user and (rule_filter.user not in account_rules["account"]["user"]):
                continue

            filter_rules = []
            for rule in account_rules["rules"]:
                # 按照访问DB筛选(模糊匹配)
                if rule_filter.access_db and (rule_filter.access_db not in rule["access_db"]):
                    continue

                # 按照访问权限筛选
                if rule_filter.privilege:
                    if not set(rule_filter.privilege.split(",")).issubset(set(rule["privilege"].split(","))):
                        continue

                filter_rules.append(rule)

            # 只添加符合过滤条件的账号
            if filter_rules or not (rule_filter.access_db or rule_filter.privilege):
                filter_account_rules_list.append({"account": account_rules["account"], "rules": filter_rules})

        return {"count": len(filter_account_rules_list), "results": filter_account_rules_list}

    def modify_account_rule(self, account_rule: AccountRuleMeta) -> Optional[Any]:
        """
        - 修改账号规则
        :param account_rule: 账号规则元信息
        """

        resp = DBPrivManagerApi.modify_account_rule(
            {
                "bk_biz_id": self.bk_biz_id,
                "operator": self.operator,
                "cluster_type": self.account_type,
                "id": account_rule.rule_id,
                "account_id": account_rule.account_id,
                "dbname": account_rule.access_db,
                "priv": account_rule.privilege,
            }
        )
        return resp

    def delete_account_rule(self, account_rule: AccountRuleMeta) -> Optional[Any]:
        """
        - 删除账号规则
        :param account_rule: 账号规则元信息
        """
        # 如果账号规则与其他地方耦合，需要进行判断
        config = TendbOpenAreaConfig.objects.filter(related_authorize__contains=[account_rule.rule_id])
        if config.exists():
            raise DBPermissionBaseException(_("当前授权规则已被开区模板{}引用，不允许删除").format(config.first().name))

        resp = DBPrivManagerApi.delete_account_rule(
            {
                "bk_biz_id": self.bk_biz_id,
                "operator": self.operator,
                "cluster_type": self.account_type,
                "id": [account_rule.rule_id],
            }
        )
        return resp

    @classmethod
    def aggregate_user_db_privileges(cls, bk_biz_id: int, account_type: AccountType) -> Dict[str, Dict[str, List]]:
        account_rules = DBPrivManagerApi.list_account_rules({"bk_biz_id": bk_biz_id, "cluster_type": account_type})[
            "items"
        ]
        # 按照user，accessdb进行聚合
        user_db__rules = defaultdict(dict)
        for account_rule in account_rules:
            account, rules = account_rule["account"], account_rule["rules"]
            user_db__rules[account["user"]] = {rule["dbname"]: rule["priv"] for rule in rules}
        return user_db__rules
