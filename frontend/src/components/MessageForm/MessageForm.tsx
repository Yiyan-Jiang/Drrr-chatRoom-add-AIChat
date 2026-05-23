/**
 * @parm 组件用途：展示旧版消息输入表单。
 */
import { useState } from 'react'

export default function MessageForm() {
  const [message, setmessage] = useState('')

  const handleon = () =>{
    setmessage(()=> message + 1)
  }


  return (
    <>
      <div
      className='pt-1'
      onClick={handleon}>
        {message}
      </div>
    </>
  )
}
