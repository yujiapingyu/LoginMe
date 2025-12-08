# LoginMe - 用户登录系统

一个基于 FastAPI 和 React 的全栈用户认证系统，实现了用户注册、登录和JWT令牌认证功能。

## 一、环境要件

### 后端环境
- **Python**: 3.8 或更高版本
- **数据库**: SQLite（开发环境）
- **主要依赖**:
  - FastAPI 0.124.0
  - SQLAlchemy 2.0.44
  - python-jose 3.5.0（JWT处理）
  - passlib 1.7.4（密码加密）
  - uvicorn 0.38.0（ASGI服务器）

### 前端环境
- **Node.js**: 16.x 或更高版本
- **包管理器**: npm 或 yarn
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

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

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
  - FastAPI依赖注入模式实现

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

#### API客户端封装
```javascript
// 统一的API基础URL配置
// 自动附加Authorization头
// 统一错误处理
```

### 项目特点

1. **前后端分离**: 清晰的前后端职责划分，便于独立开发和部署
2. **RESTful API**: 遵循REST架构风格，API设计清晰规范
3. **JWT认证**: 无状态认证机制，易于扩展和负载均衡
4. **类型安全**: 后端使用Pydantic进行数据验证，前端使用TypeScript类型提示
5. **开发友好**: 
   - 后端自动重载（uvicorn --reload）
   - 前端热模块替换（Vite HMR）
   - 自动生成的API文档（FastAPI Swagger UI）

### 未来改进方向

- [ ] 添加邮箱验证功能
- [ ] 实现密码重置功能
- [ ] 添加刷新令牌（Refresh Token）机制
- [ ] 实现用户权限和角色管理
- [ ] 添加单元测试和集成测试
- [ ] 部署到生产环境（Docker + PostgreSQL）
- [ ] 添加速率限制防止暴力破解
- [ ] 实现OAuth第三方登录（Google、GitHub等）

---

**作者**: David Fish  
**日期**: 2025年12月8日  
**版本**: 1.0.0
