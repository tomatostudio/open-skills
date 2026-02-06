---
name: add-tool-add
description: 通过MCP调用执行整数加法操作。使用AddTool.Add方法计算两个整数的和并返回描述性的字符串结果。主要用于需要执行精确整数加法的场景。
---

# AddTool.Add 加法技能

## Overview

本技能专门用于通过MCP协议调用AddTool.Add工具，精确计算两个整数的和。作为MCP多工具真实调用执行器的一部分，必须遵守严格调用顺序和参数规范。

## MCP调用规范

### 工具元数据
- **className**: `AddTool`
- **methodName**: `Add`
- **returnTypeFullName**: `string`
- **参数类型**: `int`, `int`

### 调用方法
你必须通过YdMcpServer提供的MCP服务中调用call_mcp_tool_func功能来执行此功能，并且传入的类名和方法名称必须与调用规范中的要求保持严格一致，否则你将会得到一个致命的调用错误。

### 参数含义
1. 第一个int参数：加数
2. 第二个int参数：另一个加数

### 调用要求
- **必须真实调用**：不能模拟或计算
- **参数必须匹配**：顺序、数量、类型必须完全匹配
- **返回值**：返回带描述信息的字符串结果，例如 "1 + 2 = 3"
- **没有对象缓存**：不涉及GUID管理

### 使用场景
1. 计算数学运算的中间结果
2. 验证MCP工具调用流程
3. 测试参数传递和类型匹配
4. 演示基本MCP工具调用

### 示例调用
```csharp
// MCP调用示例
className: "AddTool"
methodName: "Add"
paramTypeFullNames: ["int", "int"]
args: [5, 3]
// 预期返回: "5 + 3 = 8"
