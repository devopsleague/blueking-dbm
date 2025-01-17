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
from typing import Any, Dict, List

from django.utils.translation import ugettext as _
from django_celery_beat.schedulers import ModelEntry

from backend.components import DBPrivManagerApi
from backend.configuration.constants import (
    DB_ADMIN_USER_MAP,
    DBM_PASSWORD_SECURITY_NAME,
    MYSQL_ADMIN_USER,
    AdminPasswordRole,
    DBType,
)
from backend.configuration.exceptions import PasswordPolicyBaseException
from backend.core.encrypt.constants import AsymmetricCipherConfigType
from backend.core.encrypt.handlers import AsymmetricHandler
from backend.db_meta.enums import ClusterType, InstanceInnerRole, InstanceRole, TenDBClusterSpiderRole
from backend.db_periodic_task.models import DBPeriodicTask
from backend.db_services.ipchooser.query.resource import ResourceQueryHelper
from backend.utils.string import base64_decode, base64_encode

logger = logging.getLogger("root")


class DBPasswordHandler(object):
    """密码策略相关处理"""

    @classmethod
    def verify_password_strength(cls, password: str, echo: bool = False):
        """
        校验密码强度
        @param password: 密码(这里是不加盐的)
        @param echo: 是否回显解密密码
        """
        try:
            plain_password = AsymmetricHandler.decrypt(
                name=AsymmetricCipherConfigType.PASSWORD.value, content=password, salted=False
            )
        except Exception as err:
            logger.warning("decrypt password error: {}, maybe it is plain".format(err))
            plain_password = password
        # 密码需要用base64加密后传输
        b64_plain_password = base64_encode(plain_password)
        check_result = DBPrivManagerApi.check_password(
            {"password": b64_plain_password, "security_rule_name": DBM_PASSWORD_SECURITY_NAME}
        )
        if echo:
            check_result.update(password=plain_password)

        return check_result

    @classmethod
    def query_mysql_admin_password(
        cls, limit: int, offset: int, instances: List[str] = None, begin_time: str = None, end_time: str = None
    ):
        """
        获取mysql的admin密码
        @param limit: 分页限制
        @param offset: 分页起始
        @param instances: 实例列表
        @param begin_time: 过滤开始时间
        @param end_time: 过滤结束时间
        """
        instances = instances or []
        # 获取过滤条件
        instance_list = []
        try:
            for address in instances:
                bk_cloud_id, ip, port = address.split(":")
                instance_list.append({"ip": ip, "port": int(port), "bk_cloud_id": int(bk_cloud_id)})
        except (IndexError, ValueError):
            raise PasswordPolicyBaseException(_("请保证查询的实例输入格式合法，格式为[云区域:IP:PORT]"))

        filters = {"limit": limit, "offset": offset, "component": DBType.MySQL.value, "username": MYSQL_ADMIN_USER}
        if instance_list:
            filters.update(instances=instance_list)
        if begin_time:
            filters.update(begin_time=begin_time)
        if end_time:
            filters.update(end_time=end_time)

        # 获取密码生效实例结果
        mysql_admin_password_data = DBPrivManagerApi.get_mysql_admin_password(params=filters)
        mysql_admin_password_data["results"] = mysql_admin_password_data.pop("items")
        cloud_info = ResourceQueryHelper.search_cc_cloud(get_cache=True)
        for data in mysql_admin_password_data["results"]:
            data["password"] = base64_decode(data["password"])
            data["bk_cloud_name"] = cloud_info[str(data["bk_cloud_id"])]["bk_cloud_name"]

        return mysql_admin_password_data

    @classmethod
    def modify_admin_password(cls, operator: str, password: str, lock_hour: int, instance_list: List[Dict]):
        """
        修改db的admin密码
        @param operator: 操作人
        @param password: 修改密码
        @param lock_until: 到期时间
        @param instance_list: 修改的实例列表
        """

        # 根据cluster_type, bk_cloud_id, role将实例分类后聚合
        aggregate_instance: Dict[str, Dict[str, Dict[str, List]]] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(list))
        )
        cluster_infos: List[Dict[str, Any]] = []
        for instance in instance_list:
            role = cls._get_password_role(instance["cluster_type"], instance["role"])
            aggregate_instance[instance["bk_cloud_id"]][instance["cluster_type"]][role].append(
                {"ip": instance["ip"], "port": int(instance["port"])}
            )
        for bk_cloud_id, clusters in aggregate_instance.items():
            for cluster_type, role_instances in clusters.items():
                instances_info = [{"role": role, "addresses": insts} for role, insts in role_instances.items()]
                cluster_infos.append(
                    {"bk_cloud_id": bk_cloud_id, "cluster_type": cluster_type, "instances": instances_info}
                )

        # 根据cluster info获取DB类型，这里保证修改的实例属于同一组件
        db_type = set([ClusterType.cluster_type_to_db_type(cluster["cluster_type"]) for cluster in cluster_infos])
        if len(db_type) > 1:
            raise PasswordPolicyBaseException(_("请保证修改密码的实例属于同一DB组件"))

        # 填充参数，修改admin的密码
        db_type = db_type.pop()
        modify_password_params = {
            # username固定是ADMIN，与DBM_MYSQL_ADMIN_USER保持一致
            "username": DB_ADMIN_USER_MAP[db_type],
            "component": db_type,
            "password": base64_encode(password),
            "lock_hour": lock_hour,
            "operator": operator,
            "clusters": cluster_infos,
            "security_rule_name": DBM_PASSWORD_SECURITY_NAME,
            "async": False,
        }
        data = DBPrivManagerApi.modify_admin_password(params=modify_password_params, raw=True)["data"]
        return data

    @classmethod
    def _get_password_role(cls, cluster_type, role):
        """获取实例对应的密码角色"""
        # 映射tendbcluster的角色
        if cluster_type == ClusterType.TenDBCluster:
            if role == "spider_ctl":
                return AdminPasswordRole.TDBCTL.value
            if role in TenDBClusterSpiderRole.get_values():
                return AdminPasswordRole.SPIDER.value
            if role in [
                InstanceRole.REMOTE_MASTER.value,
                InstanceRole.REMOTE_SLAVE.value,
                InstanceRole.REMOTE_REPEATER.value,
            ]:
                return AdminPasswordRole.STORAGE.value

        # 映射后端角色
        if role in [
            InstanceInnerRole.MASTER.value,
            InstanceInnerRole.SLAVE.value,
            InstanceInnerRole.REPEATER.value,
            InstanceInnerRole.ORPHAN.value,
            InstanceRole.BACKEND_REPEATER,
            InstanceRole.BACKEND_MASTER,
            InstanceRole.BACKEND_SLAVE,
            InstanceRole.ORPHAN,
        ]:
            return AdminPasswordRole.STORAGE.value

        raise PasswordPolicyBaseException(_("{}-{}不存在相应的password角色").format(cluster_type, role))

    @classmethod
    def modify_periodic_task_run_every(cls, run_every, func_name):
        """修改定时任务的运行周期"""
        model_schedule, model_field = ModelEntry.to_model_schedule(run_every)
        db_task = DBPeriodicTask.objects.get(name__contains=func_name)
        celery_task = db_task.task
        setattr(celery_task, model_field, model_schedule)
        celery_task.save(update_fields=[model_field])

    @classmethod
    def query_proxy_password(cls):
        """查询proxy password，用于渲染drs和dbha配置中的proxy password"""
        # 查询参数固定
        params = {
            "instances": [{"ip": "0.0.0.0", "port": 0, "bk_cloud_id": 0}],
            "users": [{"username": "proxy", "component": "proxy"}],
        }
        data = DBPrivManagerApi.get_password(params)["items"][0]
        # 注意要用base64解密
        return base64_decode(data["password"])
