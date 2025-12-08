# LoginMe - 用户登录系统

一个基于 FastAPI 和 React 的全栈用户认证系统，实现了用户注册、登录和JWT令牌认证功能。

## 一、环境要件

### 后端环境
- **Python**: 3.12 或更高版本
- **数据库**: SQLite
- **主要依赖**:
  - FastAPI 0.124.0
  - SQLAlchemy 2.0.44
  - python-jose 3.5.0（JWT处理）
  - passlib 1.7.4（密码加密）
  - uvicorn 0.38.0（ASGI服务器）

### 前端环境
- **Node.js**: 25.1.0 或更高版本
- **包管理器**: npm
- **主要依赖**:
  - React 19.2.0
  - React Router DOM 7.10.1
  - Axios 1.13.2
  - Vite 7.2.4（构建工具）

## 二、起动手順

### 1. 后端启动

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 复制env
cp .env.template .env
# 复制后按照自己需求修改env中的环境变量

# 启动后端服务（开发模式，自动重载）
uvicorn main:app --reload

# 后端服务将运行在: http://127.0.0.1:8000
# API文档地址: http://127.0.0.1:8000/docs
```

### 2. 前端启动

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 复制env
cp .env.template .env
# 复制后按照自己需求修改env中的环境变量

# 启动开发服务器
npm run dev

# 前端服务将运行在: http://localhost:5173
```

### 3. 访问应用

打开浏览器访问 `http://localhost:5173` 即可使用应用。

## 三、生成AI使用箇所

本项目在以下方面使用了生成AI辅助开发：

### 1. **代码结构设计**
- 使用AI协助规划整体项目架构
- 后端API端点设计与RESTful规范确认
- 前端路由结构和组件划分建议

### 2. **代码实现**
- **后端**: 
  - JWT令牌生成和验证逻辑（`create_access_token`、`get_current_user`函数）
  - 密码加密和验证机制（使用bcrypt）
  - 数据库模型和Pydantic schema定义

- **前端**:
  - React Router配置和路由保护逻辑
  - API客户端封装（axios配置）
  - 表单验证和错误处理

### 3. **代码优化**
- 从`datetime.utcnow()`迁移到`datetime.now(timezone.utc)`以符合Python 3.12+最佳实践
- 环境变量配置优化（使用dotenv）
- 代码注释和文档生成

### 4. **问题调试**
- JWT令牌过期时间处理问题排查
- CORS配置问题解决
- 数据库连接和会话管理优化

## 四、简单な設計説明

### 确定交互流程

```
1. 用户注册流程:
   用户填写表单 → 前端验证 → POST /api/register → 后端验证邮箱唯一性 
   → 密码哈希化 → 存入数据库 → 返回用户信息

2. 用户登录流程:
   用户填写表单 → 前端验证 → POST /api/login → 后端验证邮箱和密码
   → 生成JWT令牌 → 返回access_token → 前端存储令牌

3. 访问受保护资源:
   前端请求 → 附加JWT令牌（Authorization: Bearer <token>）
   → 后端验证令牌 → 返回用户数据或401错误
```

### 后端设计

#### 技术栈
- **框架**: FastAPI - 现代、快速的Python Web框架，支持异步和自动API文档
- **ORM**: SQLAlchemy - 强大的Python SQL工具包和对象关系映射器
- **认证**: JWT (JSON Web Token) - 无状态的令牌认证机制
- **密码加密**: Bcrypt - 业界标准的密码哈希算法
- **数据验证**: Pydantic - 基于Python类型提示的数据验证

#### 数据库设计
```python
User 表:
- id: Integer (主键)
- email: String (唯一, 索引)
- hashed_password: String (BCrypt加密)
```

#### API接口设计

| 端点 | 方法 | 功能 | 认证要求 |
|------|------|------|----------|
| `/api/register` | POST | 用户注册 | 否 |
| `/api/login` | POST | 用户登录 | 否 |
| `/api/users/me` | GET | 获取当前用户信息 | 是（JWT） |

**详细接口说明:**

1. **POST /api/register**
   - 请求体: `{ "email": "user@example.com", "password": "password123" }`
   - 响应: `{ "id": 1, "email": "user@example.com" }`
   - 错误: 400 - 邮箱已注册

2. **POST /api/login**
   - 请求体: `{ "email": "user@example.com", "password": "password123" }`
   - 响应: `{ "access_token": "eyJ...", "token_type": "bearer" }`
   - 错误: 400 - 用户不存在或密码错误

3. **GET /api/users/me**
   - 请求头: `Authorization: Bearer <token>`
   - 响应: `{ "id": 1, "email": "user@example.com" }`
   - 错误: 401 - 未授权

#### 安全机制
- **密码安全**: 使用Bcrypt算法进行密码哈希，永不存储明文密码
- **令牌过期**: JWT令牌默认30分钟过期，可通过环境变量配置
- **令牌验证**: 每次请求受保护资源时验证令牌签名和过期时间
- **依赖注入**: 使用FastAPI的依赖注入系统实现认证守卫

### 前端设计

#### 技术栈
- **框架**: React 19.2.0 - 现代化的UI库
- **路由**: React Router DOM 7.10.1 - 客户端路由管理
- **HTTP客户端**: Axios - 处理API请求和响应
- **构建工具**: Vite - 快速的前端构建工具

#### 页面结构
```
/login       → 登录页面
/register    → 注册页面
/            → 首页（受保护，需要登录）
```

#### 组件设计
- **LoginPage**: 登录表单，处理用户登录逻辑
- **RegisterPage**: 注册表单，处理用户注册逻辑
- **HomePage**: 受保护的主页，显示用户信息

#### 状态管理
- 使用localStorage存储JWT令牌
- 通过axios拦截器自动在请求头中添加认证令牌
- 401错误时自动跳转到登录页
