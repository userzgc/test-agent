#!/usr/bin/env python3
"""品牌投放H5 后端接口层 场景树素材模块

⚠️ 本脚本不再单独出 XMind 文件。接口层 8 大类已并入 `gen_brandh5_xmind.py`，
   与 PRD 黑盒层合成一份全量 + 一份冒烟（大类名带「【接口】」前缀区分层次）。
   本文件只保留 full_tree / smoke_tree 供导入，改素材后请执行 gen_brandh5_xmind.py。

需求依据：飞书 wiki 技术方案 XCSodigouoAcBZxXhLBcUtCCnut（王晨雨 2026-08-22）
  - 后端本期范围仅两件：附近门店可售接口 + 注册来源枚举写入
  - 口径与推定见 docs/requirements/品牌投放H5_需求分析.md §7.2 / §7.3；评审待修见 §7.4

固定测试数据：
  主数据商品编码 P1001（黄桃果霸）/ P1002（黄桃燕麦酸奶）/ P9999（全库不存在）
  经纬度 113.882300, 22.554100（深圳南山）
  门店 10001 总部旗舰店 0.3km / 10002 科技园店 0.8km / 10003 前海店 1.2km / 10004 宝安店 2.5km / 10005 龙华店 3.1km
  父子门店 20001 万象城主店（子店 20002 一层档口 / 20003 三层档口）
"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))
from gen_xmind import generate_xmind


def L(title, children=None):
    node = {"title": title}
    if children:
        node["children"] = children
    return node


# ============ 完整版场景树（接口层） ============
full_tree = {
    "title": "品牌投放H5-后端接口",
    "children": [

        # ===== 1. 注册来源枚举写入-正向 =====
        L("1.注册来源枚举写入-正向", [
            L("公众号文章来源落库", [
                L("新用户 /v1/app/regByUnionid 携带 registerSource=28"),
                L("注册成功，customer_info.register_source=28（微信公众号文章）"),
            ]),
            L("朋友圈来源落库", [
                L("新用户 regByUnionid 携带 registerSource=29"),
                L("register_source=29（微信朋友圈）"),
            ]),
            L("微博APP来源落库", [
                L("新用户 regByUnionid 携带 registerSource=30"),
                L("register_source=30（微博APP）"),
            ]),
            L("浏览器网页来源落库", [
                L("新用户 regByUnionid 携带 registerSource=31"),
                L("register_source=31（浏览器网页）"),
            ]),
        ]),

        # ===== 2. 注册来源枚举写入-异常边界 =====
        L("2.注册来源枚举写入-异常边界", [
            L("已存在用户不覆盖来源", [
                L("状态正常的老用户（register_source=27 高德）再次 regByUnionid 携带 registerSource=28"),
                L("register_source 仍为 27，不被覆盖"),
            ]),
            L("registerSource 为 null 不写入", [
                L("已有 register_source=29 的用户，本次传 registerSource=null"),
                L("register_source 保持 29，不清空、不置 0"),
            ]),
            L("不传 registerSource 保持既有默认", [
                L("新用户 regByUnionid 不携带 registerSource（方案表格「必填：否」）"),
                L("注册成功；register_source 不写入，为该字段既有默认值"),
            ]),
            L("既有枚举值回归", [
                L("老渠道注册：registerSource=27（高德）"),
                L("register_source=27，新增 28~31 未影响既有取值写入"),
            ]),
        ]),

        # ===== 3. 附近门店接口-正向 =====
        L("3.附近门店接口-正向", [
            L("免登直连返回门店列表", [
                L("未登录态 POST /v4/product-can-sell-near-shop/nearShops，productCode=P1001、113.882300/22.554100"),
                L("@LoginIgnore 生效，HTTP 200 返回 List<ProductCanSellNearShopVo>，无需 token"),
            ]),
            L("返回结构字段完整", [
                L("入参 productCode=P1001（字段名 productCode，语义为主数据商品编码）"),
                L("每店含 productAvailable 与 productId；透传 shopId=10001、shopName=总部旗舰店、distance=0.3km、operationStatus、subShopList"),
                L("productCode 回显 P1001；productId 为接口查到的销售商品ID，各门店可不同"),
            ]),
            L("父店 subShopList 内容正确", [
                L("productCode=P1001 命中父店 20001 万象城主店"),
                L("subShopList 含 20002/20003 两条，每条 shopId、shopName、distance、operationStatus 非空且与门店主数据一致"),
            ]),
            L("默认返回最近3家", [
                L("附近 5 家：10001/10002/10003/10004/10005"),
                L("只返回 10001、10002、10003（取前N家、默认3），按 distance 升序"),
            ]),
            L("门店不足3家全返回", [
                L("附近仅 10001、10002 两家"),
                L("返回 2 家，不报错、不补位"),
            ]),
            L("打烊门店按既有过滤规则", [
                L("10002 科技园店 operationStatus 为休息中"),
                L("是否返回及是否占前3名额，与现有附近门店查询表现一致（同口径回归）"),
            ]),
        ]),

        # ===== 4. 附近门店接口-异常边界 =====
        L("4.附近门店接口-异常边界", [
            L("商品编码为空校验拦截", [
                L("productCode 为空，经纬度 113.882300/22.554100 正常"),
                L("HTTP 200；响应 code 为参数校验失败码（非成功码）、message=「商品编码不能为空」、data=null"),
                L("日志无 product 服务 Feign 调用记录，即校验在查询前拦截"),
            ]),
            L("经度为空校验拦截", [
                L("longitude 为空，productCode=P1001"),
                L("message=「经度不能为空」；code 与商品编码为空一致，data=null"),
            ]),
            L("纬度为空校验拦截", [
                L("latitude 为空，productCode=P1001"),
                L("message=「纬度不能为空」；三条校验的 HTTP 状态码与 code 完全相同，仅 message 不同"),
            ]),
            L("附近无门店返回空列表", [
                L("经纬度取无门店海域 118.000000/20.000000，Redis GEO 查询无结果"),
                L("HTTP 200，data 为空数组 []，不是 null、不是报错"),
            ]),
            L("经纬度 0,0 返回空列表", [
                L("longitude=0、latitude=0（合法坐标，几内亚湾无门店）"),
                L("HTTP 200 + 空数组 []，与无门店同表现"),
            ]),
            L("经纬度超范围返回错误", [
                L("longitude=200、latitude=100（超出 ±180 / ±90）"),
                L("返回参数错误，不返回门店数据、不抛 500"),
            ]),
            L("经纬度类型非法", [
                L("longitude=abc（非 BigDecimal 可解析值）"),
                L("返回参数类型错误提示，不抛未捕获异常、不 500"),
            ]),
            L("经纬度高精度不丢精度", [
                L("longitude=113.8823001234567、latitude=22.5541009876543"),
                L("正常返回门店列表，distance 计算不报错，无精度溢出异常"),
            ]),
        ]),

        # ===== 5. 主数据→销售商品映射与可售状态 =====
        L("5.主数据映射与可售状态-正向", [
            L("主数据有可售销售商品", [
                L("productCode=P1001（10001 有对应上层销售商品且在售）"),
                L("10001 的 productAvailable=true，productId 为该店销售商品ID"),
            ]),
            L("销售商品下架售罄不可售", [
                L("productCode=P1001，10002 对应销售商品已下架/售罄"),
                L("10002 的 productAvailable=false，门店仍在列表中返回"),
            ]),
            L("门店无对应销售商品", [
                L("productCode=P1001，10003 前海店未建对应销售商品"),
                L("10003 的 productAvailable=false"),
            ]),
            L("同一主数据多门店状态各异", [
                L("productCode=P1001 对 10001 在售、10002 售罄、10003 无映射"),
                L("三店 productAvailable 分别为 true/false/false，互不影响"),
            ]),
            L("主数据编码全库不存在", [
                L("productCode=P9999（全库无此主数据商品），经纬度正常"),
                L("不报 500；返回门店列表时各店 productAvailable 均为 false（与「门店无对应销售商品」区分：本条是主数据本身不存在）"),
            ]),
        ]),

        # ===== 6. 可售状态缓存-双重过期 =====
        L("6.可售状态缓存-双重过期", [
            L("缓存命中未过期用缓存", [
                L("shop:available:product:10001 下目标 productId field 存在且 当前-time <= 应用层TTL"),
                L("直接用缓存值，不触发 product 服务 Feign 调用"),
                L("相同入参连续请求两次，第二次返回体与首次完全一致且不再调 Feign"),
            ]),
            L("未命中可售回写 available=1", [
                L("清空 10001 缓存后首次请求 productCode=P1001（该店在售）"),
                L("Feign 查后 HSET 写入 {\"available\":1,\"time\":当前时间戳}"),
                L("二次请求命中缓存，不再调 Feign"),
            ]),
            L("未命中不可售回写 available=0", [
                L("清空 10002 缓存后首次请求 productCode=P1001（该店售罄）"),
                L("同样 HSET 写入且 value.available=0、time 为当前时间戳（available 即状态值本身）"),
                L("二次请求命中缓存返回 false，不再穿透 Feign"),
            ]),
            L("应用层TTL过期重查刷新", [
                L("直接 HSET 目标 field，把 value 中 time 改为 当前时间戳-1小时，保持 Redis Key 未过期"),
                L("本次请求触发 Feign 重查，time 被刷新为当前时间戳"),
                L("无需知道应用层 TTL 具体分钟数即可稳定复现"),
            ]),
            L("Redis 10分钟兜底过期", [
                L("shop:available:product:10001 整个 Key 写入后等待超过 10 分钟"),
                L("Key 自动过期（TTL 到期），下次查询走未命中重建"),
            ]),
            L("单门店多商品field隔离", [
                L("10001 同时缓存 P1001 与 P1002 对应的两个 productId field"),
                L("两个 field 各自独立读写，刷新其中一个不影响另一个的 available 与 time"),
            ]),
        ]),

        # ===== 7. 父子门店可售合并 =====
        L("7.父子门店可售合并", [
            L("任一子店可售则父店可售", [
                L("父店 20001 下 20002 可售 P1001、20003 不可售"),
                L("20001 的 productAvailable=true（任一可售即可售）"),
            ]),
            L("全部子店不可售则父店不可售", [
                L("20002、20003 均不可售 P1001"),
                L("20001 的 productAvailable=false"),
            ]),
            L("父店自身可售子店全不可售", [
                L("20001 本店可售 P1001，20002、20003 均不可售"),
                L("20001 的 productAvailable=true（父店自身可售也计入合并）"),
            ]),
            L("子店各自状态分别正确", [
                L("20002 可售、20003 售罄"),
                L("subShopList 中 20002 的 productAvailable=true、20003 为 false，与父店合并值不相互覆盖"),
            ]),
            L("缓存查询覆盖子门店", [
                L("收集门店ID时含 20002、20003"),
                L("shop:available:product:20002 与 :20003 均参与 HGET/HSET，不遗漏子门店"),
            ]),
        ]),

        # ===== 8. 降级容错 =====
        L("8.降级容错", [
            L("Feign失败置false兜底", [
                L("mock product 服务 Feign 调用失败/超时"),
                L("对应门店 productAvailable=false，门店列表仍返回 10001/10002/10003，不整体 500"),
            ]),
            L("缓存过期刷新失败返回旧值", [
                L("10001 缓存 available=1 但应用层已过期，刷新时 Feign 无响应"),
                L("返回缓存中旧 available=1 对应的 productAvailable=true，且不删除该 field"),
            ]),
        ]),
    ],
}


# ============ 冒烟版场景树（核心 P0） ============
smoke_tree = {
    "title": "品牌投放H5-后端接口-冒烟",
    "children": [
        L("1.注册来源枚举", [
            L("四枚举各落库一次", [
                L("registerSource 分别传 28/29/30/31 各注册一个新用户"),
                L("register_source 分别落 28/29/30/31"),
            ]),
            L("已存在用户不覆盖", [
                L("老用户再带 registerSource=28"),
                L("register_source 保持原值"),
            ]),
        ]),
        L("2.附近门店接口", [
            L("免登返回最近3家", [
                L("未登录传主数据商品ID+经纬度，附近≥5家"),
                L("HTTP 200 返回最近 3 家，含 productId+productAvailable+继承字段"),
            ]),
            L("必填校验与无门店", [
                L("productCode 为空 → HTTP 200 + 参数校验失败 code + message「商品编码不能为空」+ data=null"),
                L("经纬度 118.000000/20.000000 落无门店海域 → HTTP 200 + data=[] 空数组"),
                L("两条均无 500、无未捕获异常"),
            ]),
        ]),
        L("3.可售状态与映射", [
            L("可售/不可售/无映射三态", [
                L("主数据在门店：有在售销售商品 / 已下架售罄 / 无对应销售商品"),
                L("productAvailable 分别为 true/false/false"),
            ]),
            L("父子合并任一可售", [
                L("父门店下任一子门店该商品可售"),
                L("父门店 productAvailable=true"),
            ]),
        ]),
        L("4.缓存与降级", [
            L("命中不查Feign未命中回写", [
                L("field 命中未过期用缓存不调 Feign；未命中 Feign 查后 HSET 回写"),
                L("两条路径结果一致且缓存写入正确"),
            ]),
            L("应用层TTL过期触发刷新", [
                L("HSET 目标 field 把 value 中 time 改为 当前时间戳-1小时，Redis Key 保持未过期"),
                L("本次请求触发 Feign 重查，time 刷新为当前时间戳"),
                L("本期唯一新写的缓存逻辑，必进冒烟"),
            ]),
            L("Feign失败兜底false", [
                L("product 服务 Feign 失败"),
                L("productAvailable=false，门店列表仍返回不整体报错"),
            ]),
        ]),
    ],
}


def main():
    print("本脚本已改为素材模块，不再单独出文件。")
    print("接口层场景树已并入 scripts/gen_brandh5_xmind.py，请执行：python3 scripts/gen_brandh5_xmind.py")


if __name__ == "__main__":
    main()
