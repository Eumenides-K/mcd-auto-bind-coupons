#!/usr/bin/env python3
"""
解析优惠券领取结果并输出为GitHub Actions可用的格式
"""

import json
import sys
import base64

def main():
    """主函数"""
    try:
        # 读取result.json文件
        with open('result.json', 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        # 输出基本信息
        print(f"success={result.get('success', False)}")
        print(f"has_issue_content={'issue_content' in result}")
        
        # 将完整的JSON结果进行base64编码，避免shell转义问题
        result_json = json.dumps(result, ensure_ascii=False)
        encoded_result = base64.b64encode(result_json.encode('utf-8')).decode('ascii')
        print(f"encoded_result={encoded_result}")
        
        # 如果有issue_content，也进行base64编码
        if 'issue_content' in result:
            issue_content = result['issue_content']
            encoded_issue = base64.b64encode(issue_content.encode('utf-8')).decode('ascii')
            print(f"encoded_issue_content={encoded_issue}")
        
        return 0
        
    except:
        # 输出错误信息
        print("success=False")
        print("has_issue_content=False")
        print("error={str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
