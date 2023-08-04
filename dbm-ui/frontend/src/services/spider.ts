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

import TendbClusterModel from '@services/model/spider/tendbCluster';
import TendbInstanceModel from '@services/model/spider/tendbInstance';

import { useGlobalBizs } from '@stores';

import http from './http';
import type { ListBase } from './types/common';

const { currentBizId } = useGlobalBizs();

/**
 * 获取 spider 集群列表
 */
export function getSpiderList(params: Record<string, any> = {}) {
  return http.get<{
    count: number,
    results: TendbClusterModel[]
  }>(`/apis/mysql/bizs/${currentBizId}/spider_resources/`, params)
    .then(res => ({
      ...res,
      results: res.results.map(data => new TendbClusterModel(data)),
    }));
}

/**
 * 获取 spider 集群详情
 * @param id 集群 ID
 */
export const getSpiderDetails = (id: number) => http.get<TendbClusterModel>(`/apis/mysql/bizs/${currentBizId}/spider_resources/${id}/`);

/**
 * 获取 spider 实例列表
 */
export function getSpiderInstances(params: Record<string, any>) {
  return http.get<ListBase<TendbInstanceModel[]>>(`/apis/mysql/bizs/${currentBizId}/spider_resources/list_instances/`, params)
    .then(res => ({
      ...res,
      results: res.results.map(data => new TendbInstanceModel(data)),
    }));
}

/**
 * 获取 spider 实例详情
 */
export const getSpiderInstanceDetails = (params: {
  instance_address: string,
  cluster_id: number
}) => http.get<TendbInstanceModel>(`/apis/mysql/bizs/${currentBizId}/spider_resources/retrieve_instance/`, params);
