“天语” (Weather Whisper) 天气应用产品需求文档 (PRD)

1. 项目概述 (Project Overview)

1.1 产品简介

“天语” (Weather Whisper) 是一款为个人用户设计的、界面简洁、无广告、响应快速的零成本天气查询Web应用。它旨在提供一个纯粹、高效的天气信息获取体验，摒弃商业化天气应用中常见的冗余信息和广告干扰。

1.2 产品定位与目标

目标用户：注重体验、反感广告、有基本天气查询需求的个人用户；寻求实践Web开发技术的开发者。

核心价值：

零成本：所有技术栈和依赖服务均采用免费方案，实现零预算运营。

极速响应：轻量化的前后端设计，确保页面快速加载和数据流畅更新。

纯净体验：无任何形式的广告，界面设计以清晰、直观为第一原则。

个性化：支持用户注册，并管理自己关注的城市列表。

1.3 核心功能列表

用户模块：用户注册、邮箱验证、用户登录/登出。

天气查询：基于地理位置或手动搜索的实时、逐小时、多日天气预报。

城市管理：已登录用户可添加、删除、切换、排序个人关注的城市列表。

1.4 技术与服务栈约束

后端：Flask

前端：Vue.js 3, HTML, CSS

数据库：MySQL

天气数据API：和风天气 (QWeather) - 严格使用免费额度内的API

邮件服务：QQ邮箱 SMTP

2. 功能需求详述 (Functional Requirements)

2.1 用户模块 (User Module)

2.1.1 用户注册 (FR-U-01)

描述：提供一个安全的注册通道，允许新用户创建账户。

输入项：

email: 邮箱地址

password: 密码

confirmPassword: 确认密码

前端校验逻辑 (Client-Side Validation)：

邮箱格式：必须符合标准的邮箱格式 (e.g., user@example.com)。

密码强度：建议至少8位，包含字母和数字。

密码一致性：password 与 confirmPassword 的值必须完全相同。

非空校验：所有字段均为必填项。

后端实现流程：

接收请求：接收前端POST请求，包含 email 和 password。

数据校验：后端再次校验邮箱格式及密码是否为空。查询数据库，确保该邮箱未被注册。

生成Token：若校验通过，生成一个唯一的、加密安全的验证Token (e.g., 使用 uuid.uuid4() 或 secrets.token_urlsafe())。

创建用户记录：在 users 表中插入一条新记录。

存储 email 和密码的哈希值 (password_hash)。严禁明文存储密码！

将 is_verified 设为 FALSE。

存储 verification_token 及其过期时间 token_expiration (当前时间 + 30分钟)。

发送验证邮件：

触发条件：用户记录创建成功后。

SMTP配置:

发件人: lrx8389@qq.com

服务器: smtp.qq.com

端口: 465 (SSL)

授权码: ejznhpxrbtascdbe

邮件内容: 邮件正文需包含一个指向前端验证页面的链接，并附带 verification_token作为URL参数。例如: https://your-domain.com/verify-email?token=THE_GENERATED_TOKEN。

响应前端：向前端返回成功信息，提示用户“注册邮件已发送，请检查收件箱并完成验证”。

2.1.2 邮箱验证 (FR-U-02)

描述：用户通过点击邮件中的链接来激活账户。

实现流程：

用户操作：用户点击邮件中的验证链接。

前端路由：前端应用捕获到 /verify-email 路径，并从URL中解析出 token 参数。

后端验证：前端页面将 token 发送至后端API (e.g., POST /api/verify)。

Token处理：

后端根据收到的 token 在 users 表中查找匹配的用户。

验证成功：如果找到用户，且 token 未过期 (NOW() <= token_expiration)，则：

将该用户的 is_verified 字段更新为 TRUE。

清除 verification_token 和 token_expiration 字段（设为 NULL）。

向前端返回成功状态。

验证失败：如果 token 不存在或已过期，向前端返回失败状态（如“链接无效或已过期”）。

前端反馈：页面根据后端返回结果，向用户显示“验证成功，请登录”或“链接已失效，请重新注册或联系支持”等提示。

2.1.3 用户登录/登出 (FR-U-03)

描述：已验证用户可登录系统，访问个性化功能，并能安全退出。

登录输入项：

email: 邮箱地址

password: 密码

登录流程：

凭据提交：用户在登录页输入邮箱和密码。

后端验证：

后端根据 email 查询 users 表。

若用户存在，则校验提交的 password 与数据库中的 password_hash 是否匹配。

同时检查 is_verified 字段是否为 TRUE。未验证用户应提示先去邮箱验证。

创建会话：验证成功后，为用户创建一个会话。推荐使用JWT (JSON Web Token) 方案：

生成一个包含 user_id 和过期时间的Token。

将此Token返回给前端。

前端处理：前端接收到JWT后，将其存储在 localStorage 或 sessionStorage 中，并在后续所有需要授权的API请求的Header中携带此Token (e.g., Authorization: Bearer <token>)。

登出流程：

用户操作：用户点击“退出”按钮。

前端处理：清除本地存储的JWT。

后端处理（可选）：如果使用JWT黑名单机制，后端可将该Token加入黑名单，使其立即失效。对于简单的零成本项目，仅前端清除即可。

2.2 核心天气功能模块 (Weather Module)

2.2.1 天气展示 (FR-W-01)

描述：展示核心天气数据，数据源严格来自和风天气免费API。

数据内容：

实时天气 (/v7/weather/now)：

当前温度

天气状况文字描述 (如“晴”、“多云”)

天气状况图标 (和风天气提供图标代码，前端需准备对应图标资源)

风向

风力等级

未来24小时逐小时预报 (/v7/weather/24h)：

时间点

温度

天气状况图标

未来7天天气预报 (/v7/weather/7d)：

日期

最高/最低温度

白天/夜间天气状况文字与图标

地理定位 (FR-W-02)：

优先方案：页面加载时，尝试调用浏览器标准的 Geolocation.getCurrentPosition() API获取用户经纬度。

用户授权：浏览器会弹出请求权限的提示，需对用户请求和拒绝两种情况做处理。

失败/拒绝后备方案：若用户拒绝授权或API获取失败，页面应保持默认状态，并清晰地提示用户可以通过顶部的搜索框手动搜索城市。

2.2.2 城市搜索与管理 (FR-W-03)

描述：提供城市搜索功能，并允许登录用户管理个人关注的城市列表。

搜索功能：

API调用：调用和风天气GeoAPI的城市查询接口 (/v7/geo/city/lookup)。

交互：用户在搜索框输入城市名（如“北京”）后，向后端发起请求。后端调用和风API，并将返回的城市列表（可能包含多个同名城市，如“北京市”、“北京区”）透传给前端。

展示：前端以下拉列表或浮层形式展示搜索结果，供用户选择。选择后，页面刷新显示该城市天气。

多城市管理 (登录后功能)：

添加城市：用户搜索并选中一个城市后，旁边显示一个“+”或“关注”按钮。点击后，将该城市信息（城市名、和风城市ID）保存到 user_cities 表。

数量上限：为控制成本和保持界面简洁，每个用户最多可关注 5 个城市。达到上限后，“关注”按钮应置灰或隐藏。

列表展示：在天气详情区域旁，以列表形式展示用户所有已关注的城市。

切换：点击列表中的任一城市，应能快速加载并展示该城市的天气。

删除：列表中每个城市旁都有一个“x”或“删除”图标，点击可从关注列表中移除。

排序（可选优化）：允许用户拖拽调整关注城市的显示顺序。

3. 页面规划与Vue组件设计 (UI/UX & Vue Components)

为最大化开发效率和可维护性，应用界面应高度组件化。

3.1 首页 / 天气详情页 (View: Dashboard.vue)

这是应用的核心视图。



未登录状态：

导航栏 (AppHeader.vue)：包含应用Logo/名称、“登录”、“注册”按钮。

主内容区:

SearchBar.vue：位于页面顶部，用于城市搜索。

CurrentWeather.vue：展示实时天气。

HourlyForecast.vue：展示24小时预报。

DailyForecast.vue：展示7天预报。

已登录状态：

导航栏 (AppHeader.vue)：显示用户邮箱和“退出”按钮。

主内容区:

左侧/主区域：SearchBar.vue, CurrentWeather.vue, HourlyForecast.vue, DailyForecast.vue。

右侧/侧边栏：FavoriteCities.vue 组件，此组件通过 v-if 指令在用户登录后条件渲染。

核心Vue组件详述：

SearchBar.vue:

Props: 无。

Data: searchQuery, searchResults。

Methods: handleSearch() (调用API), selectCity(city) (触发事件，通知父组件更新天气)。

CurrentWeather.vue:

Props: weatherData (包含实时天气信息的对象)。

Responsibility: 纯展示组件，根据传入的 weatherData 渲染UI。

HourlyForecast.vue:

Props: forecastData (包含24小时预报的数组)。

Responsibility: 遍历 forecastData 数组，渲染每个小时的天气卡片。

DailyForecast.vue:

Props: forecastData (包含7天预报的数组)。

Responsibility: 遍历 forecastData 数组，渲染每日天气条目。

FavoriteCities.vue:

Props: 无。

Data: favoriteList。

Responsibility:

在 onMounted 时调用API获取用户关注列表。

渲染列表，并处理切换、删除城市的交互。

当用户添加新城市时，能响应并刷新列表。

3.2 注册页 (RegisterView.vue) & 登录页 (LoginView.vue)

作为独立的页面级组件，由 Vue Router 管理。

内部可复用一个通用的 BaseForm.vue 或 BaseInput.vue 组件来统一表单样式和行为。

使用 v-model 实现表单数据的双向绑定。

在提交按钮的点击事件中，执行前端校验，然后通过 axios (或 fetch) 与后端 /api/register 或 /api/login 端点进行异步通信。

根据API返回结果，执行页面跳转或显示错误信息。

3.3 邮箱验证结果页 (VerificationView.vue)

路由配置: path: '/verify-email'。

逻辑:

在 onMounted 生命周期钩子中，通过 useRoute() (Vue Router 4) 获取URL查询参数 token。

调用后端API，将 token 发送去验证。

Data: verificationStatus (e.g., 'loading', 'success', 'failed'), message。

UI: 根据 verificationStatus 动态显示不同的内容，如加载指示器、“✅ 验证成功，正在跳转到登录页...”或“❌ 链接已失效”。

4. 数据库设计 (Database Schema)

使用MySQL语法，表引擎建议为 InnoDB 以支持外键。

4.1 用户表 (users)

SQL



CREATE TABLE `users` (

  `id` INT AUTO_INCREMENT PRIMARY KEY,

  `email` VARCHAR(128) UNIQUE NOT NULL COMMENT '用户邮箱，作为登录名',

  `password_hash` VARCHAR(255) NOT NULL COMMENT '加盐哈希后的密码',

  `is_verified` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '邮箱是否已验证',

  `verification_token` VARCHAR(255) NULL COMMENT '邮箱验证Token',

  `token_expiration` DATETIME NULL COMMENT '验证Token的过期时间',

  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',

  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

4.2 用户关注城市表 (user_cities)

SQL



CREATE TABLE `user_cities` (

  `id` INT AUTO_INCREMENT PRIMARY KEY,

  `user_id` INT NOT NULL COMMENT '外键，关联到users表的id',

  `city_name` VARCHAR(100) NOT NULL COMMENT '城市名称，用于前端展示，如“深圳”',

  `city_qweather_id` VARCHAR(50) NOT NULL COMMENT '和风天气API的城市ID，用于API查询',

  `display_order` INT NOT NULL DEFAULT 0 COMMENT '显示顺序，数字越小越靠前',

  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

  UNIQUE KEY `uk_user_city` (`user_id`, `city_qweather_id`),

  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`) ON DELETE CASCADE

) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

说明：ON DELETE CASCADE 确保当一个用户被删除时，其所有关注的城市记录也会被自动删除。UNIQUE KEY 防止用户重复添加同一个城市。

5. API 集成要点 (API Integration)

重要安全提示：和风天气的API Key 必须 存储在后端服务器的环境变量中，严禁硬编码在代码中或暴露给前端。所有对和风天气的API请求都应由Flask后端代理发起。

5.1 和风天气 (QWeather) 免费API端点

城市搜索: GET https://geoapi.qweather.com/v2/city/lookup

核心参数: location (用户输入的城市名), key (你的API Key)。

实时天气: GET https://devapi.qweather.com/v7/weather/now

核心参数: location (城市的 city_qweather_id), key。

24小时预报: GET https://devapi.qweather.com/v7/weather/24h

核心参数: location (城市的 city_qweather_id), key。

7天预报: GET https://devapi.qweather.com/v7/weather/7d

核心参数: location (城市的 city_qweather_id), key。

5.2 后端API设计 (Flask Routes)

建议的后端API接口 (前缀 /api)：



POST /api/register - 用户注册

POST /api/login - 用户登录

POST /api/verify - 邮箱Token验证

GET /api/weather/current - 获取指定城市天气 (代理和风API)

参数: city_id

GET /api/cities/search - 搜索城市 (代理和风GeoAPI)

参数: query

GET /api/user/cities - (需授权) 获取用户关注的城市列表

POST /api/user/cities - (需授权) 添加一个关注城市

DELETE /api/user/cities/<city_db_id> - (需授权) 删除一个关注城市