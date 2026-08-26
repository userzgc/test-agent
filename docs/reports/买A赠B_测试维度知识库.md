# 买A赠B 测试维度知识库

```yaml
entry_id: KB-MKT-BUYAGIFTB-001
业务域: 营销中台 / 买A赠B 活动
活动类型码: marketingType = 1301
覆盖版本: 一期（26.6.5 迭代 · 已上线）+ 二期（约束放宽型改造）
生成日期: 2026-08-21
口径优先级: 测试用例 = 技术方案 > 需求PRD
```

## 0. 数据来源与口径裁决

### 0.1 输入源清单

| # | 来源 | 类型 | 采信级别 |
|---|---|---|---|
| S1 | `买A赠B二期_测试用例.xmind`（231 节点） | 测试用例 | 权威 |
| S2 | `买 a 赠 b 一期用例.json`（536 节点） | 测试用例 | 权威 |
| S3 | Confluence 120655361《买A赠B活动 方案设计》 | 技术方案 | 权威 |
| S4 | Confluence 120654652《买A赠B（买指定饮品赠送指定商品/券活动）》 | 需求 PRD | 参考（冲突时不采信） |
| S5 | `买A赠B二期_需求分析.md` | 二次分析 | 参考 |

### 0.2 冲突裁决表（PRD 与用例/技术方案不一致处）

| # | 议题 | PRD（S4）口径 | 采信口径（S1/S2/S3） | 处置 |
|---|---|---|---|---|
| C1 | 赠品商品数量上限 | 5.3「最多添加100个？」/ 三「最多30个商品id」 | 业务上限 **30**（S1、S2）；接口契约声明 `1~100`（S3） | 采信 30；**接口与业务口径不一致，列为 P0 必测** |
| C2 | 活动主商品数量 | 「只能选1个」 | S3 `activityProduct` 明确「仅1个」；S1 存在「多活动商品 → `marketing_obj_rel` 写入2行」 | **权威源自相矛盾，不做裁决**，见「待澄清 Q-A」 |
| C3 | 主商品「是否区分杯型」「是否关联商品标签」字段 | 5.2 有此两字段，必填 | S2 明确「没有是否区分杯型和是否关联商品标签」 | 采信用例：**字段未落地** |
| C4 | 主商品定价模式 | 未提及 | S2 「定价模式：单选枚举，pos价 / 小程序专享价」 | 采信用例：**字段存在** |
| C5 | 寄存券张数 | 5.3「单张券数量默认1，最大10」 | S2「优惠券有且仅能选择一种一张」；S3 `coupons` 券列表「仅1个」 | 采信 **1 张**，PRD 的「最大10」作废 |
| C6 | 活动库存上限 | 未定义 | S3 `stock` 取值 `1~999999` | 采信 `1~999999`（同时解决 S2 中的悬挂问号「100万？6个9」） |
| C7 | 补贴上限 / 固定金额单位 | 「0.00-100」（元） | S3 `subsidyCap` / `fixedAmount` 单位为**分** | 采信「分」，取值域 `0~10000` 分 |
| C8 | 二期主品组合约束 | 一期 PRD 无二期内容 | S1：1组选1 / 1组选多 / 多组 三种均合法 | 采信用例 |
| C9 | 赠品可选商品类型 | 「仅选择单品饮品」 | S1：新增周边商品 `BRAND_MERCH=12` | 采信用例（二期放开） |

---

## 1. 业务链路与状态机

### 1.1 活动单据状态机（OSS 运营中台）

活动有两个正交状态位，测试时必须分别覆盖。

```text
维度A 业务状态 bizStatus（由时间自动推导，不可人工改）
  1=未开始  --(now >= startTime)-->  2=进行中  --(now >= endTime)-->  3=已结束

维度B 启用状态 marketingStatus（人工开关）
  0=禁用  --/oss/buy-a-gift-b/enable-->  1=启用
  1=启用  --/oss/buy-a-gift-b/disable--> 0=禁用

初始态：新建 save / 复制创建 后默认 marketingStatus=0（禁用）
```

### 1.2 活动编辑权限矩阵（S2 权威，字段级）

| 字段 | 进行中 | 已结束 | 禁用 |
|---|---|---|---|
| 活动名称 / 活动头图 / 活动说明 | 可编辑 | 不可 | 可编辑 |
| 活动开始时间 | 不可 | 不可 | 不可 |
| 活动结束时间 | 不可 | 不可 | 可编辑 |
| 活动场景（自提/外卖） | 不可 | 不可 | 不可 |
| 活动主商品 A | 不可 | 不可 | 不可 |
| 赠品商品「添加/删除」 | 不可 | 不可 | 不可 |
| 赠品商品「结算方式」 | 不可 | 不可 | 不可 |
| 赠品商品「排序」 | 不可 | 不可 | 可编辑 |
| 赠品券 添加/删除 | 不可 | 不可 | 不可 |
| 适用/不适用门店 | 不可 | 不可 | 可编辑 |
| 人群标签 | 不可 | 不可 | 可编辑 |
| 单人参与限制 | 不可 | 不可 | 可编辑 |
| 商品标签 / 标签样式 | 不可 | 不可 | 可编辑 |

> 「活动未开始时是否可全量编辑」在 S2 中标记为悬挂问号，当前结论为「不让编辑」→ 见「待澄清 Q-B」。

### 1.3 C端交易主链路（正向）

```text
① 门店菜单  GET /get/{shopId}
     -> marketing.getMenu 拼接 BuyAGiftB 活动分类
     -> buildBuyAGiftBCategories 过滤：初级用户 / V2人群 / 库存

② 点击活动商品（随心配套餐）进入商详
     -> 随心配套餐页【不调用算价接口】

③ 赠品选择页  POST /v2/shop/buy-a-gift-b/for-user/detail
     -> 校验：启用状态、活动时间、适用门店、库存、人群
     -> 返回 BuyAGiftBUserDetailVo（赠品列表 + 寄存券信息）

④ 选择赠品类型 giftType：1=当单立享 / 2=寄存券（无默认选中，必须主动选）
     -> 前端在 products 携带 marketingType=1301, marketingId

⑤ 结算页算价  POST /v3/shoppingCart/settlement/update （isOrder=false）
     -> 主商品 marketingDiscount=0，price=原价
     -> 赠品   marketingDiscount=杯型价格，price=小料价格
     -> setPartedMarketingTypes(1301)
     -> 【不扣库存、不累加参与次数】

⑥ 结算页活动列表  POST /settlement/marketing/list
     -> 命中 partedMarketingTypes=1301 则短路：返回空活动列表
     -> 保留 giftCardDeductVo（礼品卡、钱包余额可用；优惠券不可用）

⑦ 下单  settlement/update（isOrder=true）
     -> DECR marketing_info:stock:{marketingId}
     -> GET/INCR part_times:{customerId}:{marketingId}
     -> SAVE BuyNowPriceModel(transToken) -> order 创单（orderExt 落 buyAGiftBGiftType 等）

⑧ 支付  orderStatus=20（已支付）
     -> order Feign pushOrderInfo -> member
     -> member 发送 MQ TAG_PAY_ORDER_INFO_MX（delayLevel=5，延迟 1 分钟）

⑨ 履约
     giftType=1 当单立享 -> 赠品随单出餐
     giftType=2 寄存券   -> 1 分钟后 DepositCouponConsumer 发券入卡包
```

### 1.4 寄存券子状态机（giftType=2，资损/幂等核心）

```text
[未发放]
   ├─ MQ 延迟 1min 到达 + 未退款 --CouponSender.sendBatch--> [已发放·未核销]
   ├─ 1min 内用户退款            --SET buyagiftb:deposit:refunded:{orderCode}--> [永不发放]
   └─ 发券失败                    --> 抛异常，MQ 重试（最多 16 次）

[已发放·未核销]
   ├─ 用户核销 --> [已核销]
   └─ 用户退款 --> 作废券 --> [已作废] + 允许退款

[已核销]
   └─ 用户退款 --> 拒绝：「赠品券已使用，无法退款」
```

发券 Consumer 判定顺序（**顺序本身即测试点**）：
1. `orderExt.buyAGiftBGiftType == 2`？否则跳过
2. 查 `buyagiftb:deposit:issued:{orderCode}` → 已发放则跳过（幂等）
3. 查 `buyagiftb:deposit:refunded:{orderCode}` → 已退款则跳过发券
4. 获取分布式锁 `lock:buyagiftb:deposit:{customerId}:{marketingId}`，失败则抛异常 MQ 重试
5. 锁内**双重检查**退款标识 + 订单退款状态
6. `hasSendCoupons(requestId)` 防重
7. 发券成功 → SET issued 标识；失败 → 抛异常 MQ 重试

### 1.5 逆向与异常分支矩阵

| # | 触发场景 | 系统行为 | 库存 | 参与次数 | 来源 |
|---|---|---|---|---|---|
| E1 | 下单时活动库存不足 | INCR 回滚库存，抛「活动库存不足」，下单失败 | 回滚 | 未累加 | S3 |
| E2 | 下单时参与次数达上限 | INCR 回滚库存，抛「已达参与上限」，下单失败 | 回滚 | 不变 | S3 |
| E3 | 下单 save 时活动禁用 / 过期 / 库存不足 | 校验拦截，下单失败 | — | — | S2 |
| E4 | 订单算价失败导致 save 失败 | 回滚 | 回滚 | 回滚 | S2 |
| E5 | 订单待支付超时关单 | 回滚 | 回滚 | 回滚 | S2 |
| E6 | order 服务调用超时 | **不回滚活动次数** | 未定义 | 不回滚 | S2 |
| E7 | 支付后 `pushOrderInfo` 失败（mc 服务异常） | 发券直接失败，流程终止，**不自动补发**，走人工 | 不回滚 | 不回滚 | S2 |
| E8 | 内部补贴券库存不足，下单成功后发券失败 | **活动库存不回滚** | 不回滚 | 不回滚 | S2 |
| E9 | 退款时分布式锁获取失败 | 返回「系统繁忙，请稍后重试」，退款失败 | — | — | S3 |
| E10 | 券已发放已核销后退款 | 拒绝退款 | — | — | S3 |
| E11 | 赠品部分退款（1 分钟后管店退款） | 仅退实付金额，**补贴信息不逻辑删除** | — | — | S2 |
| E12 | 赠品全额退款 | `buy_a_gift_b_verify_record` 逻辑删除（`row_state=0`） | — | — | S2 |
| E13 | 二期：多组选齐后取消某件 | 门槛回滚为未达成，赠品入口不可用，按钮文案回退 | — | — | S1 |
| E14 | 二期：赠品选择后取消 | 赠品库存回滚，不产生脏库存 | 回滚 | — | S1 |

> **E5 与 E6 是两个不同场景**：E5 是「订单待支付业务超时关单」，E6 是「Feign 调用 order 服务超时（创单结果未知）」。二者行为相反，是高风险测试点。

---

## 2. 接口契约字典

### 2.1 C端接口

| 接口 | 方法 | 路径 | 变更 |
|---|---|---|---|
| 门店菜单 | GET | `/get/{shopId}` | 改造：拼接活动分类 + 角标 |
| 门店菜单（内部） | POST | `/shop/getMenu` | 改造 |
| 商详页 | — | — | 改造：替换商品角标、是否可参与活动 |
| 查询活动信息 | POST | `/v2/shop/buy-a-gift-b/for-user/detail` | **新增** |
| 结算页算价 | POST | `/v3/shoppingCart/settlement/update` | 改造：新增 `buyAGiftB` 对象 |
| 结算页活动列表 | POST | `/settlement/marketing/list` | 改造：1301 短路 |
| 订单详情 | GET | `/cust/info/{orderCode}` | 改造：解析 orderExt 展示券 |
| 退款 | POST | `/v2/order/refund` | 改造：寄存券退款校验 |

**`/v2/shop/buy-a-gift-b/for-user/detail` 契约**

| 方向 | 字段 | 类型 | 必填 | 取值范围 / 说明 |
|---|---|---|---|---|
| in | `marketingId` | integer | 是 | 活动ID |
| in | `shopId` | integer | 是 | 门店ID |
| in | `orderType` | string | 是 | `1`=堂食 `2`=外卖 |
| out | `marketingId` | integer | — | 活动ID |
| out | `marketingName` | string | — | 活动名称 |
| out | `giftInfo` | string | — | 赠品信息说明（含两种赠品类型） |
| out | `startTime` / `endTime` | string | — | `yyyy-MM-dd HH:mm:ss` |
| out | `marketingImageUrl` | string | — | 活动头图 URL |
| out | `marketingDesc` | string | — | 活动说明 |
| out | `immediateGiftProducts` | `object[]` | — | 当单立享赠品商品列表 |
| out | `depositCoupon` | object | — | 寄存券配置 |

**`/v3/shoppingCart/settlement/update` 增量契约**

| 方向 | 层级 | 字段 | 类型 | 必填 | 取值 |
|---|---|---|---|---|---|
| in | 1 | `buyAGiftB` | object | 否 | 买赠活动参数 |
| in | 2 | `buyAGiftB.giftType` | integer | 是 | `1`=当单立享 `2`=寄存券 |
| in | 2 | `buyAGiftB.marketingId` | integer | 是 | 活动ID |
| out | 1 | `buyAGiftB` | object | 否 | 活动信息 |
| out | 2 | `giftType` | integer | 否 | `1` / `2` |
| out | 2 | `couponInfo` | object | 否 | 寄存券信息 |
| out | 3 | `couponInfo.couponRuleId` | integer | 否 | 券模板ID |
| out | 3 | `couponInfo.couponName` | string | 否 | 券名称 |

> 当单立享的赠品行通过商品详情中 `marketingType=1301` 识别。

### 2.2 OSS 运营中台接口

| 接口 | 方法 | 路径 | 出参 |
|---|---|---|---|
| 创建活动 | POST | `/oss/buy-a-gift-b/save` | boolean |
| 更新活动 | POST | `/oss/buy-a-gift-b/update` | boolean（入参较 save 多 `marketingId`） |
| 活动详情 | GET | `/oss/buy-a-gift-b/detail` | 详情对象（入参 `id` 必填） |
| 活动列表 | POST | `/oss/buy-a-gift-b/list` | 分页对象 |
| 启用 | GET | `/oss/buy-a-gift-b/enable` | boolean |
| 禁用 | GET | `/oss/buy-a-gift-b/disable` | boolean |
| 菜单分类配置 保存 | POST | `/oss/buy-a-gift-b/category-config/save` | boolean |
| 菜单分类配置 查询 | GET | `/oss/buy-a-gift-b/category-config/get` | 配置对象（无入参） |
| OSS 订单详情 | — | — | 新增出参 `buyAGiftBCouponList` |
| 赠品下单数据 | — | — | `marketingId/statDate/orderAmount/orderTurnover/avgOrderPrice` |
| 对账单查询 | — | — | 见 2.4 |
| 对账单导出 | — | — | 走下载中心，`taskType=40` |

### 2.3 `/oss/buy-a-gift-b/save` 字段字典（校验规则的唯一权威表）

| 层 | 字段 | 类型 | 必填 | 取值范围 / 校验 |
|---|---|---|---|---|
| 1 | `marketingName` | string | 是 | 1~30 字符，支持中英文数字符号表情 |
| 1 | `startTime` | string | 是 | 新建时须晚于当前时间 |
| 1 | `endTime` | string | 是 | 须晚于 `startTime` |
| 1 | `marketingImageUrl` | string | 否（PRD 标必填） | JPG/PNG/GIF |
| 1 | `marketingDesc` | string | 否（PRD 标必填） | 1~2000 字符，落 `rule_desc` |
| 1 | `orderType` | string | 是 | 逗号分隔，`1`=堂食 `2`=外卖，至少 1 个 |
| 1 | `stock` | integer | 是 | `1~999999`（饮品与券共享同一活动库存） |
| 1 | `choiceMode` | integer | 是 | `1`=不限 `2`=活动期间X次 `3`=单人单日X次 |
| 1 | `limitNum` | integer | 条件必填 | `choiceMode∈{2,3}` 时必填，`1~100` 正整数 |
| 1 | `shopRangeType` | integer | 是 | `1`=全部 `2`=按区域 `3`=按门店 |
| 1 | `regionIds` / `shopIds` | `integer[]` | 否 | 与 `shopRangeType` 联动 |
| 1 | `excludeShopRangeType` | integer | 否 | `0`=无 `1`=部分门店 |
| 1 | `excludeShopIds` | `integer[]` | 否 | 不适用门店 |
| 1 | `userRangeType` | integer | 否 | `1`=全部 `2`=按人群 `3`=按用户分群(v2) |
| 1 | `userGroupCodes` | string | 否 | 人群 code，逗号分隔 |
| 2 | `activityProduct` | object | 是 | 活动商品（随心配A），契约声明**仅1个** |
| 3 | `activityProduct.productId` | integer | 是 | 必须是随心配套餐商品 |
| 3 | `activityProduct.productName` | string | 否 | — |
| 3 | `immediateEnjoy.products` | `object[]` | 是 | **契约 `1~100`，业务口径 `1~30`（冲突 C1）** |
| 4 | `products[].productId` | integer | 是 | 二期允许 `productType∈{1普通, 12周边}` |
| 4 | `products[].cupId` | integer | 否 | 周边商品无杯型，允许空或 `0` |
| 4 | `products[].price` | integer | 否 | 商品价格（POS 价） |
| 4 | `products[].settlementType` | integer | 是 | `1`=比例结算 `2`=固定金额 |
| 4 | `products[].settlementRatio` | integer | 否 | `0~100`（%），同一商品自动联动 |
| 4 | `products[].subsidyCap` | integer | 否 | 补贴上限，**单位分**，`0~10000` |
| 4 | `products[].fixedAmount` | integer | 否 | 固定结算金额，**单位分** |
| 4 | `products[].sortIndex` | integer | 否 | 越小越前，默认按添加顺序 |
| 3 | `depositCoupon.coupons` | `object[]` | 是 | **仅 1 张** |
| 4 | `coupons[].id` | integer | 是 | 优惠券规则ID |
| 4 | `coupons[].num` | integer | 是 | 奖励数量 |
| 4 | `coupons[].bizType` | integer | 否 | `1`=优惠券 `2`=集采任务 |
| 4 | `coupons[].taskId` | integer | 否 | 任务ID |
| 4 | `coupons[].settlementRatio` | integer | 否 | 结算比例 |

**用例侧补充字段（S2，技术方案未列）**

| 字段 | 取值 | 说明 |
|---|---|---|
| 定价模式 | POS价 / 小程序专享价（单选） | 影响 C端全链路价格展示 |
| 商品标签文案 | 0~14 字符 | 底色默认白，字体默认红 |
| 分组名称（餐单分类） | 0~10 字符 | — |
| 菜单栏展示排序 | `0~100` | 与预存次卡同值时次卡置顶 |
| 分组标签 | 0~14 字符 | — |

### 2.4 错误码矩阵

⚠️ **【待补充】技术方案与 PRD 均未定义错误码（code）**。以下仅为用例/时序图中出现的**提示语**，code 值缺失。

| 触发条件 | 中文提示语 | HTTP/业务码 |
|---|---|---|
| 活动库存不足 | 活动库存不足 | 【待补充】 |
| 参与次数达上限 | 已达参与上限 | 【待补充】 |
| 退款时锁获取失败 | 系统繁忙，请稍后重试 | 【待补充】 |
| 寄存券已核销后退款 | 赠品券已使用，无法退款 | 【待补充】 |
| 主商品信息查询失败（pc info 超时） | 主商品信息查询失败 | 【待补充】 |
| 主品非随心配套餐 | 主品必须是随心配 | 【待补充】 |
| 赠品含 `freeGroup=1` 分组 | 含赠品分组的套餐不可作为赠品 | 【待补充】 |
| 赠品数量超上限 | 赠品数量上限 30 | 【待补充】 |
| 对账查询未填任何条件 | 需要至少一个查询条件 | 【待补充】 |
| C端点「去选择赠品」时不可参与 | 活动库存不足 / 不能参与（toast + 弹窗回菜单） | 【待补充】 |

> **提问建议**：请后端补充 `/oss/buy-a-gift-b/save`、`/v2/shop/buy-a-gift-b/for-user/detail`、`settlement/update` 三个接口的业务错误码枚举（code + message + 是否可重试），否则接口层异常用例只能断言文案、无法断言码值。

### 2.5 幂等与限流

| 项 | 键 / 值 | 说明 |
|---|---|---|
| 发券幂等键 | `buyagiftb:deposit:issued:{orderCode}` | Consumer 入口检查，已发放则跳过 |
| 发券防重键 | `requestId`（`hasSendCoupons(requestId)`） | 锁内二次防重 |
| 退款互斥键 | `buyagiftb:deposit:refunded:{orderCode}` | 退款先于发券时置位，发券侧检查 |
| 发券/退款互斥锁 | `lock:buyagiftb:deposit:{customerId}:{marketingId}`，TTL 5s | 发券与退款共用同一把锁 |
| 算价/下单幂等 | `transToken`（`BuyNowPriceModel`） | 算价结果落 Redis，下单凭 token 取 |
| MQ 重试上限 | 最多 16 次 | `TAG_PAY_ORDER_INFO_MX`，`delayLevel=5`（1 分钟） |
| 限流阈值 QPS | **【待补充】** | 技术方案 §8.3 容量为估算值 |

> **提问建议**：`marketing_info:stock` 的 DECR 是否有并发限流或热点 key 保护？计价接口 QPS 峰值水位是多少（对应二期需求分析 Q6）？

---

## 3. 数据存储映射

### 3.1 核心表

**`buy_a_gift_b_verify_record` — 买A赠B可寄存活动订单核销记录**

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | bigint(20) PK | — |
| `order_code` | varchar(64) NOT NULL | 订单编号 |
| `marketing_id` | bigint(20) NOT NULL | 活动ID |
| `gift_type` | tinyint(4) NOT NULL | `1`=当单立享 `2`=寄存券 |
| `order_channel` | tinyint(4) | `1`APP `2`小程序 `3`POS `4`外卖 |
| `shop_code` | varchar(20) | 门店编码 |
| `shop_name` | varchar(50) | 门店名称 |
| `order_time` / `pay_time` | datetime | 下单 / 支付时间 |
| `discount_amount` | int(11) | 优惠金额，单位分 |
| `subsidy_amount` | int(11) | 补贴金额，单位分 |
| `coupon_source_order_code` | bigint(20) | 优惠券来源订单 |
| `coupon_code` | varchar(255) NOT NULL DEFAULT '' | 券编码 |
| `row_state` | tinyint(4) DEFAULT 1 | `1`有效 `0`无效（全额退款置 0） |
| `created_time` / `modified_time` | datetime | — |

**索引字段（重点）**
- `PRIMARY KEY (id)` BTREE
- `idx_qry_time (order_time, gift_type, order_channel)` — 对账列表默认查近一个月
- `idx_qry_marketing (marketing_id, order_time, gift_type, order_channel)` — 按活动维度查
- `idx_order_code (order_code)` — 订单编号精确查

> ⚠️ 索引缺口：对账查询条件含「补贴门店」，但 `shop_code` 无索引；导出走全表扫描风险，需在大数据量下验证。

**`buy_a_gift_b_stat_day` — 买A赠B活动日统计**

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | bigint(20) PK | — |
| `marketing_id` | bigint(20) NOT NULL | 活动ID |
| `date` | date | 统计日期 |
| `gift_type` | tinyint(4) | 赠品类型 |
| `order_amount` | int(11) DEFAULT 0 | 订单量 |
| `order_turnover` | bigint(20) DEFAULT 0 | 营业额，单位分 |

索引：`idx_qry (marketing_id, date)`

**`marketing_info` — 存量表变更**

```sql
ALTER TABLE `marketing_info`
ADD COLUMN `sent_info` varchar(511) NULL COMMENT '活动库存发放信息' AFTER `valid_type`;
```

### 3.2 大字段（Text/Blob/长 varchar）清单

| 表.字段 | 类型 | 风险 |
|---|---|---|
| `marketing_info.sent_info` | varchar(511) | JSON 结构，定时任务每小时覆写；**长度上限 511 是否够装多赠品发放明细需验证** |
| `marketing_info.rule_desc` | 长文本 | 活动说明最大 2000 字符 |
| `marketing_special_rule`（JSON） | JSON | 存主品组合、多组配置、赠品清单、结算配置；二期多组配置写入此字段（来源 S1） |
| `buy_a_gift_b_verify_record.coupon_code` | varchar(255) | — |

### 3.3 ER 关系

```text
marketing_info (活动主表, marketingType=1301)
  │ 1
  ├─── n ── marketing_obj_rel        (活动-主商品关联；一期1行；二期用例出现2行 → 见 Q-A)
  ├─── 1 ── marketing_special_rule   (JSON：主品组合 + 赠品清单 + 结算配置 + depositCoupon)
  ├─── n ── buy_a_gift_b_verify_record  (marketing_id, 订单核销/分账明细)
  └─── n ── buy_a_gift_b_stat_day       (marketing_id + date, 日统计)

buy_a_gift_b_verify_record.order_code ──> order 服务订单表（跨库，无外键）
buy_a_gift_b_verify_record.coupon_code ─> member 券实例（跨库，无外键）
```

> `marketing_obj_rel` / `marketing_special_rule` 的完整 DDL **【待补充】**（技术方案只给了 2 张新表 + 1 处 ALTER）。
> **提问建议**：请补充这两张存量表在买A赠B场景下的字段用法与 JSON schema，否则 DB 断言只能靠人工查库。

### 3.4 缓存层（Redis）

| 服务 | Key 模板 | 数据结构 | TTL | 更新策略 | 用途 | 来源 |
|---|---|---|---|---|---|---|
| member | `buyagiftb:deposit:refunded:{orderCode}` | String | 5 min | Write-Through（退款时写） | 退款标识，发券前检查 | S3 |
| member | `buyagiftb:deposit:issued:{orderCode}` | String | 5 min | Write-Through（发券成功后写） | 发券幂等 + 退款前检查 | S3 |
| member | `lock:buyagiftb:deposit:{customerId}:{marketingId}` | 分布式锁 | 5 s | 显式加解锁 | 发券与退款互斥 | S3 |
| marketing | `marketing_info:stock:{marketingId}` | String（计数） | **【待补充】** | Redis 为权威计数（DECR/INCR），DB 由定时任务每小时回写 → Write-Behind | 活动库存 | S3/S2 |
| marketing | `part_times:{customerId}:{marketingId}` | String（计数） | **【待补充】** | INCR，失败回滚 | 用户参与次数 | S3/S2 |
| marketing | 活动配置缓存（key 未披露） | 未披露 | **5 s** | Cache-Aside | 配置变更后 5s 生效窗口 | S1/S5 |

> ⚠️ **TTL 缺口是高危项**：`marketing_info:stock` 与 `part_times` 未给 TTL。
> - `part_times` 若 `choiceMode=3`（单人单日X次），TTL 必须精确到自然日 24:00，否则跨日次数不清零 = 用户少参与；TTL 过短则次数被重置 = 超发资损。
> - `stock` 若 TTL 早于活动结束时间，key 过期后库存计数丢失 = 无限超发。
> **提问建议**：请后端明确这两个 key 的 TTL 与过期后的重建逻辑（是否回源 DB `sent_info`）。

### 3.5 数据一致性关键点

- **库存池归并**：同一商品名称的多个 productId（如「冰鲜柠檬水」4 个 ID）共享 1 个活动库存；修改任一行库存，同组自动联动。结算方式与排序各行独立配置。
- **饮品库存 与 券库存 独立**，OSS 列表每小时更新一次（依赖 `buyAGiftBGiftSentCountSyncJob`）。
- **已下单订单按下单时配置分账**，不随活动后续修改变化（S1）。

---

## 4. 拓扑与依赖

### 4.1 依赖分级

**核心强依赖（失败即阻断主流程）**

| 依赖 | 交互方式 | 失败影响 |
|---|---|---|
| `marketing`(msc) 营销服务 | Feign / 内部调用 | 活动查询、算价、库存扣减全部不可用 |
| `product`(pc) 商品中心 | Feign `batchGetShopProduct` / `info` | 赠品信息缺失；**`freeGroup` 字段回填错误将导致白嫖资损** |
| `order` 订单服务 | Feign 创单 / 退款 | 不可下单 |
| `member` 会员服务 | Feign `pushOrderInfo`、券发放 | 寄存券不发放（且**不自动补发**） |
| Redis | 库存 DECR / 参与次数 / 分布式锁 | 下单直接失败；锁不可用则退款失败 |
| 扫呗（第三方支付/分账） | 立减金营销账单 / 内部补贴券营销 | 分账失败，财务对账不平 |

**非核心弱依赖（失败降级，不阻断下单）**

| 依赖 | 交互方式 | 失败影响 |
|---|---|---|
| RocketMQ `TAG_PAY_ORDER_INFO_MX` | 延迟消息（`delayLevel=5`，1 min） | 寄存券延迟发放；最多重试 16 次 |
| elasticjob `buyAGiftBGiftSentCountSyncJob` | cron `0 0 0/1 * * ?`（每小时） | OSS 列表库存数字不刷新 |
| elasticjob `buyAGiftBVerifyRecordDayStatJob` | cron `0 0 1 * * ?`（每日 01:00） | 数据页日统计缺失 |
| 下载中心（`taskType=40`） | 异步导出 | 对账单无法导出 |
| pc 商品选择器 `listProductCups`（二期加 `productTypes`） | 同步 | 后台无法按周边商品筛选 |

配置来源：Nacos `Data ID: mc-task-prod.yaml` / `Group: DEFAULT_GROUP`，两个 job 均 `shardingTotalCount=1`、`failover=true`、`monitorExecution=true`。

### 4.2 超时配置

⚠️ **【待补充】** 技术方案未列出任何 ConnectTimeout / ReadTimeout。

| 调用链 | ConnectTimeout | ReadTimeout | 状态 |
|---|---|---|---|
| ssos → marketing | — | — | 【待补充】 |
| marketing → pc（`batchGetShopProduct` / `info`） | — | — | 【待补充】 |
| order → member（`pushOrderInfo`） | — | — | 【待补充】 |
| member → 扫呗 | — | — | 【待补充】 |
| 应用 → Redis | — | — | 【待补充】 |

> 用例 S5-S13「pc info 超时 → 主商品信息查询失败拒绝保存」依赖明确的超时阈值才能构造。
> **提问建议**：请提供上述 5 条链路的超时配置及超时后的降级策略（是拒绝保存，还是放行？当前用例假设是「拒绝保存」，需确认）。

---

## 5. 测试资产生成

### 5.1 数据工厂配方（构造最短路径）

**配方 A — 测「当单立享下单分账」**
```text
1. OSS 建活动：主品=随心配套餐A(1组1件)，赠品=普通饮品×1，settlementType=1，ratio=100，stock=999
2. GET /oss/buy-a-gift-b/enable 启用；等待 startTime 到达（或直接建即时生效活动）
3. C端：GET /get/{shopId} 确认活动分类出现
4. POST /v2/shop/buy-a-gift-b/for-user/detail 拿赠品列表
5. POST settlement/update（isOrder=false, buyAGiftB.giftType=1）算价
6. POST settlement/update（isOrder=true）下单 → 支付
7. 查 buy_a_gift_b_verify_record（gift_type=1, subsidy_amount）
前置依赖：随心配套餐商品、门店在适用范围、用户在人群范围内
```

**配方 B — 测「寄存券退款」（必须卡 1 分钟窗口）**
```text
配方A 步骤1-2，但赠品配 depositCoupon（1 张券）
→ 下单，giftType=2 → 支付
→ 【分支1 券未发放】支付后 60s 内发起 /v2/order/refund
     期望：SET buyagiftb:deposit:refunded:{orderCode}，退款成功，券永不发放
→ 【分支2 券已发放未核销】等待 >60s 后退款
     期望：券作废，退款成功
→ 【分支3 券已核销】>60s + 核销券后退款
     期望：拒绝「赠品券已使用，无法退款」
提速手段：调低 MQ delayLevel 或直接构造 Redis 标识位
```

**配方 C — 测「二期周边赠品分账 6 种模式」**
```text
1. 准备周边商品 SKU（productType=12，无杯型，基础价 50 元）
2. 同一活动配 6 个赠品行，分别设 6 种结算配置：
   ①无补贴 ②固定3元 ③比例100%无上限 ④比例90%+上限10元(未达)
   ⑤比例90%+上限10元(已达) ⑥补贴9元 vs 现价5元
3. 每种模式各下单 1 笔 → 支付 → 查 verify_record.subsidy_amount
4. 各退款 1 笔 → 查冲正金额
最短路径：一个活动内配 6 行赠品，一次配置跑完 12 个断言（6下单 + 6退款）
```

**配方 D — 测「库存超发 / 并发」**
```text
1. 建活动 stock=10，choiceMode=2（活动期间 2 次）
2. 50 并发线程下单 → 期望成功 10、失败 40（marketing_info:stock 归零不为负）
3. 单用户 5 并发 → 期望成功 2、失败 3，失败时库存回滚
```

**配方 E — 测「freeGroup 白嫖拦截」（资损）**
```text
1. 商品侧准备一个含 freeGroup=1 分组的随心配套餐
2. OSS 尝试将其配为赠品 → 期望保存被拦截
3. 反向验证：mock pc info 返回 freeGroup=0 → 拦截失效，可白嫖（证明拦截完全依赖该字段）
```

### 5.2 用例优先级建议

**P0 — 核心逻辑 / 资损防线（必须 100% 覆盖）**

| 域 | 场景 |
|---|---|
| 资损 | 6 种结算模式 × {普通赠品, 周边赠品} × {下单, 退款} = 24 组分账断言 |
| 资损 | 结算金额不超过优惠金额（现价5元 vs 补贴9元 → 取5元） |
| 资损 | `freeGroup=1` 套餐作为赠品被拦截 |
| 资损 | 活动库存并发不超发；参与次数并发不超限 |
| 状态机 | 寄存券三分支退款（未发放 / 已发放未核销 / 已核销） |
| 状态机 | 发券幂等（重复投递 MQ 不重复发券） |
| 配置 | 主品三种组合（1组选1 / 1组选多 / 多组）保存成功 |
| 配置 | 赠品选周边商品 `productType=12` 保存成功；筛选「全部/周边商品」正确 |
| 算价 | 三种主品组合的门槛达成判定；赠品价格=0 |
| 算价 | 小程序专享价 × 买A赠B 全组合实付价 |
| 兼容 | 一期存量「买1赠1」活动全链路回归 |
| 兼容 | 寄存券链路零改动回归 + 不可配周边 |

**P1 — 异常处理 / 边界**

| 域 | 场景 |
|---|---|
| 异常 | 库存不足 / 参与次数达上限 / 活动禁用过期的拦截与回滚 |
| 异常 | pc info 超时 → 拒绝保存 |
| 异常 | `pushOrderInfo` 失败 → 发券失败不补发 |
| 异常 | 退款锁获取失败 → 系统繁忙 |
| 边界 | 赠品数量 1 / 30 / 31（31 应拦截） |
| 边界 | 活动库存 1 / 999999 / 1000000 |
| 边界 | `limitNum` 0 / 1 / 100 / 101 |
| 边界 | 活动名称 0 / 1 / 30 / 31 字符；活动说明 2000 / 2001 |
| 边界 | 缓存 5s 窗口期内旧配置仍生效 |
| 展示 | 多商品 >3 个折叠「展开全部 / 收起更多」；按钮文案切换 |
| 展示 | 周边赠品图片 404 兜底图 |
| 数据 | 全额退款 / 部分退款后的日统计与对账数据 |

**P2 — 兼容性 / 多端**
- 微信小程序 / 支付宝小程序 / iOS / Android 四端展示一致性
- 分类排序（预存次卡 vs 买A赠B 同排序值时次卡置顶）
- POS 小票展示（赠品商品显示活动优惠；赠品券不显示）

---

## 6. 质量基线

⚠️ **【待补充】—— 需求文档、技术方案、用例三份材料中均无任何性能指标与覆盖率目标。**

| 指标类型 | 目标值 | 状态 |
|---|---|---|
| 接口响应时间（算价 `settlement/update`） | — | 【待补充】 |
| 接口响应时间（`for-user/detail`） | — | 【待补充】 |
| 计价链路 QPS 峰值承载 | — | 【待补充】（技术方案 §8.3 为估算） |
| 行覆盖率 / 分支覆盖率目标 | — | 【待补充】 |
| 寄存券发放时延 SLA | 名义 1 分钟（MQ `delayLevel=5`） | 未定义超时告警阈值 |
| 分账金额异常告警阈值 | 用例提及「分账金额异常监控触发」 | 阈值【待补充】 |
| 对账兜底 | 上线后 7 日抽样对账 | 抽样比例与责任人【待补充】 |
| 活动生效率指标水位 | — | 【待补充】 |

> **提问建议（按紧急度）**
> 1. 算价接口 P99 响应时间目标是多少？大促峰值 QPS 是多少？——决定是否需要压测，以及压测通过线。
> 2. 「分账金额异常监控」的具体阈值和告警通道是什么？——这是周边赠品（单价 50 元 vs 饮品 8 元）补贴放大的唯一自动防线。
> 3. 本次迭代是否有单测覆盖率准入要求？如无，是否接受 0 单测直接提测？

---

## 7. 变更影响雷达

### 7.1 一期变更（新增能力）

| 变更项 | 类型 | 受影响接口 |
|---|---|---|
| 新增 `buy_a_gift_b_verify_record` | 建表 | 对账单查询、对账单导出、OSS 订单详情、退款（逻辑删除） |
| 新增 `buy_a_gift_b_stat_day` | 建表 | 赠品下单数据、活动数据页 |
| `marketing_info` 新增 `sent_info` 列 | **DDL 改存量表** | `/oss/buy-a-gift-b/list`（库存展示）、`/oss/buy-a-gift-b/detail`、`buyAGiftBGiftSentCountSyncJob`，以及**所有读 `marketing_info` 的存量营销活动接口**（需回归 SELECT * 场景） |
| `orderExt` 新增 `buyAGiftBGiftType` / `buyAGiftBMarketingId` / `depositCouponRuleId` | 订单扩展字段 | `/cust/info/{orderCode}`、`/v2/order/refund`、`pushOrderInfo`、OSS 订单详情 |
| 结算页 1301 短路 | 逻辑改造 | `/settlement/marketing/list`、`availableCouponsNew`（后端保留兜底短路） |
| 下载中心新增 `taskType=40` | 枚举扩展 | 下载中心列表、导出任务调度 |

### 7.2 二期变更（约束放宽）

| 变更项 | 代码落点 | 受影响接口 |
|---|---|---|
| 移除主品「1组 + 每组选1」硬约束 | `marketing/msc` `validateMainProductType` | `/oss/buy-a-gift-b/save`、`/update` |
| 新增「含 `freeGroup=1` 分组不可保存」拦截 | `validateMainProductType` 新增遍历 | `/oss/buy-a-gift-b/save`、`/update`（**新增对 pc `info` 接口的强依赖**） |
| 门槛判定改 `containsAll` 覆盖语义 | `BuyAGiftBRuleRunner.satisfyDiscountCondition` | `settlement/update`（算价 + 下单双路径） |
| 赠品类型放开 `BRAND_MERCH=12` | `validateGiftProductTypes` | `/oss/buy-a-gift-b/save`、`/for-user/detail`、`settlement/update` |
| ssos 赠品选择器新增 `productTypes` 参数 | ssos → pc `listProductCups` | 后台赠品选择弹窗（**可能需 pc 二方包配合发版**） |
| 周边商品进入分账链路 | 代码零改动 | 扫呗立减金营销账单、`buy_a_gift_b_verify_record.subsidy_amount`、对账单、退款冲正 |

**发布顺序约束**：`msc` 必须先于 `ssos` 发布。若顺序颠倒，会出现「后台已能筛出周边商品，但保存时 msc 仍拦截赠品类型」的不可用窗口。

### 7.3 未改动但需回归的链路（零改动 ≠ 零风险）

- 寄存券（下次使用）发券 / 核销 / 退款全链路 —— 代码零改动，但受主品组合放宽影响
- `ShoppingCartServiceImpl` 随心配多组解析 —— 声称已通用遍历 `comboGroups`
- `applyMainProductExclusivePrice` 专享价 —— 声称已循环全部主商品，**无需改但必测**
- 一期存量「买1赠1」活动 —— `containsAll` 在单商品下等价原 `size()==1`

---

## 8. 待澄清问题（阻塞用例设计）

| # | 问题 | 冲突来源 | 影响 | 建议责任人 |
|---|---|---|---|---|
| Q-A | **活动主商品到底能配几个？** 技术方案 `activityProduct` 明确「仅1个」，但二期用例存在「多活动商品 → `marketing_obj_rel` 写入2行」「选齐所有主品才可选赠品」整组场景 | S1 vs S3（两个权威源互斥） | 若实际仅支持 1 个，二期用例中「多活动商品门槛」整组场景需作废；若支持多个，则接口契约与门槛判定逻辑均需重新确认 | 营销后端 + 产品 |
| Q-B | 活动「未开始」状态是否可编辑？ | S2 标记为悬挂问号，暂定「不让编辑」 | 影响 1.2 权限矩阵一整列 | 产品 |
| Q-C | 赠品数量上限 30 还是 100？接口 `@Size` 是否已按 30 收口 | C1（业务 30 vs 契约 100） | 若接口仍放 100，前端限 30 = 可绕过前端直接调接口配 100 个赠品 | 营销后端 |
| Q-D | `marketing_info:stock` / `part_times` 的 Redis TTL 及过期重建逻辑 | 技术方案未披露 | 直接决定超发资损与跨日清零正确性 | 营销后端 |
| Q-E | 各服务间超时配置（5 条链路） | 技术方案未披露 | 无法构造超时用例，无法验证降级行为 | 营销后端 + 运维 |
| Q-F | 全套业务错误码枚举 | 技术方案未披露 | 异常用例只能断言文案 | 营销后端 |
| Q-G | 性能基线与覆盖率准入 | 三份材料均无 | 无质量门禁 | 产品 + 研发负责人 |
| Q-H | `marketing_obj_rel` / `marketing_special_rule` 在本场景下的字段用法与 JSON schema | 技术方案未给 DDL | DB 层断言只能人工查库 | 营销后端 |
| ORDER-07 | 关联商品不在该门店餐单中（历史悬挂项） | 待产品确认 | 用例中标记为悬挂 | 产品 |

---

## 9. 深度测试点 Top 3（最可能遗漏）

### 🔴 深度测试点 1：寄存券「退款标识 5min TTL」与「MQ 重试 16 次」的时间窗错配

**为什么会漏**：所有用例都只测「1 分钟内退款」和「1 分钟后退款」两个点，没人测 **5 分钟之后**。

**风险推演**：
- `buyagiftb:deposit:refunded:{orderCode}` 的 TTL 只有 **5 分钟**；
- 而发券 MQ 消费失败后最多重试 **16 次**，退避重试的总时长完全可能超过 5 分钟；
- 一旦重试跨过 5 分钟，退款标识已过期消失，Consumer 第 3 步「检查退款标识」查不到 → 判定为未退款 → **给一个已经全额退款的订单补发了寄存券**；
- `issued` 标识同样 5min TTL，此时也已过期，幂等防线一并失效。

**构造方法**：下单支付 → 立即退款（置位 refunded）→ 人为让首次发券消费失败（如 mock `CouponSender` 抛异常）→ 让 MQ 重试链路持续超过 5 分钟 → 观察第 N 次重试是否发券成功。

**期望**：不应发券。若发券成功，说明退款标识必须改为**持久化到 DB 或 TTL 延长至覆盖 MQ 最大重试窗口**。

---

### 🔴 深度测试点 2：`marketing_info.sent_info` varchar(511) 溢出导致库存统计静默失真

**为什么会漏**：这个字段是一期 ALTER 加的，没有任何用例覆盖；且它由每小时定时任务写入，出错时**不报错、不影响下单**，只让 OSS 列表的库存数字慢慢变错。

**风险推演**：
- `sent_info` 存「活动库存发放信息」，长度上限 511 字符；
- 二期赠品可配到 **30 个**（普通 + 周边混配），若该 JSON 按赠品维度记录发放明细（如 `{"productId":发放数}`），30 个赠品 ID（`8~10` 位）+ 计数 + JSON 符号 ≈ `450~600` 字符，**贴着甚至越过 511 上限**；
- MySQL 非严格模式下超长会**静默截断** → JSON 破损 → 下一次 job 解析失败或写入脏数据；
- 表现为 OSS 活动列表「饮品库存 / 券库存」显示错误，运营据此误判是否加库存 → 超卖或提前下架。

**构造方法**：配一个 30 个赠品的活动（productId 取 10 位长 ID），跑 `buyAGiftBGiftSentCountSyncJob`，直接查库看 `sent_info` 实际长度与 JSON 完整性；同时验证 MySQL `sql_mode` 是否含 `STRICT_TRANS_TABLES`。

**期望**：字段长度足以容纳 30 赠品场景，或 job 有截断保护 + 告警。

---

### 🔴 深度测试点 3：活动配置缓存 5 秒窗口 × 已下单订单分账口径的交叉污染

**为什么会漏**：用例把这两件事分开测了 —— 「缓存 5s 后新配置生效」（P1，S1 第 2 章）和「已下单订单按下单时配置分账，不随活动修改变化」（S1 第 2 章）。**没有人测它们的交叉点**。

**风险推演**：
- 运营在 T0 把某赠品结算比例从 90% 改成 100%；
- T0~T0+5s 窗口内，部分应用节点仍持旧配置（90%），部分已刷新（100%）；
- 用户在窗口内下单：**算价节点**读到 90%，**下单/落 `verify_record` 节点**读到 100%（或反之）；
- 结果：`discount_amount` 与 `subsidy_amount` 来自两份不同配置 → 单笔订单内部口径不自洽 → 传给扫呗的补贴金额与订单优惠金额对不上 → **财务对账不平，且事后无法从任何一份配置快照复现**；
- 更隐蔽的是退款冲正：退款时若再读一次配置，冲正金额可能与下单分账金额不等，形成**永久性长短款**。

**构造方法**：脚本在修改配置的同一秒内持续并发下单（20 QPS 打满 5 秒窗口），事后逐笔比对 `verify_record.discount_amount / subsidy_amount` 与两份配置的对应关系，检查是否存在混合口径的订单；再对这些订单全额退款，比对冲正金额。

**期望**：分账金额必须在下单时**快照固化**（写入 `verify_record` 或订单扩展），退款冲正只读快照，不再回读活动配置。若实现是回读配置，这是一个必须在上线前修掉的资损缺陷。

---

> 本条目由需求文档 + 技术方案 + 一期/二期测试用例交叉抽取生成。
> 凡标注 **【待补充】** 处均为原始材料确实缺失，未做任何推测填充。
