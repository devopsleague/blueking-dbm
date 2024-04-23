export default class MongodbInstanceDetail {
  bk_agent_id: string;
  bk_cloud_id: number;
  bk_cloud_name: string;
  bk_cpu: number;
  bk_disk: number;
  bk_host_id: number;
  bk_host_innerip: string;
  bk_idc_id: string;
  bk_idc_name: string;
  bk_mem: number;
  bk_os_name: string;
  cluster_id: number;
  cluster_name: string;
  cluster_type: string;
  create_at: string;
  db_module_id: number;
  db_version: null;
  id: number;
  instance_address: string;
  ip: string;
  machine_type: string;
  master_domain: string;
  port: number;
  role: string;
  shard: string;
  slave_domain: string;
  spec_config: string;
  status: string;
  version: string;

  constructor(payload: MongodbInstanceDetail) {
    this.bk_agent_id = payload.bk_agent_id;
    this.bk_cloud_id = payload.bk_cloud_id;
    this.bk_cloud_name = payload.bk_cloud_name;
    this.bk_cpu = payload.bk_cpu;
    this.bk_disk = payload.bk_disk;
    this.bk_host_id = payload.bk_host_id;
    this.bk_host_innerip = payload.bk_host_innerip;
    this.bk_idc_id = payload.bk_idc_id;
    this.bk_idc_name = payload.bk_idc_name;
    this.bk_mem = payload.bk_mem;
    this.bk_os_name = payload.bk_os_name;
    this.cluster_id = payload.cluster_id;
    this.cluster_name = payload.cluster_name;
    this.cluster_type = payload.cluster_type;
    this.create_at = payload.create_at;
    this.db_module_id = payload.db_module_id;
    this.db_version = payload.db_version;
    this.id = payload.id;
    this.instance_address = payload.instance_address;
    this.ip = payload.ip;
    this.machine_type = payload.machine_type;
    this.master_domain = payload.master_domain;
    this.port = payload.port;
    this.role = payload.role;
    this.shard = payload.shard;
    this.slave_domain = payload.slave_domain;
    this.spec_config = payload.spec_config;
    this.status = payload.status;
    this.version = payload.version;
  }
}