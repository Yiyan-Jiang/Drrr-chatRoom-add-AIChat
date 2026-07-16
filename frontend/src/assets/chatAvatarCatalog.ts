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

type ChatAvatarAssets = {
  avatar: string
  bubble: string
}

const fallbackKey: AvatarKey = 'kanra'

export const chatAvatarCatalog: Record<AvatarKey, ChatAvatarAssets> = {
  admin: { avatar: adminAvatar, bubble: adminBubble },
  gray: { avatar: grayAvatar, bubble: grayBubble },
  kanra: { avatar: kanraAvatar, bubble: kanraBubble },
  pink: { avatar: pinkAvatar, bubble: pinkBubble },
  setton: { avatar: settonAvatar, bubble: settonBubble },
  tanaka: { avatar: tanakaAvatar, bubble: tanakaBubble },
  zaika: { avatar: zaikaAvatar, bubble: zaikaBubble },
  zawa: { avatar: zawaAvatar, bubble: zawaBubble },
}

export function resolveChatAvatarAssets(avatarKey?: string | null): ChatAvatarAssets {
  if (avatarKey && avatarKey in chatAvatarCatalog) {
    return chatAvatarCatalog[avatarKey as AvatarKey]
  }
  return chatAvatarCatalog[fallbackKey]
}
