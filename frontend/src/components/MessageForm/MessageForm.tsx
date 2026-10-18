/**
 * 本地字符串点击追加示例。
 */
import { useState } from 'react'

/** 展示本地字符串，点击后在末尾追加字符 1。 */
export default function MessageForm() {
  const [message, setmessage] = useState('')

  const handleon = () => {
    setmessage(() => message + 1)
  }

  return (
    <>
      <div className="pt-1" onClick={handleon}>
        {message}
      </div>
    </>
  )
}
