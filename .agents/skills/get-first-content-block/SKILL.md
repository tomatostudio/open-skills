---
name: get-first-content-block
description: 通过MCP调用从缓存的ContentBlock集合中提取第一个内容块。必须正确处理对象GUID传递，不能传递对象本身。这是GUID管理的典型案例。
---

# GetFirstContentBlock 技能

## Overview

专门用于从已通过MCP调用生成的ContentBlock集合中提取第一个内容块。此技能演示了MCP系统中的对象缓存和GUID引用机制，是GUID驱动调用模式的典型示例。

## MCP调用规范

### 工具元数据
- **className**: `AnnotatedMessageTool`
- **methodName**: `GetFirstContentBlock`
- **returnTypeFullName**: `EverythingServer.Tools.ContentBlock`
- **参数类型**: `System.Collections.Generic.IEnumerable<EverythingServer.Tools.ContentBlock>`

## 核心原理

### GUID驱动调用（违反即失败）
```csharp
// ? 错误示例 - 传递对象结构
args: [{ "type": "text", "content": "test" }]

// ? 正确示例 - 传递GUID对象
args: [{ "GUID": "cached-guid-string" }]
```

### 调用前提条件
1. 必须已有缓存的ContentBlock集合（来自AnnotatedMessage调用）
2. 必须持有该集合的GUID字符串
3. 不能序列化或构造ContentBlock对象

## 使用流程

### 步骤1：生成内容块集合
```csharp
// 先生成内容块
className: "AnnotatedMessageTool"
methodName: "AnnotatedMessage"
args: ["Success", true]
// 服务器返回GUID，必须保存：{ "GUID": "abc123" }
```

### 步骤2：提取第一个内容块
```csharp
// 使用保存的GUID调用
className: "AnnotatedMessageTool"
methodName: "GetFirstContentBlock"
paramTypeFullNames: ["System.Collections.Generic.IEnumerable<EverythingServer.Tools.ContentBlock>"]
args: [{ "GUID": "abc123" }]
// 返回单个ContentBlock，也会生成新GUID
```

## GUID管理规则

### 大模型必须
1. ? 保存返回的GUID
2. ? 在后续调用中传递GUID
3. ? 使用正确的对象格式传递GUID

### 大模型禁止
1. ? 序列化对象结构
2. ? 反序列化对象内容
3. ? 构造或修改对象
4. ? 传递对象本身而非GUID

## 验证要点

### 断点验证
1. 必须进入CallMcpToolFunc方法
2. className："AnnotatedMessageTool"完全正确
3. methodName："GetFirstContentBlock"完全正确
4. 参数必须是对象格式包含GUID属性

### 参数验证
```json
// 正确参数结构
{
  "GUID": "保存的缓存GUID"
}

// 错误参数结构
{
  "blocks": [{"type": "text", "content": "test"}]  // ? 传递对象内容
}
```

## 错误场景

### 常见错误
1. **GUID不存在**：传递未缓存的GUID
2. **参数格式错误**：直接传递字符串而非对象
3. **类型不匹配**：参数类型声明错误
4. **忘记保存GUID**：调用AnnotatedMessage后未保存返回的GUID

### 解决方法
1. 确保AnnotatedMessage调用成功并保存GUID
2. 使用正确的对象格式传递参数
3. 检查paramTypeFullNames是否正确

## 集成示例

### 完整工作流
```text
1. 调用AnnotatedMessage(Success, true)
   → 获得GUID: "123"
   → 保存GUID: savedGuid = "123"

2. 调用GetFirstContentBlock({ "GUID": savedGuid })
   → 获得ContentBlock对象
   → 获得新GUID: "456"
   → 保存新GUID供后续使用
```

### 实际应用
作为复杂MCP工作流的中间步骤，用于从生成的消息集合中提取特定内容块进行进一步处理。
