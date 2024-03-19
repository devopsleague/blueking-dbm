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


import BizConfTopoTreeModel from '@services/model/config/biz-conf-topo-tree';

import { useGlobalBizs } from '@stores';

import http from '../http';

const { currentBizId } = useGlobalBizs();

/**
 * 获取业务拓扑树
 */
export function geSqlserverResourceTree(params: { cluster_type: string }) {
  // return http.get<BizConfTopoTreeModel[]>('http://127.0.0.1:8083/mock/20/apis/sqlserver/bizs/3/resource_tree/', params);
  return http.get<BizConfTopoTreeModel[]>(`/apis/sqlserver/bizs/${currentBizId}/resource_tree/`, params);
}
