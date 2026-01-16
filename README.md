# 麦当劳自动领券

使用GitHub Actions每日自动通过麦当劳MCP领取优惠券，并将结果记录在Issues中。

## 使用方法

### 1. 获取MCP Token

登录[麦当劳MCP平台](https://open.mcd.cn/mcp/login)，获取MCP Token

### 2. 设置环境变量

点击页面右上角的 "Fork" 按钮将此仓库fork到你的GitHub账户，然后在你的fork仓库中作如下设置：

1. 进入仓库的 `Settings` 页面
2. 选择 `Secrets and variables` > `Actions`
3. 点击 `New repository secret`
4. 添加以下Secret：
   - **Name**: `MCD_MCP_TOKEN`
   - **Secret**: 你的MCP Token

### 3. 配置GitHub Actions权限

为了使工作流能够创建和管理Issues，需要配置适当的权限：

1. 进入仓库的 `Settings` 页面
2. 选择 `Actions` > `General`
3. 向下滚动到 `Workflow permissions` 部分
4. 选择 **Read and write permissions**
5. 勾选 **Allow GitHub Actions to create and approve pull requests**
6. 点击 **Save** 保存设置

### 4. 启用GitHub Actions

1. 进入仓库的 `Actions` 页面
2. 点击 "I understand my workflows, go ahead and enable them"

### 5. 手动测试（可选）

你可以手动触发工作流来测试设置：

1. 进入 `Actions` 页面
2. 选择 "自动领取优惠券" 工作流
3. 点击 "Run workflow"

## 工作流说明

### 执行时间

- **每日北京时间上午9:00** (UTC 1:00) 自动执行
- 支持手动触发执行

### 执行流程

1. 检出代码并设置Python环境
2. 安装依赖包
3. 运行优惠券领取脚本
4. 解析执行结果
5. 创建或更新GitHub Issue记录结果

## 本地开发

### 环境要求

- Python 3.8+
- requests库

### 安装依赖

```bash
pip install -r requirements.txt
```

### 本地运行

设置环境变量并运行脚本：

```bash
# Windows
set MCD_MCP_TOKEN=your_token_here
python auto_bind_coupons.py

# Linux/Mac
export MCD_MCP_TOKEN=your_token_here
python auto_bind_coupons.py
```

### 脚本输出

脚本会输出JSON格式的结果，并保存到 `coupon_bind_result.json` 文件中。

## 文件结构

```
.
├── .github/
│   └── workflows/
│       └── auto-bind-coupons.yml  # GitHub Actions工作流配置
├── auto_bind_coupons.py           # 主要的Python脚本
├── requirements.txt               # Python依赖
└── README.md                      # 说明文档
```

## 故障排除

### 常见问题

1. **Token未设置**
   - 确保在GitHub Secrets中正确设置了 `MCD_MCP_TOKEN`

2. **网络连接问题**
   - 检查API服务是否可用
   - 查看GitHub Actions日志中的详细错误信息

3. **权限问题**
   - 确保仓库启用了Actions功能
   - 检查Token是否有足够的权限
   - **Issue创建失败**: 如果看到 "Resource not accessible by integration" 错误：
     - 检查仓库的 `Workflow permissions` 设置是否为 `Read and write permissions`
     - 确认工作流文件中包含以下权限配置：
       ```yaml
       permissions:
         contents: read
         issues: write
       ```

## 许可证

本项目采用MIT许可证。