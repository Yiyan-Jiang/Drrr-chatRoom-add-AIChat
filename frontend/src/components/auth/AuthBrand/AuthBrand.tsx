/**
 * @parm 组件用途：展示登录注册页面的品牌 Logo 和横幅。
 */
import logoUrl from '@/assets/icon/Logo/logo.png'
import bannerUrl from '@/assets/icon/Logo/banner-80x15.png'

interface AuthBrandProps {
  logoSizeClassName: string
  showBanner?: boolean
  title?: string
}

export default function AuthBrand({ logoSizeClassName, showBanner = true, title }: AuthBrandProps) {
  return (
    <div className="text-center">
      <img src={logoUrl} alt="Logo" className={logoSizeClassName} />
      {title ? <div className="mt-2 font-bold text-white">{title}</div> : null}
      {showBanner ? (
        <div className="mt-5">
          <img src={bannerUrl} alt="smallLogo" />
        </div>
      ) : null}
    </div>
  )
}
