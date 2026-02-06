---
name: annotated-message-tool
description: 通过MCP调用生成带注释的消息内容块集合。支持Error/Success/Debug三种消息类型，可选包含图片。必须正确处理GUID缓存机制。
---

# AnnotatedMessageTool 带注释消息技能

## Overview

本技能用于通过MCP协议生成结构化的带注释消息内容块。返回的对象集合会被服务器缓存，必须正确处理GUID引用机制。

## MCP调用规范

### 工具元数据
- **className**: `AnnotatedMessageTool`
- **methodName**: `AnnotatedMessage`
- **returnTypeFullName**: `System.Collections.Generic.IEnumerable<EverythingServer.Tools.ContentBlock>`
- **参数类型**: 
  - `EverythingServer.Tools.AnnotatedMessageTool.MessageType`
  - `bool`
  
### 调用方法
你必须通过YdMcpServer提供的MCP服务中调用call_mcp_tool_func功能来执行此功能，并且传入的类名和方法名称必须与调用规范中的要求保持严格一致，否则你将会得到一个致命的调用错误。

### 参数含义
1. **消息类型**：必须为以下之一
   - `Error` - 错误消息
   - `Success` - 成功消息
   - `Debug` - 调试消息
2. **是否包含图片**：可选，默认值：`true`

## GUID管理规则（重要）

### 必须遵守的规则
1. **返回对象集合会被缓存**：服务器自动为返回的ContentBlock集合生成GUID
2. **大模型只能持有GUID**：不能序列化、反序列化或构造对象结构
3. **只能保存和传递GUID**：后续访问必须通过GUID引用

### 示例流程
```text
调用 -> 返回IEnumerable<ContentBlock> -> 服务器缓存 -> 获得GUID -> 保存GUID
后续调用 -> 传递GUID -> 访问具体内容块
```

## 验证要点
1. 必须真实调用MCP工具
2. 必须正确处理MessageType枚举
3. 必须保存返回的GUID
4. 参数顺序：MessageType, bool
5. 不能自行构造ContentBlock对象

## 后续引用示例
从缓存中获取第一个内容块：
```csharp
// 使用保存的GUID调用GetFirstContentBlock
className: "AnnotatedMessageTool"
methodName: "GetFirstContentBlock"
paramTypeFullNames: ["System.Collections.Generic.IEnumerable<EverythingServer.Tools.ContentBlock>"]
args: [{ "GUID": "保存的GUID字符串" }]
```