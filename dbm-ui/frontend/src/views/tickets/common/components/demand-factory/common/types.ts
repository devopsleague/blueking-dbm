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
import type { SpecInfo } from '@services/model/ticket/details/common';
import type { clustersItems } from '@services/types/ticket';

// MongoDB 副本集群
export interface DetailsMongoDBReplicaSet {
  bk_cloud_name: string;
  cap_spec: string;
  city_code: string;
  city_name: string;
  cluster_alias: string;
  cluster_id: number;
  cluster_name: string;
  cluster_type: string;
  db_app_abbr: string;
  db_version: string;
  disaster_tolerance_level: string;
  ip_source: string;
  node_count: number;
  node_replica_count: number;
  oplog_percent: number;
  proxy_port: number;
  replica_count: number;
  replica_sets: Array<{
    domain: string;
    name: string;
    set_id: string;
  }>;
  resource_spec: {
    mongo_machine_set: SpecInfo;
  };
  start_port: number;
}

// MongoDB 分片集群
export interface DetailsMongoDBSharedCluster {
  bk_cloud_name: string;
  cap_key: string;
  cap_spec: string;
  city_code: string;
  city_name: string;
  cluster_alias: string;
  cluster_id: number;
  cluster_name: string;
  cluster_type: string;
  db_app_abbr: string;
  db_version: string;
  disaster_tolerance_level: string;
  ip_source: string;
  oplog_percent: number;
  proxy_port: number;
  start_port: number;
  resource_spec: {
    mongo_config: SpecInfo;
    mongos: SpecInfo;
    mongodb: SpecInfo;
  };
}

// MongoDB 账号授权
export interface MongoDBAuthorizeRules {
  authorize_data?: {
    auth_db: string;
    cluster_ids: number[];
    password: string;
    rule_sets: {
      db: string;
      privileges: string[];
    }[];
    username: string;
  }[];
  authorize_uid: string;
  excel_url?: string;
}

// Sqlserver 集群部署
export interface DetailsSqlserver {
  bk_cloud_id: number;
  charset: string;
  city_code: string;
  city_name: string;
  cluster_count: number;
  db_module_id: number;
  db_module_name: string;
  db_version: string;
  disaster_tolerance_level: string;
  domains: {
    key: string;
    master: string;
    slave: string;
  }[];
  inst_num: number;
  ip_source: string;
  nodes: {
    backend: {
      ip: string;
      bk_host_id: number;
      bk_cloud_id: number;
      bk_biz_id: number;
    }[];
  };
  resource_spec: {
    backend: SpecInfo;
  };
  spec: string;
  spec_display: string;
  start_mysql_port: number;
  start_mssql_port: number;
}

// Sqlserver 数据库备份
export interface SqlserverDbBackup {
  backup_place: string;
  backup_type: string;
  clusters: Record<number, clustersItems>;
  file_tag: string;
  infos: {
    backup_dbs: string[];
    cluster_id: number;
  }[];
}

// Sqlserver 账号授权
export interface SqlserverAuthorizeRules {
  authorize_data?: {
    user: string;
    target_instances: string[];
    access_dbs: string[];
    cluster_type: string;
  }[];
  authorize_uid: string;
  excel_url?: string;
}

// spider 迁移主从
export interface SpiderMigrateCluster {
  infos: {
    cluster_id: number,
    new_master: {
      bk_biz_id: number,
      bk_cloud_id: number
      bk_host_id: number,
      ip: string,
    },
    new_slave: {
      bk_biz_id: number,
      bk_cloud_id: number
      bk_host_id: number,
      ip: string,
    },
  }[],
  clusters: Record<number, {
    id: number,
    tag: string[],
    name: string,
    alias: string,
    phase: string,
    region: string,
    status: string,
    creator: string,
    updater: string,
    bk_biz_id: number,
    time_zone: string,
    bk_cloud_id: number,
    cluster_type: string,
    db_module_id: number,
    immute_domain: string,
    major_version: string,
    cluster_type_name: string,
    disaster_tolerance_level: string
  }>,
  ip_source: string,
  backup_source: string
}

// spider 迁移主从
export interface SpiderSlaveRebuid {
  infos: {
    cluster_id: number
    slave: {
      ip: string,
      bk_biz_id: number,
      bk_host_id: number,
      bk_cloud_id: number
    }
    old_slave: SpiderSlaveRebuid['infos'][number]['slave'],
    new_slave: SpiderSlaveRebuid['infos'][number]['slave'],
    resource_spec: {
      new_slave: {
        name: string;
        cpu: {
          max: number;
          min: number;
        };
        id: number;
        mem: {
          max: number;
          min: number;
        };
        qps: {
          max: number,
          min: number
        },
        count: number;
        storage_spec: {
          mount_point: string;
          size: number;
          type: string;
        }[];
      }
    }
  }[],
  clusters: Record<number, {
    id: number,
    tag: string[],
    name: string,
    alias: string,
    phase: string,
    region: string,
    status: string,
    creator: string,
    updater: string,
    bk_biz_id: number,
    time_zone: string,
    bk_cloud_id: number,
    cluster_type: string,
    db_module_id: number,
    immute_domain: string,
    major_version: string,
    cluster_type_name: string,
    disaster_tolerance_level: string
  }>,
  ip_source: string,
  backup_source: string
}

export type TicketDetailTypes =
  | DetailsMongoDBReplicaSet
  | DetailsMongoDBSharedCluster
  | MongoDBAuthorizeRules
  | DetailsSqlserver
  | SqlserverDbBackup
  | SqlserverAuthorizeRules
  | SpiderMigrateCluster
