/** 维护头像与气泡图片的配对，并解析头像资源。 */
import adminAvatar from './icon/avater/admin/icon_admin.png'
import adminBubble from './icon/avater/admin/orange.png'
import grayAvatar from './icon/avater/gray/icon_gray.png'
import grayBubble from './icon/avater/gray/gray.png'
import kanraAvatar from './icon/avater/kanra/icon_kanra.png'
import kanraBubble from './icon/avater/kanra/kanra.png'
import pinkAvatar from './icon/avater/pink/icon_gg.png'
import pinkBubble from './icon/avater/pink/pink.png'
import settonAvatar from './icon/avater/setton/icon_setton.png'
import settonBubble from './icon/avater/setton/setton.png'
import tanakaAvatar from './icon/avater/tanaka/icon_tanaka.png'
import tanakaBubble from './icon/avater/tanaka/tanaka.png'
import zaikaAvatar from './icon/avater/zaika/icon_zaika.png'
import zaikaBubble from './icon/avater/zaika/zaika.png'
import zawaAvatar from './icon/avater/zawa/icon_zawa.png'
import zawaBubble from './icon/avater/zawa/green.png'
import type { AvatarKey } from '@/types/user'

/** 同一头像主题的头像与聊天气泡图片地址。 */
type ChatAvatarAssets = {
  /** 头像图片地址。 */
  avatar: string
  /** 聊天气泡图片地址。 */
  bubble: string
}

const fallbackKey: AvatarKey = 'kanra'

/** 内置头像主题与图片资源的映射。 */
export const chatAvatarCatalog: Record<AvatarKey, ChatAvatarAssets> = {
  /** admin 主题的头像与气泡图片。 */
  admin: { avatar: adminAvatar, bubble: adminBubble },
  /** gray 主题的头像与气泡图片。 */
  gray: { avatar: grayAvatar, bubble: grayBubble },
  /** kanra 主题的头像与气泡图片。 */
  kanra: { avatar: kanraAvatar, bubble: kanraBubble },
  /** pink 主题的头像与气泡图片。 */
  pink: { avatar: pinkAvatar, bubble: pinkBubble },
  /** setton 主题的头像与气泡图片。 */
  setton: { avatar: settonAvatar, bubble: settonBubble },
  /** tanaka 主题的头像与气泡图片。 */
  tanaka: { avatar: tanakaAvatar, bubble: tanakaBubble },
  /** zaika 主题的头像与气泡图片。 */
  zaika: { avatar: zaikaAvatar, bubble: zaikaBubble },
  /** zawa 主题的头像与气泡图片。 */
  zawa: { avatar: zawaAvatar, bubble: zawaBubble },
}

/**
 * 解析头像主题；键缺失或不在目录时使用默认主题。
 * @param avatarKey - 用户资料中的头像主题键。
 * @returns 同一主题的头像和气泡图片地址。
 */
export function resolveChatAvatarAssets(
  avatarKey?: string | null,
): ChatAvatarAssets {
  if (avatarKey && avatarKey in chatAvatarCatalog) {
    return chatAvatarCatalog[avatarKey as AvatarKey]
  }
  return chatAvatarCatalog[fallbackKey]
}
