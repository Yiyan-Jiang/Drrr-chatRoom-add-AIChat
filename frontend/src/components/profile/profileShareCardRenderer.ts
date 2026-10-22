/** 使用 Canvas 渲染个人会员分享卡片。 */
import { resolveChatAvatarAssets } from '@/assets/chatAvatarCatalog'
import type { User } from '@/types/user'
import { formatProfileDate } from './profilePageModel'

/** 分享卡片可用的底图角色键。 */
export type ProfileCardTheme =
  'celty' | 'izaya' | 'shizuo' | 'mikado' | 'masaomi' | 'anri'

/** 角色底图对应的名称与装饰色。 */
export const profileCardThemes: Record<
  ProfileCardTheme,
  {
    /** 界面和卡片中的角色名称。 */
    label: string
    /** 卡片左侧强调色。 */
    accent: string
  }
> = {
  celty: { label: '赛尔提', accent: '#f2c400' },
  izaya: { label: '折原临也', accent: '#c51230' },
  shizuo: { label: '平和岛静雄', accent: '#1685cf' },
  mikado: { label: '龙之峰帝人', accent: '#1779b8' },
  masaomi: { label: '纪田正臣', accent: '#e5b52b' },
  anri: { label: '园原杏里', accent: '#b82435' },
}

/** 等待浏览器解码本地图片，避免画布读取尚未完成的资源。
 * @param src - 图片资源地址。
 * @returns 图片加载完成后的元素。
 */
function loadImage(src: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image()
    image.onload = () => resolve(image)
    image.onerror = () => reject(new Error(`无法加载图片：${src}`))
    image.src = src
  })
}

/** 按显式换行和画布宽度计算文字行，保留空行。
 * @param context - 用于测量文字的画布上下文。
 * @param text - 要排版的文字。
 * @param maxWidth - 每行可用的最大宽度。
 * @returns 按顺序排列的实际文字行。
 */
function wrapText(
  context: CanvasRenderingContext2D,
  text: string,
  maxWidth: number,
): string[] {
  const lines: string[] = []
  for (const paragraph of text.split(/\r?\n/)) {
    if (!paragraph) {
      lines.push('')
      continue
    }

    let line = ''
    for (const character of Array.from(paragraph)) {
      const nextLine = line + character
      if (line && context.measureText(nextLine).width > maxWidth) {
        lines.push(line)
        line = character
      } else {
        line = nextLine
      }
    }
    lines.push(line)
  }
  return lines
}

/** 按行绘制文字，空行保留垂直间距。
 * @param context - 用于绘制文字的画布上下文。
 * @param lines - 按顺序排列的文字行。
 * @param x - 文字块左边缘坐标。
 * @param y - 文字块顶部坐标。
 * @param lineHeight - 相邻行之间的垂直距离。
 */
function drawLines(
  context: CanvasRenderingContext2D,
  lines: string[],
  x: number,
  y: number,
  lineHeight: number,
): void {
  lines.forEach((line, index) => {
    if (line) context.fillText(line, x, y + index * lineHeight)
  })
}

/** 在 1536×1024 角色底图上绘制用户资料并返回 PNG 数据 URL。
 * @param user - 当前已保存的用户资料。
 * @param theme - 本次选择的角色底图。
 * @returns 可直接用于预览与下载的 PNG 数据 URL。
 */
export async function renderProfileCard(
  user: User,
  theme: ProfileCardTheme,
): Promise<string> {
  await document.fonts.ready
  const [background, avatar] = await Promise.all([
    loadImage(`/profile-cards/${theme}.png`),
    loadImage(resolveChatAvatarAssets(user.avatar_key).avatar),
  ])
  const canvas = document.createElement('canvas')
  canvas.width = 1536
  canvas.height = 1024
  const context = canvas.getContext('2d')
  if (!context) throw new Error('当前浏览器无法创建画布。')

  context.drawImage(background, 0, 0, canvas.width, canvas.height)

  const accent = profileCardThemes[theme].accent
  const panelX = 44
  const panelWidth = 590
  const panelRight = panelX + panelWidth
  const textX = panelX + 62
  const textWidth = panelWidth - 96
  const titleTop = 28
  const nicknameTop = 74
  const avatarSize = 104
  const avatarX = panelRight - avatarSize - 34
  const nicknameWidth = avatarX - textX - 18

  const username = user.username.replace(/\s+/g, ' ').trim()
  const nickname = user.nickname?.replace(/\s+/g, ' ').trim() || username
  let nicknameFontSize = 56
  let nicknameLineHeight = 0
  let nicknameLines: string[] = []
  while (true) {
    context.font = `700 ${nicknameFontSize}px "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`
    nicknameLineHeight = nicknameFontSize * 1.12
    nicknameLines = wrapText(context, nickname, nicknameWidth)
    if (
      nicknameLines.length * nicknameLineHeight <= avatarSize ||
      nicknameFontSize === 18
    ) {
      break
    }
    nicknameFontSize = Math.max(18, nicknameFontSize - 2)
  }

  const nicknameBottom = nicknameTop + nicknameLines.length * nicknameLineHeight
  const avatarBottom = nicknameTop + avatarSize
  const usernameFontSize = 22
  context.font = `400 ${usernameFontSize}px "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`
  const usernameLines = wrapText(context, `@${username}`, textWidth)
  const usernameLineHeight = usernameFontSize * 1.35
  const usernameTop = Math.max(nicknameBottom + 14, avatarBottom + 12)
  const usernameBottom = usernameTop + usernameLines.length * usernameLineHeight

  const metadataTop = usernameBottom + 20
  const metadataFontSize = 22
  const metadataLineHeight = 32
  const metadataBottom = metadataTop + metadataLineHeight * 2
  const bio = user.bio?.trim() || '尚未填写个人简介'
  const bioTop = metadataBottom + 56
  const maxPanelHeight = 760
  let bioFontSize = 22
  let bioLineHeight = bioFontSize * 1.35
  let bioLines: string[] = []
  while (bioFontSize >= 18) {
    bioLineHeight = bioFontSize * 1.35
    const maxBioLines = Math.floor(
      (maxPanelHeight - bioTop - 24) / bioLineHeight,
    )
    context.font = `400 ${bioFontSize}px "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`
    bioLines = wrapText(context, bio, textWidth)
    if (bioLines.length <= maxBioLines) break

    const compactLines = wrapText(
      context,
      bio.replace(/\r?\n/g, ' '),
      textWidth,
    )
    if (compactLines.length <= maxBioLines) {
      bioLines = compactLines
      break
    }
    bioFontSize -= 1
  }
  const panelHeight = Math.max(
    476,
    Math.ceil(bioTop + bioLines.length * bioLineHeight + 22),
  )
  const panel = { x: panelX, y: canvas.height - panelHeight, width: panelWidth }

  context.fillStyle = '#f1e3c6'
  context.fillRect(panel.x, panel.y, panel.width, panelHeight)
  context.fillStyle = accent
  context.fillRect(panel.x + 28, panel.y + 34, 12, panelHeight - 68)

  context.textBaseline = 'top'
  context.fillStyle = '#171615'
  context.font = '600 22px "Microsoft YaHei", "Noto Sans CJK SC", sans-serif'
  context.fillText('M E M B E R   C A R D', textX, panel.y + titleTop)

  context.font = `700 ${nicknameFontSize}px "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`
  drawLines(
    context,
    nicknameLines,
    textX,
    panel.y + nicknameTop,
    nicknameLineHeight,
  )

  const avatarY = panel.y + nicknameTop
  context.save()
  context.beginPath()
  context.rect(avatarX, avatarY, avatarSize, avatarSize)
  context.clip()
  context.drawImage(avatar, avatarX, avatarY, avatarSize, avatarSize)
  context.restore()
  context.strokeStyle = '#171615'
  context.lineWidth = 3
  context.strokeRect(avatarX, avatarY, avatarSize, avatarSize)

  context.font = `400 ${usernameFontSize}px "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`
  drawLines(
    context,
    usernameLines,
    textX,
    panel.y + usernameTop,
    usernameLineHeight,
  )

  context.strokeStyle = '#6e675b'
  context.lineWidth = 2
  context.beginPath()
  context.moveTo(textX, panel.y + metadataTop - 10)
  context.lineTo(panelRight - 36, panel.y + metadataTop - 10)
  context.stroke()

  context.font = `500 ${metadataFontSize}px "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`
  context.fillText(
    `成员编号  ${String(user.id).padStart(6, '0')}`,
    textX,
    panel.y + metadataTop,
  )
  context.fillText(
    `加入日期  ${formatProfileDate(user.created_at)}`,
    textX,
    panel.y + metadataTop + metadataLineHeight,
  )

  context.beginPath()
  context.moveTo(textX, panel.y + metadataBottom + 14)
  context.lineTo(panelRight - 36, panel.y + metadataBottom + 14)
  context.stroke()

  context.font = `400 ${bioFontSize}px "Microsoft YaHei", "Noto Sans CJK SC", sans-serif`
  drawLines(context, bioLines, textX, panel.y + bioTop, bioLineHeight)

  return canvas.toDataURL('image/png')
}
