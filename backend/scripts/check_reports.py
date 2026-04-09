#!/usr/bin/env python3
"""
每日漏报巡检脚本
建议通过 crontab 在每日 18:00 执行：
  0 18 * * * /usr/bin/python3 /path/to/backend/scripts/check_reports.py
"""

import sys
import os

# 将 backend 目录加入路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from database import SessionLocal
from services.alert_service import check_unreported_tasks


def main():
    db = SessionLocal()
    try:
        alerts = check_unreported_tasks(db)

        if not alerts:
            print("[巡检通过] 今日所有进行中的节点均已提交进度汇报。")
            return

        print(f"[漏报预警] 共发现 {len(alerts)} 项未汇报的节点：")
        print("-" * 60)
        for alert in alerts:
            print(f"  工单号: {alert['wo_number']}")
            print(f"  项目名: {alert['project_name']}")
            print(f"  节  点: {alert['milestone']}")
            print(f"  详  情: {alert['message']}")
            print("-" * 60)

        # TODO: 对接企业微信/钉钉/邮件推送
        # send_to_wechat(alerts)
        # send_to_dingtalk(alerts)

    finally:
        db.close()


if __name__ == "__main__":
    main()
