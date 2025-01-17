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
import itertools
import logging
from typing import List

from django.utils.translation import ugettext as _

from backend.db_meta.models import ExtraProcessInstance
from backend.iam_app.dataclass.actions import ActionEnum
from backend.iam_app.dataclass.resources import ResourceEnum
from backend.iam_app.exceptions import ActionNotExistError
from backend.iam_app.handlers.drf_perm.base import (
    IAMPermission,
    MoreResourceActionPermission,
    ResourceActionPermission,
)
from backend.ticket.builders import BuilderFactory
from backend.ticket.builders.common.base import fetch_cluster_ids
from backend.ticket.constants import TicketType
from backend.utils.basic import get_target_items_from_details

logger = logging.getLogger("root")


class CreateTicketOneResourcePermission(ResourceActionPermission):
    """
    创建单据相关动作鉴权 -- 关联一个动作
    """

    def __init__(self, ticket_type: TicketType) -> None:
        self.ticket_type = ticket_type
        action = BuilderFactory.ticket_type__iam_action.get(ticket_type)
        actions = [action] if action else []
        # 只考虑关联一种资源
        resource_meta = action.related_resource_types[0] if action else None

        if resource_meta == ResourceEnum.INFLUXDB:
            # 对于influxdb没有集群概念，特殊考虑
            instance_ids_getter = self.instance_influxdb_ids_getter
        elif resource_meta == ResourceEnum.BUSINESS:
            instance_ids_getter = self.instance_biz_ids_getter
        elif action in ActionEnum.get_match_actions("tbinlogdumper"):
            # 对应dumper相关操作，需要根据dumper的实例ID反查出相关的集群
            instance_ids_getter = self.instance_dumper_cluster_ids_getter
        else:
            instance_ids_getter = self.instance_cluster_ids_getter

        super().__init__(actions, resource_meta, instance_ids_getter=instance_ids_getter)

    @staticmethod
    def instance_biz_ids_getter(request, view):
        return [request.data["bk_biz_id"]]

    @staticmethod
    def instance_cluster_ids_getter(request, view):
        # 集群ID从details解析，如果没有detail(比如sql模拟执行)，则直接取request.data
        details = request.data.get("details") or request.data
        cluster_ids = fetch_cluster_ids(details)
        # 排除非int型的cluster id(比如redis的构造实例恢复集群使用ip表示的)
        cluster_ids = [int(id) for id in cluster_ids if isinstance(id, int) or (isinstance(id, str) and id.isdigit())]
        return cluster_ids

    @staticmethod
    def instance_influxdb_ids_getter(request, view):
        details = request.data.get("details") or request.data
        return get_target_items_from_details(details, match_keys=["instance_id", "instance_ids"])

    @staticmethod
    def instance_dumper_cluster_ids_getter(request, view):
        details = request.data.get("details") or request.data
        # 如果是dumper部署，则从detail获取集群ID，否则从ExtraProcessInstance根据dumper获取集群ID
        if request.data["ticket_type"] == TicketType.TBINLOGDUMPER_INSTALL:
            cluster_ids = fetch_cluster_ids(details)
        else:
            dumper_instance_ids = details.get("dumper_instance_ids", [])
            cluster_ids = list(
                ExtraProcessInstance.objects.filter(id__in=dumper_instance_ids).values_list("cluster_id", flat=True)
            )
        return cluster_ids


class CreateTicketMoreResourcePermission(MoreResourceActionPermission):
    """
    创建单据相关动作鉴权 -- 关联多个动作
    由于这种相关的单据类型很少，且资源独立，所以请根据单据类型来分别写instance_ids_getter函数
    """

    def __init__(self, ticket_type: TicketType) -> None:
        self.ticket_type = ticket_type
        action = BuilderFactory.ticket_type__iam_action.get(ticket_type)
        resource_metes = action.related_resource_types
        # 根据单据类型来决定资源获取方式
        instance_ids_getters = None

        # 授权 - 关联：账号 + 集群
        if ticket_type in [
            TicketType.MYSQL_AUTHORIZE_RULES,
            TicketType.TENDBCLUSTER_AUTHORIZE_RULES,
            TicketType.SQLSERVER_AUTHORIZE_RULES,
            TicketType.MONGODB_AUTHORIZE_RULES,
        ]:
            instance_ids_getters = self.authorize_instance_ids_getters
        # 授权 - 关联：开区模板 + 集群
        elif ticket_type in [TicketType.MYSQL_OPEN_AREA, TicketType.TENDBCLUSTER_OPEN_AREA]:
            instance_ids_getters = self.openarea_instance_ids_getters

        super().__init__(actions=[action], resource_metes=resource_metes, instance_ids_getters=instance_ids_getters)

    @staticmethod
    def authorize_instance_ids_getters(request, view):
        authorize_resource_tuples = []
        if "authorize_data" in request.data["details"]:
            authorize_data_list = [request.data["details"]["authorize_data"]]
        else:
            authorize_data_list = request.data["details"]["authorize_data_list"]
        for data in authorize_data_list:
            authorize_resource_tuples.extend(list(itertools.product([data["account_id"]], data["cluster_ids"])))
        return authorize_resource_tuples

    @staticmethod
    def openarea_instance_ids_getters(request, view):
        details = request.data["details"]
        return [(details["config_id"], details["cluster_id"])]


def create_ticket_permission(ticket_type: TicketType) -> List[IAMPermission]:
    action = BuilderFactory.ticket_type__iam_action.get(ticket_type)
    if not action:
        raise ActionNotExistError(_("单据动作ID:{} 不存在").format(action))
    if len(action.related_resource_types) <= 1:
        return [CreateTicketOneResourcePermission(ticket_type=ticket_type)]
    else:
        return [CreateTicketMoreResourcePermission(ticket_type=ticket_type)]
