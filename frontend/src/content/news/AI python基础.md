---
date: 2026-04-14
title: AI python基础
category: 学习记录
tags: test, skill
---

# AI python基础

记录AI agent python基础
<!-- more -->

## 特性

* 封装
  * 私有方法 ：只能类内使用，在变量或者是函数名前加上__
* 继承
* 多态
  一项多用

## 魔法方法

```python
class Car(Object):
  def __init__(self,color,speed):
    self.color = color 
    self.speed = speed
    # 初始化类

  def __str__(self):
    return f"{self.color},{self.speed}"
    # 一定在函数内返回一个字符串，当打印对象的时候会把这串字符串打印出去

  def __def__(self):
    printCar()
    # 相当于组件卸载时候执行的，这里调用一个类内定义的方法

  def printCar(self):
    print(f'这车是我的，颜色是{self.color}，速度是{self.speed}')
    # 可以在类内自定义一个方法

  print(c1.__dict__) #可以将类转换成字典的一个魔法方法
```

## 继承

类可以多继承，也可以单继承，当多继承有同名方法的时候，优先搜索自身，然后就近原则从左往右去找，找到第一个去返回

```python
def FuteCar(Car):
  pass 
  # 这里继承了Car，有Car内的所有方法
```

## 类方法

使用`@classmethod`来定义类方法，默认只能床褥self，使用`@staticmethod`来定义静态类方法，不能传入参数

使用类名.属性,可以定义一个所有类下的对象都共享的一个类属性/类方法

## 闭包

在函数嵌套的前提下，内部的函数使用了外部函数的变量，并且外部函数返回了内部函数，**使用外部函数变量的内部函数称为闭包**

```python
def out_fn(a):
  c = 100
  def inner_fn(b):
    nonlocal c
    c += 100
    return a + b + c
  return inner_fn

print(out_fn(1)(2))
```

上面这个就是一个最简单的求和案例的闭包，一个外部函数内有一个函数，外部函数的返回值为内部函数

### 装饰器

不改变原有函数的基础上，给原有函数增加额外的功能，本质上是一个闭包函数  
有嵌套，有引用，有返回，有额外功能


下面演示一下两种最基础的装饰器的写法
```python
# 1，装饰函数没有参数
def fancy(fn_name):
  def wrapper():
    print('装饰器开始')
    fn_name()
    print('装饰器结束')
  return wrapper

@fancy
def eat():
  print('吃饭')

eat()

# 2. 被装饰函数有参数
def fancy(fn_name):
  def wrapper(food):
    print('装饰器开始')
    fn_name(food)
    print('装饰器结束')
  return wrapper

@fancy
def eat(food):
  print(f'我在吃{food}')

eat('玉米')

# 3. 装饰函数有多个参数
def fancy(fn_name):
  def wrapper(*args , **kwargs):
    print('装饰器开始')
    fn_name(*args , **kwargs)
    print('装饰器结束')
  return wrapper

@fancy
def eat(food,drink):
  print(f'我在吃{food},在喝{drink}')

eat('玉米','蜜雪')

# 4. 被装饰函数有返回值

def fancy(fn_name):
  def wrapper(*args, **kwargs):
    print('装饰器开始')
    res = fn_name(*args,**kwargs) # 这里调用的时候闯入参数
    print('装饰器结束')
    return res # 内函数要把计算结果传出去
  return wrapper

@fancy
def add(a,b):
  return a + b

res =  add(1,2)
print(f'计算结果是 {res}')

# 装饰器本身带参数
def outLoad(times): # 给装饰器套一个外壳来接收参数
  def fancy(fn_name):
    def wrapper(*args,**kwargs):
      print(f'装饰开始，准备执行{times}次')
      for i in range(times):
        res = fn_name(*args,**kwargs)
      print('装饰器结束')
      return res
    return wrapper
  return fancy  #注意要暴露装饰器

@outLoad(3) # 这里注意可以放值
def sayH(name):
  print(f'你好，{name}')

sayH('Alyssa')

```

## 网编

用来实现不同计算机运行的程序间进行数据交互

服务器的socket

```python
import socket
# 创建服务器端Socket对象， ipv4，TCP
server_socket = socket.socket(socket.Af_INET, socket.SOCK_STREAM)
# 绑定IP地址和端口号
server_socket.bind( ('',10086) )
# 设置最大监听数
server_socket.listen(5)
# 等待客户端申请建立链接
accept_socket, client_info = server_socket.accept()
# 给客户端发送消息
accept_socket.send(b'Weclome to Socket')
# 接收客户端的消息并打印
accept_socket.recv(1024).decode('utf-8')
print(accept_socket)
# 释放资源
accept_socket.close()
# server_socket.close() 服务器端一般不关闭
```

客户端的socket
```python
import socket
# 创建客户端Socket对象
client_socket = socket.socket(socket.Af_INEF, socket.SOCK_STREAM)
# 连接服务器端，指定：服务器端IP，端口号
client_socket.connect( ('',10086) )
# 接收服务器端的信息并打印
data = cilent_socket.recv(1024).decode('utf-8')
print(data)
# 给服务器端发送消息
client_socket.send(b'HEILLO')
# 释放资源
client_socket.close()
```

## 多进程多线程

并发： 一段时间内，交替执行任务
并行： 一段时间内，真正的同时一起执行任务

1. 导入进程工具包`import multiprocessing`
2. 通过进程类 实例化进程 对象 `子进程OBJ = mutiprocessing.Process()`
3. 启动进程执行任务 `进程对象.start()`

```python
子进程对象 = multiprocessing.Process(group=None, target=None, name=None, args=(), kwargs={})

# group 参数未使用，值始终未None
# target 表示调用对象，即子进程要执行的任务（回调函数入口地址）
# args 表示以元组的形式向子任务参数传参， 元组方式传参一定要和参数的顺序保持一致
# kwargs 表示以字典的方式给子任务传参，字典方式传参字典中的key要和参数名保持一致
# name 子进程的名称

import multiprocessing

def codong():
  for i in range(11):
    time.sleep(0.3)
    print(f'正在敲第{i}行代码')

def listing(name):
  for i in range(11):
    time.sleep(0.3)
    print(f'{name} 正在听第{i}遍音乐')

p1 = multiprocessing.Process(target=coding)
p2 = multiprocessing.Process(target=listing args=('刘备'))

p1.start()
p2.start()

# os.getpid() 获取进程pid
```

操作系统通过MMU（内存管理单元）给每个进程映射一套独立的页表，使得进程 A 的 0x1000 地址和进程 B 的 0x1000 地址指向完全不同的物理内存。这种隔离是权限和映射层面的强制隔离，即便进程想主动访问别人的资源，硬件层面也会触发段错误。


**进程拥有独立的虚拟地址空间，操作系统通过页表映射隔离物理内存。即便父子进程通过写时复制共享物理页，两者也无法直接访问对方的地址空间，这是数据隔离的根本原因。**

### 进程守护

默认情况下，主进程会等待子进程执行结束再结束  
如果要设置主进程子进程同步结束：  
1. 设置子进程为 守护进程
   `p1.daemon = True`
2. 强制关闭子进程
   `p1.terminate()`

---

### 线程
  
* 进程（Process）：是资源分配的最小单位，数据间相互隔离
* 线程（Thread）：是CPU 调度的最小单位。一个进程内部可以包含多个线程，它们共享该进程的绝大部分资源。

```python
线程对象 = threading.Thread(group=None, target=None, name=None, args=(), kwargs={})

# group 线程组，只能使用None
# target 执行的目标任务名
# args 以元组的方式给执行任务传参，元组方式的传参一定要和目标任务函数参数的任务一致
# kwargs 以字典的方式给执行任务传参，字典的key一定要和参数的顺序保持一致
# name 线程名，一般不用设置

def coding():
  for i in range(11):
    print(f'正在敲第{i}行代码')

def listing(name):
  for i in range(11):
    print(f'{name} 正在听第{i}首歌')

if __name__ == '__main__':
  t1 = threading.Thread(target=coding)
  t2 = threading.Thread(target=listing,args=('老王'))

  t1.start()
  t2.start()

```

1. 线程之间的执行是无序的
2. 主线程会等待所有的子线程执行结束再结束
3. 线程之间共享全局变量
4. 线程之间共享全局变量数据出现错误问题
    