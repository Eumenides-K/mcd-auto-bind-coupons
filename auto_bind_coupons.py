#!/usr/bin/env python3
"""自动领取优惠券脚本

该脚本通过调用 MCD MCP API 自动领取优惠券，并将结果格式化用于 GitHub Issue 记录。
"""

import json
import os
import sys
import requests

from datetime import datetime
from typing import Any, Dict, Optional

SUCCESS_TEXT = "ℹ️ 优惠券自动领取完成"
FAIL_TEXT = "❌ 优惠券自动领取失败"


class CouponBinder:
    """优惠券领取器，负责与 MCD MCP API 交互。"""

    def __init__(self) -> None:
        """初始化优惠券领取器。"""
        self.api_url = "https://mcp.mcd.cn/mcp-servers/mcd-mcp"
        self.token = os.getenv("MCD_MCP_TOKEN")

        if not self.token:
            raise ValueError("环境变量 MCD_MCP_TOKEN 未设置")

    def bind_coupons(self) -> Dict[str, Any]:
        """发送领取优惠券请求。

        Returns:
            Dict[str, Any]: 包含请求结果、状态码和错误信息的字典。

        Raises:
            requests.exceptions.RequestException: 网络请求失败时抛出。
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

        payload = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "auto-bind-coupons",
            },
        }

        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()

            response_data = response.json()

            # 检查业务逻辑状态
            if self._is_no_coupons_available(response_data):
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response_data,
                    "message": "暂无可领取的优惠券",
                    "timestamp": datetime.now().isoformat(),
                }

            return {
                "success": True,
                "status_code": response.status_code,
                "data": response_data,
                "timestamp": datetime.now().isoformat(),
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _is_no_coupons_available(self, response_data: Dict[str, Any]) -> bool:
        """检查响应是否表示"暂无可领取的优惠券"。

        Args:
            response_data: API 响应数据。

        Returns:
            bool: True 表示无优惠券可领，False 表示有优惠券可领。
        """
        try:
            content = response_data.get("result", {}).get("content", [])
            if content and isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = item.get("text", "")
                        if "暂无可领取的优惠券" in text or "无优惠券可领" in text:
                            return True
            return False
        except Exception:
            return False

    def _parse_coupons_from_response(self, response_data: Dict[str, Any]) -> Optional[str]:
        """从响应数据中解析优惠券信息。

        Args:
            response_data: API 响应数据。

        Returns:
            Optional[str]: 格式化后的优惠券信息，如果没有优惠券则返回 None。
        """
        try:
            content = response_data.get("result", {}).get("content", [])
            if content and isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        text = item.get("text", "")
                        # 检查是否包含优惠券信息（包含"领券结果"）
                        if "领券结果" in text:
                            return text
            return None
        except Exception:
            return None

    def format_result_for_issue(self, result: Dict[str, Any]) -> tuple[str, str]:
        """格式化结果用于 GitHub Issue。

        Args:
            result: API 响应结果。

        Returns:
            tuple[str, str]: 包含 Issue 标题和内容的元组。
        """
        timestamp = result.get("timestamp", "未知时间")

        if result.get("success"):
            data = result.get("data", {})
            status_code = result.get("status_code", "未知")
            message = result.get("message", "")

            # 检查是否为"无优惠券可领"的情况
            if self._is_no_coupons_available(data):
                title = SUCCESS_TEXT
                body = f"""**执行时间**: {timestamp}

暂无可领取的优惠券
"""
                return title, body

            # 尝试解析优惠券信息
            coupons_info = self._parse_coupons_from_response(data)
            if coupons_info:
                title = SUCCESS_TEXT
                body = f"""**执行时间**: {timestamp}

{coupons_info}
"""
                return title, body

            # 无法解析优惠券信息，使用原始数据
            title = SUCCESS_TEXT
            body = f"""**执行时间**: {timestamp}
**HTTP 状态码**: {status_code}
{f'**执行说明**: {message}' if message else ''}

### 响应数据
```json
{json.dumps(data, indent=2, ensure_ascii=False)}
```
"""
            return title, body

        # 失败情况
        error = result.get("error", "未知错误")
        title = FAIL_TEXT
        body = f"""**执行时间**: {timestamp}
**错误信息**: {error}

### 建议检查项目
- [ ] 环境变量 `MCD_MCP_TOKEN` 是否正确设置
- [ ] 网络连接是否正常
- [ ] API 服务是否可用
- [ ] Token 是否已过期
"""
        return title, body


def main() -> None:
    """主函数，执行优惠券领取流程。"""
    try:
        binder = CouponBinder()
        result = binder.bind_coupons()

        # 添加格式化的 Issue 标题和内容到结果中
        title, issue_content = binder.format_result_for_issue(result)
        result["issue_title"] = title
        result["issue_content"] = issue_content

        # 输出结果用于 GitHub Actions - 确保 UTF-8 编码，无 BOM
        output = json.dumps(result, indent=2, ensure_ascii=False)

        # 在 Windows 环境下，确保输出是纯 UTF-8
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="strict")

        print(output)

        # 返回退出码
        exit(0 if result.get("success") else 1)

    except Exception as e:
        error_result = {
            "success": False,
            "error": f"脚本执行错误: {str(e)}",
            "timestamp": datetime.now().isoformat(),
        }

        # 添加格式化的 Issue 标题和内容到错误结果中
        try:
            binder = CouponBinder()
            title, issue_content = binder.format_result_for_issue(error_result)
            error_result["issue_title"] = title
            error_result["issue_content"] = issue_content
        except Exception as format_error:
            # 如果格式化失败，使用简单的错误信息
            error_result["issue_title"] = FAIL_TEXT
            error_result["issue_content"] = f"""**执行时间**: {error_result['timestamp']}
**错误信息**: {error_result['error']}

### 格式化错误
无法生成详细的 Issue 内容: {format_error}

### 建议检查项目
- [ ] 环境变量 `MCD_MCP_TOKEN` 是否正确设置
- [ ] 网络连接是否正常
- [ ] API 服务是否可用
- [ ] Token 是否已过期
"""

        # 确保错误输出也是 UTF-8 编码
        output = json.dumps(error_result, indent=2, ensure_ascii=False)

        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="strict")

        print(output)
        exit(1)


if __name__ == "__main__":
    main()