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
import json

from django.utils.translation import ugettext_lazy as _
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from backend.bk_web import viewsets
from backend.bk_web.swagger import common_swagger_auto_schema
from backend.db_services.meta_import.constants import SWAGGER_TAG
from backend.db_services.meta_import.serializers import MySQLHaMetadataImportSerializer
from backend.iam_app.handlers.drf_perm import RejectPermission
from backend.ticket.constants import TicketType
from backend.ticket.models import Ticket


class DBMetadataImportViewSet(viewsets.SystemViewSet):

    pagination_class = None

    def _get_custom_permissions(self):
        if not self.request.user.is_superuser:
            return [RejectPermission()]
        return []

    @common_swagger_auto_schema(
        operation_summary=_("tendbha元数据导入"),
        tags=[SWAGGER_TAG],
    )
    @action(
        methods=["POST"],
        detail=False,
        serializer_class=MySQLHaMetadataImportSerializer,
        parser_classes=[MultiPartParser],
    )
    def tendbha_metadata_import(self, request, *args, **kwargs):
        data = self.params_validate(self.get_serializer_class())
        # 解析json文件
        data["json_content"] = json.loads(data.pop("file").read().decode("utf-8"))
        # 自动创建ticket
        Ticket.create_ticket(
            ticket_type=TicketType.MYSQL_HA_METADATA_IMPORT,
            creator=request.user.username,
            bk_biz_id=data["bk_biz_id"],
            remark=self.tendbha_metadata_import.__name__,
            details=data,
        )
        return Response(data)