import TimeBaseClassModel from '@services/util/time-base-class';

export default class SqlserverPermission extends TimeBaseClassModel {
  account: {
    account_id:number;
    bk_biz_id:number;
    creator:string;
    create_time:string;
    user:string
  };
  rules: {
    account_id: number;
    access_db: string;
    bk_biz_id: number;
    creator: string;
    create_time: string;
    rule_id: number;
    privilege: string;
  }[];

  constructor(payload: SqlserverPermission) {
    super(payload);
    this.account = payload.account;
    this.rules = payload.rules;
  }
}
