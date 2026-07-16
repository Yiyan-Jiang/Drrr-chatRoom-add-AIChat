/**
 * AI 聊天类型：服务 AI 角色选择、AI 聊天页面和 AI 请求/响应协议。
 */
export type AICharacter = 'sakura' | 'rin' | 'mio' | 'yang'

export interface AIChatRequest {
  message: string
  character?: AICharacter
}

export interface AIChatResponse {
  content: string
}
