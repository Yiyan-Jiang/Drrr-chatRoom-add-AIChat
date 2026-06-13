---
date: 2026-03-27
title: react学习
category: 学习
tags: test, skills
---

# React 学习

react 学习记录

<!-- more -->

## 虚拟DOM

React有两种虚拟DOM的创建方式，**一种是js，另外一种是jsx的方式。**
* **jsx的方式**(推荐)
  ```jsx
  // <div id="test"><\div> 
  const VEM = (<h1>Hello React </h1>) 
  ReactDOM.render(VEM,document.getElementById("test"))
  ```
* ~~js的方式~~
  ```js
  // <div id="test"><\div>
  const VEM = React.creatElement("h1",{id:test},"Hello React")
  ReactDOM.render(VEM,document.getElementById("test"))
  ```
**显然在多重嵌套的情况下jsx会更好**，虚拟DOM比真实的DOM更加*轻量*

---

## jsx的语法
1. 定义虚拟DOM，不需要加引号
2. 标签中可以混入JS表达式，使用{}存储
3. 样式类名使用 `className` , 内联样式使用jsx插槽且需插入对象
4. jsx只允许拥有唯一根标签
5. 小写字母开头转化为html，大写字母转化为组件

```jsx
  // .add{ background-color:"red"; }
  //  ...

  const myID = 'iD'
  const mytext = 'tExT'
  const VEM = (
    <div>
      <h2>
        <span className="add" style={{color:red}} id="{myID.toLowerCase()}">
          {mytext.toLowerCase()}
        </span>
      </h2>
      <input/> // 只允许有唯一根组件
    </div>
  )

  ReactDOM.render(VEM,document.getElementById("test"))
```

* **遍历的时候需要有唯一`key`**
```jsx
  const data = ['nihao','zaijia','aduiduidi']
  const VEM = (
    <div>
      <ul>
        {
          data.map((item , index) => {
            return <li key={index} >{ item }</li>
                  {/* 这里每个被遍历的item都需要有个key，但最好不要index */}
          })
        }
      </ul>
    </div>
  )
```
---

## 模块与组件

~~具体的概念跟vue一样，懒得写了~~ 💩💩

### 组件
#### 函数式组件

使用**函数**来创建组件 , 无状态的简单组件

```jsx
  // <div id="test"><\div> 
  // ...

  function firstComponent(){
    return <h1>Hello my first component !</h1>
  }
  ReactDOM.render(<FirstComponent/>,document.getElementById("test"))
            // 注意组件的标签首字母要大写
            // 这一步会调用函数来返回组件，虚拟DOM → 真实DOM
```

#### 类式组件
使用**类**来定义组件,**必须继承 `React.Component` 的组件**    
有状态的复杂组件
```jsx
  class mynextcomponent extends React.Component {
    render(){
      return <h1>Hello my next component !</h1>
    }
  }
  ReactDOM.render(<Mynextcomponent/>,document.getElementById("test"))
            // 这一步会new一个实例对象
```
---

### 组件<span style='color:red'>实例</span>的三大核心属性

**需要是类式组件**，~~函数定义的组件不存在组件实例~~

#### state 状态
state通过`setState()`函数来进行更改，每次更改调用一次`render()`
```jsx
  class HavestateComponent extends React.Component {
    constructor(props){
      super(props) // 继承React.Component的构造函数
      this.state = {
        isState : true 
      } // 初始化状态
      this.changeState = this.changeState.bind(this)
          // 定义了自身的同名函数，bind更改了this,使得同名函数changeState可以拿到this实例对象，此时触发事件是触发的自身事件而非原型事件
    }
    render(){
      // 读取状态
      const {isState} = this.state ;
        // 等价于 const isState = this.state.isState ;
        // render 里面的this是组件实例对象，而自定义的方法接收到一个直接引用，拿不到实例对象
      return <h1 onClick={changeState}>我是一个{isState ? '有状态' : '无状态'}的组件</h1>
    }
    changeState(){
      // 状态不能直接更改 ，而要使用setState()更改
      // const {isState} = this.state ❌
      // this.state.isState = !isState ❌
      const {isState} = this.state
      this.setState({isState:!isState})
    }
  }
  ReactDOM.render(<HavestateComponent/>,document.getElementById("test"))
```

下面是精简版的代码,精简化状态和自定义函数要修改this的问题
```jsx
  class HavestateComponent extends React.Component {

    state = { isState: true }  // state写在constructor外部

    render(){
      const {isState} = this.state ;
      return <h1 onClick={changeState}>我是一个{isState ? '有状态' : '无状态'}的组件</h1>
    }
    changeState = () => {
      const {isState} = this.state
      this.setState({isState:!isState})
      // 通过赋值将方法挂载到实例上实现this调用的转换
    }
  }
```
---

#### props
使用`props`实现父子组件通信,`props`是只读的

```jsx
  class PropsShow extends React.Component {
    render(){
      const {name,age,sex} = this.props
      //  this.props.age = age + 1 ❌ props只读
      return (
        <ul>
          <li>性别:{sex}</li>
          <li>姓名:{name}</li>
          <li>年龄:{age + 1}</li>
        </ul>
      )
    }
  }
  ReactDOM.render(<PropsShow name='小明' age={18} sex='男'/>,document.getElementById("test1")) 
  //age如果使用age='18'在render处理只是字符串拼接，最好使用下面这种写法
 
  // 也可以使用扩展符展开对象（js不允许），只允许在标签使用
  const p = {name:'小红' , age:18,sex:'女'}
  ReactDOM.render(<PropsShow {...p}/>,document.getElementById("test2"))
  // 通过props来实现复用
```

有时候我们必须对`props`进行限制,使用`propTypes`,`defaultProps`来添加类型限制和默认值
```jsx
  class PropsShow extends React.Component {
    render(){
      const {name,age,sex} = this.props
      return (
        <ul>
          <li>性别:{sex}</li>
          <li>姓名:{name}</li>
          <li>年龄:{age + 1}</li>
        </ul>
      )
    }
    static propTypes = {
      name: PropTypes.string.isRequired,
      age: PropTypes.number
      // 注意函数的类型是func
    }
    static defaultProps = {
      sex: '秘密',
      age: 18
    }
  }
  
  // ReactDOM.render(...
```
函数式组件也可以使用`props`
```jsx
  function funcProps(props) {
    const {name,age,sex} = props
    return (
      <ul>
        <li>性别:{sex}</li>
        <li>姓名:{name}</li>
        <li>年龄:{age + 1}</li>
      </ul>
    )
  }
  funcProps.propTypes = {
      name: PropTypes.string.isRequired,
      age: PropTypes.number
      // 注意函数的类型是func
  }
  funcProps.defaultProps = {
    sex: '秘密',
    age: 18
  }
```

---
#### ref
组件内的标签可以定义`ref`属性来标识自己

* 下面是**过时的**~~字符串形式的ref~~，字符串 ref 存在性能问题和一些边缘 bug，<span style='background-color:yellow;'>所以不推荐使用</span>
```jsx
 class ShowRef extends React.Component {
  showDate = () => {
    const {inputByref} = this.refs
    alert(inputByref.value)
  }
  render(){
    return (
      <div>
        <input ref='inputByref' type='text' placeholder='点击按钮输出数据'/>
        <button onClick={this.showDate}>点击输出数据</button>
      </div>
    )
  }
 }
```

* 回调形式的`ref`
  1. 使用内联函数回调，更新的时候会被执行两次，第一次传入null，然后才是虚拟DOM
  ```jsx
  class ShowRef extends React.Component {
    showDate = () => {
      const {inputByref} = this
      alert(inputByref.value)
    }
    render(){
      return (
        <div>
          <input ref={(e)=>{this.inputByref = e}} type='text' placeholder='点击按钮输出数据'/>
          <button onClick={this.showDate} >点击输出数据</button>
        </div>
      )
    }
  }
  ```

  2. 写成class方式可以解决调用两次的问题,但是大多数情况下无关紧要
  ```jsx
  class ShowRef extends React.Component {
    showDate = () => {
      const {inputByref} = this
      alert(inputByref.value)
    }
    saveInput = (e) => {
      this.inputByref = e ;
    }
    render(){
      return (
        <div>
          <input ref={this.saveInput} type='text' placeholder='点击按钮输出数据'/>
          <button onClick={this.showDate} >点击输出数据</button>
        </div>
      )
    }
  }
  ```

* 使用 `createRef()`,调用后可以放回一个容器，容器可以存储被ref标识的节点
```jsx
  class ShowRef extends React.Component {
    myRef = React.createRef()
    showDate = () => {
      alert(this.myRef.current.value)
    }
    render(){
      return (
        <div>
          <input ref={this.myRef} type='text' placeholder='点击按钮输出数据'/>
          <button onClick={this.showDate} >点击输出数据</button>
        </div>
      )
    }
  }
```

---
## React 事件处理
通过onXxx指定事件处理函数，使用事件委托来处理  
通过`event.target`获得触发事件的对象，**不要过度使用`ref`**

* 非受控组件
  输入类的DOM，现用现取
* 受控组件
  输入维护状态

---
## 函数柯里化

调用的函数返回函数，统一处理参数，来复用函数，减少代码量

```jsx
  class Frombyself extends React.Component{
    state = {
      username:'',
      password:''
    }
    saveData = (data) =>{ // 这里拿到数据
      return (event) => { // 这里回调函数，event为当前的节点
        this.setState({
          [data]: event.target.value
        })
      }
    }
    render(){
      return (
        <from >
          账号：<input onChange={this.saveData('username')} type='text' name='username'/>
          密码：<input onChange={this.saveData('password')} type='password' name='password'/>
          <button>提交</button>
        </from>
      )
    }
  }
```

如果不使用函数柯理化的话，可以这么写：
```jsx
// ...
  saveData = (data,event) =>{ // 这里拿到数据
    this.setState({
      [data]:event.target.value
    })
  }
  render(){
    return (
      <from >
        账号：<input onChange={(event) => {this.saveData('username',event.target.value)}} type='text' name='username'/>
        密码：<input onChange={this.saveData('password')} type='password' name='password'/>
        <button>提交</button>
      </from>
    )
  }

```
---

## 组件生命周期

卸载组件使用`ReactDOM.unmountComponentAtNode(document...{id/class})`
React 的生命周期钩子主要分为**类组件**和**函数组件**两个体系来理解。随着 React 版本的演进，函数组件中的 Hooks 已成为主流。

---

### 一、 类组件中的生命周期钩子

在类组件中，生命周期主要分为三个阶段：**挂载（Mounting）**、**更新（Updating）** 和 **卸载（Unmounting）**。

#### 1. 挂载阶段
组件实例被创建并插入 DOM 时，按顺序调用：

-   **`constructor(props)`**
    -   初始化 state 和绑定事件处理函数。如果不初始化 state 或不进行方法绑定，则不需要实现。
-   **`static getDerivedStateFromProps(props, state)`**（React 16.3+）
    -   在 `render` 之前调用。根据 props 来更新 state。返回一个对象来更新 state，或返回 null 表示无更新。
    -   *注意：这是一个静态方法，无法访问 `this`。*
-   **`render()`**
    -   唯一必须实现的方法。根据 props 和 state 返回 JSX。**注意：** 在 `render` 中不能调用 `setState`，否则会导致无限循环。
-   **`componentDidMount()`**
    -   组件挂载后（DOM 已生成）立即调用。
    -   适合在此处进行**副作用操作**：发送网络请求、添加订阅、操作真实 DOM。

#### 2. 更新阶段
当 props 或 state 发生变化时，会触发重新渲染，按顺序调用：

-   **`static getDerivedStateFromProps(props, state)`**
    -   挂载和更新时都会调用。
-   **`shouldComponentUpdate(nextProps, nextState)`**
    -   用于性能优化。返回 `false` 可以阻止组件重新渲染（不会阻止子组件的渲染）。默认返回 `true`。
-   **`render()`**
    -   重新计算虚拟 DOM。
-   **`getSnapshotBeforeUpdate(prevProps, prevState)`**（React 16.3+）
    -   在最近一次渲染输出（提交到 DOM 前）之前调用。返回值会作为第三个参数传给 `componentDidUpdate`。
    -   常用于在 DOM 更新前获取滚动位置等信息。
-   **`componentDidUpdate(prevProps, prevState, snapshot)`**
    -   更新后立即调用。在此处可以进行 DOM 操作或发起网络请求（注意对比 props 变化，避免无限循环）。

#### 3. 卸载阶段
-   **`componentWillUnmount()`**
    -   组件销毁前调用。用于清理定时器、取消网络请求、清除订阅等。

#### 4. 错误处理阶段
-   **`static getDerivedStateFromError(error)`**
    -   在后代组件抛出错误后调用，用于渲染降级 UI（展示错误边界）。
-   **`componentDidCatch(error, info)`**
    -   用于记录错误信息。

> **注意**：`componentWillMount`、`componentWillReceiveProps`、`componentWillUpdate` 这些旧的生命周期钩子已在 React 17+ 中被废弃（需要加 `UNSAFE_` 前缀才能使用），不推荐在新代码中使用。

![常用生命周期钩子一览](https://s41.ax1x.com/2026/03/28/pe1YZHP.png)

---

## Diffing 算法

1. key是虚拟DOM的标识，在更新显示时key起着极其重要的作用，更新的时候，react会新旧进行diff比较，如果key在新旧之间相同，则会进行比较之后替换，如果找不到则会添加新的DOM
2. 使用index作为key可能会引发：
  1. 逆序添加等破坏结构性顺序的操作    
  会产生没必要的DOM更新 => 效率极低
  2. 如果还包含输入类的DOM => 界面会出现问题（数据错乱）
  3. 如果不涉及以上操作还是没问题的
3. 开发中如何选择：
  * 最好使用id，uid，等唯一值
  * 如果是简单的更新，使用index也可以

---
## TodoList 拆解

拆分成四个组件，分别是`APP.jsx`,`Head.jsx`,`List.jsx`,`Footer.jsx`
* `APP.jsx`部分负责页面的框架，在state内存储Todos对象列表
* `Head.jsx` 负责添加部分，主要内容为输入框来进行添加Todo对象
* `List.jsx` 负责展示内有的Todo内容，和勾选`done`状态
* `Footer.jsx` 负责全选勾选框，查找，删除`done`为 true 的组件

**存储的todos：**
```jsx
// App.jsx
class App extends Component {
  state = {
    todos:[
      {
        id: number , //唯一id
        todo: Str , // 展示内容
        done: bool  , // 标记是否已完成
        isMatch: bool // 标记是否符合查找条件
      },
    ]
  } ;
}
```

### 增

数据存储在App的state之中，通过父子级通信，来修改APP的state来实现

```jsx
// App.jsx
class App extends Component {
  fetchData = (dataObj) => {
    const {todos} = this.state
    const newtodos = [dataObj,...todos]
    this.setState({todos:newtodos})
  } //通过回调函数实现，父子级组件通信
  // ...
  render(){
    <>
      <Head fetchData={this.fetchData}></Head>
    </>
  }
}

//Head.jsx
export default class head extends Component {
  handleKeyup = (e) => {
    if(e.keyCode != 13 ) return
    if(e.target.value.trim() === ''){
      alert("请输入有效内容")
      return
    } // 处理输入为空或按下不为回车返回

    const unionkey = Math.floor(Date.now() + Math.random()*10e4 - Math.random()*10e4) // 唯一key，因为懒没用uuid

    const todoObj = {
      id:unionkey,
      todo: e.target.value ,
      done:false ,
      isMatch:false
    } //要增加的数据

    this.props.fetchData(todoObj) // 回调函数，父级拿到数据
    e.target.value = ''
  }

  <input className='...'
  placeholder='请输入待办事项' onKeyUp={this.handleKeyup}/>
}
```


### 删

三类删除

1. 绑定在List上的删除当前元素
  ```jsx
  // App.jsx
  class App extends Component {
    render(){
      return (
        <List todos={todos}
        delDate={this.delDate}></List>
      )
    }
  }
  // List.jsx
  handleDel = (id) =>{
    return (e) => {
      if(window.confirm('确定删除吗')){ // 这里的window不能省略
        this.props.delDate(id)
      }
    }
  }
  <button className=''
  onClick={this.handleDel(todo.id)}
  >删除</button>
  ```
2. 清除所有已完成
  ```jsx
  //App.jsx
  class App extends Component {
    clearAllDone = () => {
    const {todos} = this.state
    const newTodos = todos.filter((todo)=>{
      return todo.done === false
    })
    this.setState({todos:newTodos})
    }
    render(){
      return (
        <Footer todos={todos}
        clearAllDone={this.clearAllDone}
        ></Footer>
      )
    }
  }

  //Footer.jsx
  export default class Footer extends Component {
    handleClear = () =>{
      this.props.clearAllDone()
    }
    render(){
      return(
        <button className=''
          onClick={this.handleClear}
        >清除全部已完成</button>
      )
    }
  }
  ```
3. 清除所有查询状态
  ```jsx
  //App.jsx
  class App extends Component {
    clearAllmatch = (newtodos) => {
      this.setState({todos:newtodos})
    }
    render(){
      return(
      <Footer todos={todos}
      clearAllmatch={this.clearAllmatch}></Footer>
      )
    }

  }


  //Footer.jsx
  export default class Footer extends Component {
    clearAllMat = () =>{
      const {todos} = this.props
      const newTodos = todos.map((todo) => {
        return {...todo,isMatch:false}
      })
      this.props.clearAllmatch(newTodos)
    }
    render(){
      clearAllMat = () =>{
        const {todos} = this.props
        const newTodos = todos.map((todo) => {
          return {...todo,isMatch:false}
        })
        this.props.clearAllmatch(newTodos)
      }
      return(
        <button className=''
        onClick={this.clearAllMat}>
        清除当前查询</button>
      )
    }
  }
  ```
### 改
1. 改变当前todo的done属性
  ```jsx
  // App.jsx
  class App extends Component {
    changeData = (id,done) =>{
      const {todos} = this.state
      const newtodoObj =  todos.map((todo) => {
        if(todo.id === id){
          return {...todo,done}
        }else{
          return todo
        }
      })
      this.setState({todos:newtodoObj})
    }
    render(){
      return(
        <List todos={todos}
        changeData={this.changeData} 
        ></List>
      )
    }
  }

  //List.jsx
  export default class List extends Component {
    handleClick = (id) => {
    return (e) =>{
      this.props.changeData(id,e.target.checked)
    }
  }
    render(){
      return(
        <input type="checkbox" checked={todo.done} 
        onChange={this.handleClick(todo.id)}/>
      )
    }
  }
  ```
2. 修改当前事项
   ```jsx
   // App.jsx
    class App extends Component {
      changeVal = (id , newVal) =>{
        const {todos} = this.state
        const newtodos = todos.map((todo)=>{
          if(todo.id != id){
            return todo ;
          }else{
            return {...todo, todo:newVal}
          }
        })
        this.setState({todos:newtodos})
      }
      render(){
        return(
          <List todos={todos}
          changeVal = {this.changeVal}></List>
        )
      }
    }
    // List.jsx
    export default class List extends Component {
      doubleHandleRev = (id) =>{
        return (e) => {
          const {editid} = this.state
          const newediid = id === editid ? null : id
          this.setState({editid:newediid})
        }
      }
      onKeyuprev = (id) => {
        return (e) => {
          if(e.keyCode !== 13) return;
          if(e.target.value.trim() === ''){
            alert('修改无效，请输入有效值')
            this.doubleHandleRev(id)(e);
            return
          }
          const newVal = e.target.value.trim()
          this.props.changeVal(id,newVal)
          this.doubleHandleRev(id)(e)
        }
      }
      render(){
        return(
          {!isEditing ? (
            <li className={`list-none ${!todo.isMatch ? 'bg-transparent': 'bg-[#ff6b6b]'}`}
              onDoubleClick={this.doubleHandleRev(todo.id)}
              key={todo.id}> {todo.todo} 
            </li>)
            :(
              <input type='text'
              className='outline-none'
              autoFocus
              onKeyUp={this.onKeyuprev(todo.id)}
              onDoubleClick={this.doubleHandleRev(todo.id)}
              onBlur={()=> {this.setState({editid: null})}}/>
          )}
        )
      }
    }
    ```

### 查

通过模糊匹配高亮符合查找的todo

```jsx
// App.jsx
  class App extends Component {
    findTodo = (DataArr) => {
      const {todos} = this.state
      const matchId = DataArr.map(t => t.id)
      const newTodos = todos.map((todo) => {
        return ({...todo,isMatch:matchId.includes(todo.id)}) ;
      })
      this.setState({todos:newTodos})
    }
    render(){
      return(
        <Footer todos={todos}
        findTodo ={this.findTodo}></Footer>
      )
    }
  }
  export default class Footer extends Component {
    keyupFind = (e) =>{
      if(e.keyCode !== 13 || e.target.value === ''){
        return ;
      } 
      const {todos} = this.props
      const todoRes = todos.filter((todo)=>{
        return todo.todo.includes(e.target.value)
      })
      this.props.findTodo(todoRes)
      e.target.value = ''
    }
    render(){
      return(
        <input type="text" placeholder='查询任务(按下回车后检索)'
        onKeyUp={this.keyupFind}/>
      )
    }
  }
```
---
## react ajax

### 配置代理

配置微小服务器解决axios跨域问题

1. 配置一个代理  
在package.json 里面添加 "proxy":"$(url)"

2. 配置多个代理
在src内创建文件setupProxy.js，语法cjs  
在使用axios请求时，走代理需要在网址后添加/api1/端口
```jsx
const proxy = require('http-proxy-middleware')

module.exports = function(app){
  app.use(
    proxy('/api1',{
      target:'$(url)', // 请求转发给谁
      changeOrigin:true, // 控制服务器收到的请求头中Host字段的值
      pathRewrite:{'^/api1':''} // 重写请求路径
    }),
    // 通过更改不同的前缀来访问不同的服务器来配置多个代理
    proxy('/api2',{
      target:'$(url)',
      changeOrigin:true,
      pathRewrite:{'^/api1':''}
    })
  )

}
```

### xhr 和 fetch
**现在的axios和jQuery都是对xhr的封装**
* xhr


* fetch
 
使用性不高，因为兼容性问题，实现了xhr没做到的关注分离，对实现进行了细致的拆分

```jsx
fetch("url").then(
  response => {
    console.log('服务器有响应')
    return response.json() //如果联系成功就会返回一个Promise对象，状态同实例一样
  },
  error => {
    // 这里应该中断promise链，否则会返回undefine，走获取数据成功的路线
    return new Promise(()=>{})
  }
  // 也可以不写error，使用catch来统一回复错误
).then(
  responese => {
    // 此时才真正拿到数据
  }
  error => {console.log('获取数据失败了')}
  // 也可以不写error，使用catch来统一回复错误
).catch(
  (error) => {console.log(error)}
)
```
也可以继续优化
```jsx
//注意封装的函数要 + async
  try {
    const response = await fetch("url")
    const data = await response.json()
    ...
  }catch(error){
    console.log('请求出错',error)
  }
```
---
## 兄弟组件通信

为什么单独开呢，当然是因为山龟骨就这么讲😡，2020年的教程属实有点过时了

### 消息订阅与发布机制

不一定只有兄弟，也可以穿透  
在 React 中实现消息订阅与发布（Pub/Sub）机制，常用以下库：
1. pubsub-js（最经典、最常用，尤其在中文社区）
2. mitt（现代推荐，轻量级 Event Emitter）

下面使用pubsub-js演示

```jsx
import PubSub from 'pubsub-js'

PubSub.publish('', {})
// 发布的消息名 ↑  数据 ↑ 可以是对象
                // 订阅的消息名 ↓  订阅的消息名 ↓ 数据 ↓
const token =  PubSub.subscribe('',(msg,data)=>{
  // 内部的处理函数 ，一般在组件挂载后开始订阅
}) 

// 组件卸载后停止订阅，传入上面接收的消息接收的token（id）
PubSub.unsubscribe(this.token)

```
---

## SPA应用

单页面应用，整个应用只有一个完整的页面，点击页面中的链接不会全局刷新，只有局部更新

### 路由

前端路由依靠浏览器的history操作
* 哈希路由（#）`<HashRouter><\HashRouter>`
* `<BrowserRouter></BrowserRouter>`
  

**哈希路由（HashRouter）和 BrowserRouter 的主要区别**如下：

#### 1. **URL 表现形式不同**（最直观的区别）
- **BrowserRouter**：使用干净的路径 URL  
  示例：`https://example.com/about` 或 `https://example.com/products/123`

- **HashRouter**：URL 中带 `#`（哈希片段）  
  示例：`https://example.com/#/about` 或 `https://example.com/#/products/123`

浏览器在 `#` 后面的内容**不会发送给服务器**，这是核心差异。

#### 2. **底层实现原理不同**
- **BrowserRouter**：基于 HTML5 **History API**（`pushState`、`replaceState` 等）。  
  React Router 通过监听 `popstate` 事件来处理路由变化。

- **HashRouter**：基于 URL 的 **hash**（`window.location.hash`）。  
  通过监听 `hashchange` 事件来处理路由变化。

#### 3. **部署和服务器配置要求**
- **BrowserRouter**：
  - 需要服务器支持 **SPA（单页应用）配置**。
  - 所有路由（如 `/about`、`/products/123`）都必须返回同一个 `index.html` 文件。
  - 否则刷新页面或直接访问子路由会 **404**。
  - 常见配置：Nginx、Apache、Vercel、Netlify 等都很好支持。

- **HashRouter**：
  - **不需要**任何服务器配置。
  - 即使是纯静态托管（GitHub Pages、普通静态服务器、甚至本地打开 `index.html`）也能正常工作。
  - 因为服务器永远只看到 `/` 这个路径，`#` 后面的路由由前端自己处理。


---

路由链接使用`<Link to='url'></link>`

```jsx
<BrowserRouter>
  <Link className='' to='url'>About</link>
  <Link className='' to='url'>home</link>
</BrowserRouter>
```

如果想要有动态css，使用`<NavLink></NavLink>`,然后使用activeClassName来自定义高亮属性
```jsx
<NavLink activeClassName='bg-red-200' to='url'></NavLink>
```
可以自定义组件对`<NavLink></NavLink>`封装来提高代码的简洁性
```jsx
// MyNavLink.jsx
class MyNavLink extends React.Component {
  render(){
    // const {to} = this.props
    // const {title} = this.props
    return(
      <NavLink activeClassName='bg-red-200' {...this.props} />
    )
  }
}

// 
<MyNavLink to='/home'>Home</MyNavLink>

```


注册路由使用`<Route path='/about' component={About}/>`
```jsx
  <BrowserRouter>
    <Route path='/about' component={About}/>
    <Route path='/home' component={Home}/>
    {/* 注意上下两个得用同一个路由标签包裹 */}
  </BrowserRouter>
```

路由的匹配原则是遍历匹配，如果有多个路由可能会出现效率问题，可以使用`<Switch></Switch>`包裹，只会匹配第一个符合路径的路由
```jsx
  <Switch>
    <Route path='/about' component={About}/>
    <Route path='/home' component={Home}/>
    <Route path='/home' component={Index}/>
  </Switch>
```

路由有模糊匹配，Link内可以多给，但是Route不能，看根路径匹配从左往右，[输入的路径]必须包含[匹配的路径]

如果不想要模糊的话，可以使用`exact={true}`属性,但是严格匹配不能随便开,二级路由会有问题

```jsx
  <BrowserRouter>
    <Route exact path='/about' component={About}/>
    <Route exact path='/home' component={Home}/>
  </BrowserRouter>
```

如果要默认展示路由的话，可以使用`<Redirect />`来重定向，当所有路由都没法匹配的时候，来重定向

```jsx
  <BrowserRouter>
    <Route exact path='/about' component={About}/>
    <Route exact path='/home' component={Home}/>
    <Redirect to='/home' />
  </BrowserRouter>
```

### 嵌套路由

路由按先后注册顺序匹配，二级路由需要在路径添加父路由的路径，假如开启严格匹配子路由都会匹配不到

### 路由组件传递参数

路由子组件也可以收到参数

#### params

在注册路由的时候得声明接收params参数

```jsx
  // 声明接收id，和title参数
  <Route path='url/:id/:title'  component={Component}  />
  // 使用${}来传递params
  <Link to={`/url/${ud}/${title}`}><Link/>
  {/* 接收的使用 this.props.match.params.id */}

```

#### search

```jsx
  // searcch 参数无需声明接收
  <Route path='url'  component={Component}  />
  // 使用？名称=${}来传递search
  <Link to={`/url/?id=${id} & title=${title}`}><Link/>
  {/* 接收的使用querystring这个库*/}
  import qs from 'querystring'
  qs.stringify(obj) // 将对象转换为urlencoding
  qs.parse(str) //将urlcoding转换为对象
  const {search} = this.props.location
  const res = qs.parse(search.slice(1)) // 这里就拿到了传入了对象数据
```

#### state

是路由组件独有的不同上文的state

```jsx
// state 参数无需声明接收
 <Router  path='url'  component={Component}/>
 <Link to={{pathname:'url',state:{id:id,title:title}}}/>
// 使用this.props.location.state 取出 

```

### 编程式路由导航

可以使用`this.props.history.replace(url,state)`或者是`push(url,state)`来自定义事件路由跳转，可以携带参数  
如果想传入state参数，使用函数的第二个参数即可即可

如果要一般组件上实现路由组件的api，可以使用`withRouter`, 在暴露的时候使用`export default withRouter(Componnent)`,`withRouter`的返回值是组件

---

## redux

redux专门用于状态管理的JS库，来共享状态，用在比较复杂的，能不用就不用

### redux 的三个核心概念

先建立一个redux文件夹，里面写入要有组件的redux和store的js文件，
```js
// store.js
import {craetStore , applyMiddleware} from 'redux'
import Reducer from './url' //引入你写的redux
import thunk from 'redux-thunk'

export default const store = createStore(Reducer,applyMiddleware(thunk)) // 第二个参数是异步用的

// Redux.js
// 会接到之前的状态和动作状态action
function Reducer(preState,action){
  const {type,data} = action // 拿到了一个字符串和数据对象，根据type判断动作
  // 这里处理事务，返回一个值
}

//action.js 
//为组件生成action对象
const creatAction = (data) => {
  return {type:'',data} // 返回Obj，同步action
}

const creatAction = (data,time) => {  
  // 异步action指的是action的值是函数
  return () => {
    setTimeout(()=>{
      store.dispath({type:'',data})
    },time)
  }
}

// Component.jsx
import store from './redux/url' // 用于获取store
import {creatAction} from './action' //创建action对象

console.log(store.getState()) //获取状态

store.dispath(creatAction(value)) //分发数据，但是不会触发render去重新挂载，需要使用下面的api

componentDidMount(){
  //组件挂载之后检测组件的变化
  store.subscribe(()=>{
    this.setState({})
    // 调空状态强制调用render
  })
}

// 也可以在跟组件直接写
store.subscribe(()=>{
  ReactDOM.render(<App/>,document.getElementById('root'))
})
```

### react-redux

react官方出的redux库，所有的UI组件都要包裹一个容器的组件，是父子关系，UI不能直接和react打交道，但是可以通过容器组件父子级通信来获取数据

* 容器组件
```jsx
import UIcomponent  from 'url'
import {connect} from 'react-redux'

// a 函数的返回值作为状态传递给UI组件
function a (state){
  return { n:store.getState()} 
  // 子组件就可以通过props拿到n
}

function b(dispath) {
  return { jia:(data)=>{
    //一些逻辑部分
  }}//也可以传入一个函数
}

export default  const container = connect(a,b)(UIcomponent) //使用connet关联UI和redux,第一个参数只能是函数


```

* store引入
容器的store不能直接引入，得在app里引入
```jsx
  import store from './redux/store'
  <Conponent store={store}>
```
---

## 扩展

### setState

setState其实不止可以传入对象，还可以传入函数  
如果新状态不依赖于原来的state，使用对象方式，如果新状态依赖原来的state，使用函数式

```jsx
export default class Demo extends Component {
  state = {cnt:0}
  hanldChick = ()=>{
    const {cnt} = this.state
    this.setState((state,props)=>{
      return {cnt:state.cnt+1}
      // 能拿到state和props
    }) 
  } //传入一个返回对象的函数
  render(){
    return(
      <div onClick='hanldChick'></div>
    )
  }
}
```

---

### lazyLoad

在引入需要做懒加载的组件适合，不直接import而是使用`lazy()`函数,同时也要配置`Suspense`

```jsx
const Home = lazy(()=>{import('./Home')})

//在引入组件的时候

<Suspense fallback={<h1></h1>}> {/* 如果用户网络慢返回什么 */}
  <Route path='/url' compoent={Home}/>
  <Route />
</Suspense>

```

---

### Hooks

可以在函数组件中使用类的所有功能

#### State Hook
```jsx
function Demo(){
  const [data,fuc] = React.useState(0) //不会因为多次调用而覆盖
  const add = ()=>{
    fuc(data + 1)
    //或者
    fuc((data)=>{
      return {dara:data+1}
    })
  }
  return(

  )
}

```

#### EffectHook

```jsx
function Demo(){
  React.useEffect(()=>{

    return ()=>{

    } //相当于卸载组件的回调
  },[]) //第二个参数传入要监测的内容，传入空则只在挂载的时候触发，不传入则全监听

  return (

  )
}
```

#### RefHook

```jsx
function Demo(){
  const myRef = React.useRef()
  return (
    <input ref={myRef} />
  )
}
```

#### Fragment

如果限制于jsx只能return一个根组件的话，可以使用`<Fragment></Fragment>`标签，这个标签会在jsx解析后丢失


#### Context

一种组件的通信方式，用于祖组件和后代组件的通信方式

```jsx
// 创建Context对象
const XxxContext = React.createContext()
const {Provider} = XxxContext
// 下方的后代组件用Provider包裹

function FatherComponent () {

  return (
    <Provider vaule={value}> //传入要写入的数据，传入多个使用对象即可{{value:value ,age:age}}
      <B/> //之后代组件就都能收到
    </Provider>
  )
}
// 子组件必须声明接收Context

function B (){
 return (
  <div>
    <Consumer>
      {
        (value)=>{
          return `${value.value}` //使用Consumer接收
        }
      }
    </Consumer>
  </div>
 )
}
```

---

#### PureConponent

只要父组件render()，子组件也会重新render()，即使子组件没有调用到父组件的所有东西，有时候可能会产生效率问题,只有当props更改时候，子组件才render()

调用`shouldCompinentUpdate(nextProps,naxtState)`,检查前后对比即可

但是react封装了一个更好用的`PureComponent`

```jsx
export default class FatherComponent extends PureComponent{
  // 这样就不会 , 但是只是浅对比
}
```

---

#### renderProps

如果先写组件没有确定父子级别关系的话，可以这样写

```jsx
export default class Parents extends Component{
  render(){
    return (
      <A render={ (name)=> <B name={name}/> } />
      // 然后A组件使用this.props.render(name) 传递给B

    )
  }
}
```

---

#### 错误边界

不让子组件的错误影响到整个页面，在父组件做边界处理，但是只适合生产环境，不适合开发环境，在开发环境是没用的

```jsx
export default class Parent extneds Component {
  state = {hasError:''}
  static getDerivedStateFromError(error){
    return {hasError:error}
  }//当子组件出现报错时，会触发这个调用，并得到错误

  componnentDidCatch(){
    // 在这统计错误，发送后台，只能捕获生命周期产生的错误
  }

  render(){
    return (
      <>
      {
        this.state.hasError ? <h2>当前网络繁忙</h2> : <>正常渲染即可</>
      }
      </>
    )
  }
}
```
---

## redux

使用步骤：  
1. 定义一个`reducer`函数（根据当前想要做的修改返回一个新的状态）
2. 使用`createStore`方法传入`reducer`函数，生成一个store实例对象
3. 使用store实例的`subscribe`方法订阅数据的变化（数据一旦变化，可以得到通知）
4. 使用store实例的`dispath`方法提交action对象触发数据变化（告诉reducer你想怎么改数据）
5. 使用store实例的`getState`方法获取最新的状态数据更新到视图中

```js
<script>
  function reducer (state = {cnt:0},action) {
    if (action.type == 'value1') {
      return {cnt:state.cnt+1}
    }else if(action.type == ''){
      return {cnt:state.cnt-1}
    }
    return state
  }

  const store = Redux.createStore(reducer)

  store.shbscribe(()=>{
    log('state变化了')
    document.getElementById('cnt').innerText = store.getState().cnt 
  })

  const btn = document.getElementById('btn')
  btn.addEventListener('click',()=>{
    store.dispatch({
      type:'value1' ,


    })
  })
</script>

```

也可以使用**Redux Toolkit和react-redux**，来在react中更简单的使用redux

1. 通常集中状态管理的部分都会单独创建一个单独的`store`目录
2. 应用通常都会有很多个store模块，所以创建一个`modules`目录，在内部编写业务分类的子store
3. store中的入口文件`index.js`的作用是组合modules中的所有子模块，并导出store
  
> --store
> | -- modules
> | | -- cntStore.js
> | | -- changeStore.js
> | -- index.js

```jsx
//cntStore.js
createSlice({
  name:'cnt',
  // 初始化state
  initialState:{
    cnt: 0
  },
  // 修改数据的方法
  reducers:{
    add(state){
      state.cnt++
    },
    del(state){
      state.cnt --
    },
    toTen(state,action){
      state.cnt = action.payload
    }
  }
})
// 结构出来actionCreater 函数
const {add,del} = cntStore.actions
// 获取reducer
const reducer = cntStore.reducer
// 按需导出的方式导出action
export {add ,del}
// 导出reducer
export default reducer
```
在index.js中
```js
import reducer from './modules/counterStore'

const store = configureStore({
  reducer:{
    counter:counterReducer
  }
})

export default store
```

react-redux负责把Redux和React链接起来

```js
//index.js
  <Provider store={store}>

  </Provider>
```

```jsx
function App(){
  const {cnt} = useSelector(state => state.counter)
  const dispatch = useDospatch()

  return(
    <div>
      <button onClick={ ()=>dispath(add()) }>+<button>
    </div>
  )
}
```

也可以异步修改

1. 创建store的写法保持不变，配置好同步修改状态的方法
2. 单独封装一个函数，在函数内部return一个新的函数，在新函数中
   * 封装异步请求获取数据
   * 调用同步actionCreater传入异步数据生成一个action对象，并使用dispatch提交
3. 组件中dispatch的写法保持不变
   
```js
const channelStore =  createSlice({
  name:'name',
  initialState:{
    List:[]
  },
  reducers:{
    setChannels(state,action){
      state.channelList = action.payload
    }
  }
})


const = {setChannels} = channelStore.action

const fetchChanlList = () => {
  return async (dispatch) => {
    const res = await axios.get('url')
    dispatch(setChannels(res.data.data.channels))
  }
}
export {fetchChanlList}

const reducer = channelStore.reducer
export default reducer
```

在index.js

```js
import channelReducer from './modules/channelStore'

const store = configureStore({
  reducer:{
    channel:channelReducer
  }
})

export default store
```

在组件中

```jsx
function App(){
  const {channelList} = useSelector(statte=>state.channel)
  const dispatch = useDispatch()
  useEffect(()=>{
    dispatch(fetchChannlList())
  },[dispatch])
  // 使用useEffect触发异步请求执行
}
```
---

## 路由6

### 创建路由

```jsx
//创建router实例对象并且配置路由对应关系

const router = createBrowserRouter([
  {
    path:'/url',
    element:<Home/>
  },
  {
    path:'/url',
    element:''

  }
])

// 路由绑定
<RouterProvider router = {router} />
```

### 编程式导航

```jsx
const Login = () => {
  const navigate = useNavigate()
  return (
    <div>
      <buttton onClick={()=>navigate('url')}
      ></button>
    </div>
  )
}
```

### 路由传参

#### searchParams

```jsx
<buttton onClick={()=>navigate('url?id=101&name=jack')}
{/* 通过下面获得 */}
const [params] = useSearchParams()
const id = params.get('id')
```

#### Params

```jsx
// 记得在配置路由url的时候/url:id声明自己要接受的参数
<buttton onClick={()=>navigate('url?id=101&name=jack')}
{/* 通过下面获取 */}
const params = useParams()
const id = params.id
```

### 嵌套路由

```jsx
const router = createBrowserRouter([
  {
    path:'/url',
    element:<Home/>,
    children:[
      {
        paht:'/url',
        element:'</>'
      },
      {
        parh:'.url',
        element:'</>'
      }
    ]
  },
  {
    path:'/url',
    element:''

  }
])
```
在一级路由内部使用`<Outlet>`展示  
当访问一级路由的时候，默认的二级路由可以直接得到渲染，只需要在二级路由到位置去掉path，设置index属性为true

配置path路径为通配符，当所有组件都匹配不到的时候，就会有notfound来兜底

```jsx
const router = createBrowserRouter([
  {
    path:'/url',
    element:<Home/>,
    children:[
      {
        index:true, //这里设置默认路由
        element:'</>'
      },
      {
        parh:'*',
        element:'<Notfound/>'
      }
    ]
  },
  {
    path:'/url',
    element:''

  }
])
```
---

## 收尾

#### 业务规划

有这几个文件夹：
1. `apis`接口
2. `assets`静态资源
3. `components`通用组件
4. `pages`页面级组件
5. `router`路由Router
6. `store`Redux状态
7. `utils`工具函数


## Hook

React Hooks 是 React 16.8 版本引入的一项重大特性，它让你无需编写类组件，就能在函数组件中使用状态和其他 React 特性。

### 📖 Hooks 核心概念速览
*   **设计目标**：简化组件逻辑，将分散在各生命周期中的逻辑聚合到单一 Hooks 中；通过自定义 Hooks 优雅地复用逻辑；确立函数组件作为 React 开发的主要范式。
*   **使用规则**：**只在 React 函数组件或自定义 Hooks 的顶层调用**，不要在循环、条件或嵌套函数中使用，以保证每次渲染时 Hooks 的调用顺序一致。

### 🧰 常用核心 Hooks 详解

#### 1. `useState`：管理组件内部状态
这是最基础的 Hook，用于在函数组件中添加响应式状态。

```javascript
import { useState } from 'react';

function Counter() {
  // 声明一个名为 count 的状态变量，初始值为 0
  const [count, setCount] = useState(0);

  return (
    <div>
      <p>计数：{count}</p>
      {/* 通过调用 setCount 来更新状态 */}
      <button onClick={() => setCount(count + 1)}>+1</button>
    </div>
  );
}
```
**关键知识点**:
*   `useState` 返回一个数组，包含当前状态值和更新该状态的函数。
*   必须通过返回的 `set` 函数更新状态，直接赋值不会触发重新渲染。
*   状态更新是异步的，React 会批量处理以优化性能，因此无法立即获取最新值。
*   当新状态依赖于旧状态时，推荐使用**函数式更新**，例如 `setCount(prevCount => prevCount + 1)`，以避免因闭包导致状态过期的问题。

#### 2. `useEffect`：处理副作用操作
`useEffect` 用于处理数据请求、订阅、手动修改 DOM 等副作用，它替代了类组件中的 `componentDidMount`、`componentDidUpdate` 和 `componentWillUnmount` 生命周期。

```javascript
import { useState, useEffect } from 'react';

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // 组件挂载后或 userId 变化时执行
    fetch(`/api/users/${userId}`)
      .then(response => response.json())
      .then(data => setUser(data));

    // 可选的清理函数，在组件卸载或下次执行 effect 前运行
    return () => {
      console.log(`组件即将卸载或 userId 即将变为 ${userId}，可以在这里清理订阅或取消请求`);
    };
  }, [userId]); // 依赖数组：只有当 userId 变化时，才会重新执行 effect

  return <div>{user?.name}</div>;
}
```
**依赖数组的执行时机**:
| 依赖数组 | 执行时机 | 类比生命周期 |
| :--- | :--- | :--- |
| 无 | 组件每次渲染后都执行。 | `componentDidUpdate` |
| `[]` (空数组) | 只在组件挂载后执行一次。 | `componentDidMount` |
| `[dep1, dep2]` | 组件挂载后和任一依赖项变化后执行。 | `componentDidUpdate` (有判断) |

#### 3. `useContext`：跨组件传递数据
`useContext` 让你能轻松地消费 Context，避免了通过 props 逐层传递数据的麻烦。

```javascript
// 1. 创建 Context
import { createContext, useContext } from 'react';
const ThemeContext = createContext('light');

function App() {
  // 2. 使用 Provider 提供数据
  return (
    <ThemeContext.Provider value="dark">
      <Toolbar />
    </ThemeContext.Provider>
  );
}

function Toolbar() {
  return <ThemedButton />;
}

function ThemedButton() {
  // 3. 在后代组件中消费数据
  const theme = useContext(ThemeContext);
  return <button className={theme}>当前主题：{theme}</button>;
}
```

#### 4. `useRef`：持有可变引用
`useRef` 返回一个可变的 ref 对象，其 `.current` 属性被初始化为传入的参数。返回的 ref 对象在组件的整个生命周期内保持不变，且当其内容变化时不会触发组件重新渲染。

```javascript
import { useRef, useEffect } from 'react';

function TextInputWithFocus() {
  // 创建一个 ref 对象
  const inputEl = useRef(null);
  // 创建一个计数器，用于记录渲染次数，但不会触发额外渲染
  const renderCount = useRef(0);

  useEffect(() => {
    renderCount.current += 1; // 更新 .current 不会导致组件重新渲染
    // 在组件挂载后，将焦点设置到输入框
    inputEl.current.focus();
  }, []);

  return (
    <div>
      <input ref={inputEl} type="text" />
      <p>组件已渲染 {renderCount.current} 次</p>
    </div>
  );
}
```
`useRef` 常用于获取 DOM 元素的引用（如管理焦点、文本选择或媒体播放）、存储“跨渲染周期”且不需要触发 UI 更新的可变值（如定时器 ID、前一个状态值等）。

### 🚀 高级 Hooks 与性能优化
当遇到性能瓶颈时，可以使用以下 Hooks 进行优化。

#### 1. `useMemo`：缓存计算结果
`useMemo` 用于缓存**值**，它会在依赖项发生变化时才重新计算，否则返回上一次缓存的结果。适用于需要大量计算开销的场景。

```javascript
import { useMemo } from 'react';

function DataAnalysis({ dataset }) {
  // 仅在 dataset 变化时，才重新计算统计数据
  const statistics = useMemo(() => {
    console.log('正在执行复杂计算...');
    return {
      sum: dataset.reduce((a, b) => a + b, 0),
      avg: dataset.reduce((a, b) => a + b, 0) / dataset.length
    };
  }, [dataset]); // 依赖项是 dataset

  return <div>总和: {statistics.sum}, 平均: {statistics.avg}</div>;
}
```

#### 2. `useCallback`：缓存函数引用
`useCallback` 用于缓存**函数**本身，在依赖项未变化时返回同一个函数引用。这主要在你需要将函数作为 props 传递给由 `React.memo` 包裹的子组件时，用于避免子组件的不必要重渲染。

```javascript
import { useCallback, useState } from 'react';

function Parent() {
  const [count, setCount] = useState(0);
  const [otherState, setOtherState] = useState('');

  // 当其他状态更新时，increment 函数引用保持不变，避免了依赖它的子组件重渲染
  const increment = useCallback(() => {
    setCount(c => c + 1);
  }, []); // 空依赖数组，函数引用永远不变

  return (
    <div>
      <ChildButton onIncrement={increment} />
      <button onClick={() => setOtherState(Date.now())}>更新其他状态</button>
    </div>
  );
}

const ChildButton = React.memo(({ onIncrement }) => {
  console.log('子组件渲染');
  return <button onClick={onIncrement}>增加</button>;
});
```
> **注意**：`useMemo` 和 `useCallback` 是性能优化的工具，应避免过度使用，仅在必要时（如复杂计算、传递回调给 `React.memo` 包裹的组件）采用，以免产生不必要的内存开销和比较成本。

### 🛠️ 自定义 Hook：逻辑复用的基石
自定义 Hook 是一个以 `use` 开头的 JavaScript 函数，其内部可以调用其他 Hook。它让你能将组件逻辑提取到可复用的函数中。

```javascript
// useFetch.js - 一个用于数据请求的自定义 Hook
import { useState, useEffect } from 'react';

function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setData(data);
        setLoading(false);
      })
      .catch(err => {
        setError(err);
        setLoading(false);
      });
  }, [url]); // 当 URL 变化时重新请求

  return { data, loading, error };
}

export default useFetch;

// 在组件中使用
function UserProfile({ userId }) {
  const { data: user, loading, error } = useFetch(`/api/users/${userId}`);

  if (loading) return <div>加载中...</div>;
  if (error) return <div>出错了: {error.message}</div>;
  return <div>用户名: {user?.name}</div>;
}
```

### ⚠️ 最佳实践与常见问题

*   **不要忽略 ESLint 规则**：强烈建议使用 `eslint-plugin-react-hooks` 插件。特别是 `exhaustive-deps` 规则，它会自动检查 `useEffect`、`useCallback`、`useMemo` 的依赖数组是否包含所有必要的值，能有效避免因依赖缺失导致的“陈旧闭包”Bug。
*   **不要修改 Hooks 的调用顺序**：始终在函数组件的顶层调用 Hooks，确保每次渲染时 Hooks 的调用顺序都保持一致，这是 React 内部正确追踪每个 Hook 状态的前提。
*   **正确清理副作用**：在 `useEffect` 中，如果创建了需要清理的资源（如订阅、定时器、事件监听器），务必在返回的清理函数中进行清理，以防止内存泄漏和不必要的性能损耗。
*   **避免在 `useEffect` 中进行不必要的操作**：不是所有与外部数据同步的操作都需要放在 `useEffect` 中。例如，由用户点击触发的 API 请求，直接在事件处理函数中执行会更清晰和高效。

### 📚 参考资源
*   **React 官方文档（中文）**: [https://zh-hans.react.dev/](https://zh-hans.react.dev/) （最权威的学习资料）
*   **ESLint 插件**: [https://www.npmjs.com/package/eslint-plugin-react-hooks](https://www.npmjs.com/package/eslint-plugin-react-hooks)

---
欢迎来到我的博客！🎉
