/*
 * TencentBlueKing is pleased to support the open source community by making 蓝鲸智云-DB管理系统(BlueKing-BK-DBM) available.
 *
 * Copyright (C) 2017-2023 THL A29 Limited, a Tencent company. All rights reserved.
 *
 * Licensed under the MIT License (the "License"); you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at https://opensource.org/licenses/MIT
 *
 * Unless required by applicable law or agreed to in writing, software distributed under the License is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for
 * the specific language governing permissions and limitations under the License.
 */
import type { InstanceSpecInfo } from '@services/model/spider/tendbCluster';

import { utcDisplayTime } from '@utils';

export default class TendbInstance {
  bk_cloud_id: number;
  bk_cloud_name: string;
  bk_host_id: number;
  cluster_id: number;
  cluster_type: string;
  cluster_name: string;
  create_at: string;
  db_module_id: number;
  id: number;
  instance_address: string;
  ip: string;
  machine_type: string;
  master_domain: string;
  permission: {
    tendbcluster_view: boolean;
  };
  port: number;
  role: string;
  status: 'running' | 'unavailable';
  slave_domain: string;
  spec_config: InstanceSpecInfo;
  version: string;
  bk_cpu: number;
  bk_disk: number;
  bk_host_innerip: string;
  bk_mem: number;
  bk_os_name: string;
  bk_idc_name: string;
  bk_idc_id: string;
  db_version: string;

  constructor(payload = {} as TendbInstance) {
    this.bk_cloud_id = payload.bk_cloud_id;
    this.bk_cloud_name = payload.bk_cloud_name;
    this.bk_host_id = payload.bk_host_id;
    this.cluster_id = payload.cluster_id;
    this.cluster_name = payload.cluster_name;
    this.cluster_type = payload.cluster_type;
    this.create_at = payload.create_at;
    this.db_module_id = payload.db_module_id;
    this.id = payload.id;
    this.instance_address = payload.instance_address;
    this.ip = payload.ip;
    this.machine_type = payload.machine_type;
    this.master_domain = payload.master_domain;
    this.permission = payload.permission;
    this.port = payload.port;
    this.role = payload.role;
    this.slave_domain = payload.slave_domain;
    this.spec_config = payload.spec_config;
    this.status = payload.status;
    this.version = payload.version;
    this.bk_cpu = payload.bk_cpu ?? 0;
    this.bk_disk = payload.bk_disk ?? 0;
    this.bk_host_innerip = payload.bk_host_innerip ?? '';
    this.bk_mem = payload.bk_mem ?? 0;
    this.bk_os_name = payload.bk_os_name ?? '';
    this.bk_idc_id = payload.bk_idc_id ?? '';
    this.bk_idc_name = payload.bk_idc_name ?? '';
    this.db_version = payload.db_version ?? '';
  }

  get createAtDisplay() {
    return utcDisplayTime(this.create_at);
  }
}
