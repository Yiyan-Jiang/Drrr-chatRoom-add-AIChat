/**
 * 展示登录注册页面的品牌 Logo 和横幅。
 */
import logoUrl from '@/assets/icon/Logo/logo.png'
import bannerUrl from '@/assets/icon/Logo/banner-80x15.png'

/** 认证品牌区域的展示配置。 */
interface AuthBrandProps {
  /** 应用到 Logo 图片的尺寸与样式类。 */
  logoSizeClassName: string
  /** 是否展示横幅，默认展示。 */
  showBanner?: boolean
  /** Logo 下方的可选标题。 */
  title?: string
}

/** 展示认证页面的 Logo、可选标题和横幅。 */
export default function AuthBrand({
  logoSizeClassName,
  showBanner = true,
  title,
}: AuthBrandProps) {
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
