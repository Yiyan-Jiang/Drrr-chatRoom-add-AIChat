/** 共享代码高亮容器与行标记的 CSS 选择器。 */
/** 用于匹配代码行、突出行和突出字符的高亮节点选择器。 */
export const prettyCodeSelectors = {
  /** 所有代码行节点的选择器。 */
  line: '[data-line]',
  /** 需要突出显示的代码行选择器。 */
  highlightedLine: '[data-highlighted-line]',
  /** 需要突出显示的字符片段选择器。 */
  highlightedChars: '[data-highlighted-chars]',
} as const
