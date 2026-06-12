---
date: 2026-04-9
title: AI agent的一些随笔
category: 学习记录
tags: test, AI
---

# AI agent

记录自己在AI agent的一些学习吧

<!-- more -->
## 什么是AI agent

ai agent应该和LLM区别分开来，ai agent更趋向于链接用户与LLM的一个中间件，拥有一些system prompt和工具以及skill，在用户提交prompt后加上system prompt提交给LLM来处理指令，LLM会返回一些输出内容和调用工具的指令，ai agent予与执行，ai agent可以分解任务、调用工具、处理异常、迭代优化，直到完成。而LLM（大语言模型）是一个被动响应的文本预测器，其本身不具备获取上下文的能力，所以需要ai agent把上下文context，用户输入prompt，system prompt提供给LLM进行处理思考，自然就引出来几个问题：
* 如何处理context压缩
* 如何确保prompt的高效
* 如何确保本地不会因为LLM的指令而产生安全问题（即如何限权进行边界控制）
* 如何保证LLM的结构化输出而不是自由生成文本
* agent的多层架构设计
* 成本与延迟的权衡
* 如何可视化ai agent的工作，确保其确实在工作而不是看起来像那麽回事，即如何评测ai agent的工作
* 如何划分人工和ai agent的事务
  
## AI agent的核心概念

AI Agent 是形如 Perception → Reasoning & Planning → Action → Memory → Self-reflection 的基于ReAct范式的闭环

* Perception 感知
  ai agent在这一步会进行初步的observation，获取用户的输入，当前环境的状态使用Tool Calling来获取外部信息，读取文件的代码以及拉取网页代码,读取邮件的操作,看图等操作，低质量 Agent 经常在这里感知不完整或信息过载。
* Reasoning & Planning（推理与规划）
  这一步ai agent会对prompt进行装配，将 当前状态+工具描述，memory结果，system prompt精炼(一般会通过RAG)给与LLM，这一步会多步对话，而不是只让LLM一次输出，如何agent将LLM的命令进行规划拆分成多份可执行的子任务，LLM在规划中也会出现规划幻觉以及不可执行的情况。
* Action（行动）
  这一步ai agent继续Calling Tool开始逐步执行上一步规划的步骤行动这步就会出现工具倾向的选择问题以及如何处理行动的边界，涉及一些安全性隐私性数据是否需要人工介入
* Memory（记忆）
  将本次的行动写入向量数据库以及存储用户偏好作为长期记忆，这步也是LLM模型差距的体现，部分模型可能不会返回给ai agent需要存储的长期记忆。同时本次对话的context也将作为短期记忆，因为ai agent本地的设置context是有限制大小的，所以短期记忆的压缩可能会把本应作为长期记忆的关键点给丢失，而显现出部分低模型的缺点。所以agent在这一步应该主动提取重要的事务进行存储
* Self-reflection（自我反思）
  ai agent会进行自我反思来提高自身的容错，每一步执行后都让LLM来评估这一步是否有效以及如何调整计划，进行不断的重试。（这里应该对迭代的次数进行限制来避免死循环）低模型的LLM在这步的反思也会经常出现浅思考。不同的框架在这步的反思过程也会有所差别，可以是将执行的错误生成一份总结存入system prompt，或是使用比执行模型更强的LLM作为评判者

真正的agent在执行的过程，常常出现非线性的操作，存在任意环节的跳转。

现在也更加倾向与多角色的Multi-Agent Collaboration，通过角色扮演对话明确不同agent的职责和沟通协议，让它们在一个结构化中协同完成任务，或是组织化工作流，构建出一个分工明确的虚拟团队来互相协作，产生高质量的复杂成果。

### system prompt
system prompt主要定义了以下内容：
* 角色定义
* 用户使用偏好
* 长期记忆
* 工具/资源调用（toll，skills，）
* 边界
* 反思与纠错机制





---

## 学习的一些文献


