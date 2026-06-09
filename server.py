from copy import deepcopy
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="AI 报告工作台模拟服务")

BASE_DIR = Path(__file__).resolve().parent

states = {}


def get_state(session_id):
    if session_id not in states:
        states[session_id] = {"outline": None, "confirmed": False, "report": None, "phase": "outline", "history": []}
    return states[session_id]


REPORT_FIXTURES: list[dict[str, Any]] = [
    {
        "id": "r-2026-q2",
        "title": "2026 Q2 智能经营分析报告",
        "date": "2026-06-05",
        "owner": "战略分析组",
        "status": "已生成",
        "summary": "聚焦收入增长、客户结构与风险提示。",
        "metrics": [
            {"label": "收入规模", "value": "¥8,420万"},
            {"label": "同比增长", "value": "+18.6%"},
            {"label": "风险事项", "value": "5项"},
        ],
        "tags": ["经营分析", "季度复盘", "董事会材料"],
        "boundData": [
            {
                "title": "经营数据",
                "children": [
                    {"title": "销售收入明细", "bound": True},
                    {"title": "区域渠道贡献", "bound": True},
                    {"title": "重点客户续约率", "bound": True},
                ],
            },
            {
                "title": "财务数据",
                "children": [
                    {"title": "成本费用结构", "bound": True},
                    {"title": "现金流预测", "bound": False},
                    {"title": "毛利率拆解", "bound": True},
                ],
            },
            {
                "title": "外部数据",
                "children": [
                    {"title": "行业景气指数", "bound": False},
                    {"title": "竞品价格监测", "bound": True},
                ],
            },
        ],
        "chat": [
            {"role": "user", "text": "请基于已绑定的数据生成一份经营分析报告。"},
            {"role": "assistant", "text": "已读取销售、财务与竞品监测数据，建议报告采用“整体表现—结构拆解—风险建议”的叙事结构。"},
            {"role": "user", "text": "风险提示需要突出现金流和大客户集中度。"},
            {"role": "assistant", "text": "已将现金流预测缺口、大客户续约波动纳入风险章节，并在详情预览中增加行动建议。"},
        ],
        "outline": [
            {"title": "一、执行摘要", "points": ["核心结论", "关键指标变化", "管理层关注事项"]},
            {"title": "二、经营表现", "points": ["收入规模与增长", "区域渠道贡献", "客户结构变化"]},
            {"title": "三、财务与风险", "points": ["成本费用结构", "现金流压力", "大客户集中度"]},
            {"title": "四、行动建议", "points": ["短期跟进事项", "中期优化方向", "指标监控机制"]},
        ],
        "detail": {
            "lead": "本季度公司收入保持双位数增长，核心区域延续高景气，但费用投入节奏和大客户续约不确定性需要持续跟踪。",
            "sections": [
                {
                    "title": "经营表现",
                    "content": "Q2 收入达到 ¥8,420 万，同比增长 18.6%。华东与华南渠道合计贡献 63% 的新增收入，其中企业级客户套餐升级是主要拉动因素。",
                },
                {
                    "title": "风险提示",
                    "list": [
                        "现金流预测数据尚未完全绑定，建议补齐未来 12 周回款计划。",
                        "前五大客户收入占比升至 41%，续约波动可能影响下季度确认收入。",
                        "竞品在中端产品线出现价格下探，需要评估促销策略与毛利影响。",
                    ],
                },
                {
                    "title": "建议动作",
                    "content": "建议将重点客户续约、费用使用率和现金回款纳入周度追踪看板，并由销售、财务、运营共同维护数据口径。",
                },
            ],
        },
    },
    {
        "id": "r-market",
        "title": "新能源行业洞察报告",
        "date": "2026-05-28",
        "owner": "行业研究组",
        "status": "草稿",
        "summary": "分析政策变化、供需结构与竞品动态。",
        "metrics": [
            {"label": "政策事件", "value": "12条"},
            {"label": "样本企业", "value": "36家"},
            {"label": "机会方向", "value": "4类"},
        ],
        "tags": ["行业洞察", "新能源", "竞品跟踪"],
        "boundData": [
            {
                "title": "政策数据",
                "children": [
                    {"title": "地方补贴政策", "bound": True},
                    {"title": "出口关税变化", "bound": False},
                ],
            },
            {
                "title": "市场数据",
                "children": [
                    {"title": "装机量月度趋势", "bound": True},
                    {"title": "头部企业产能", "bound": True},
                    {"title": "竞品发布节奏", "bound": False},
                ],
            },
        ],
        "chat": [
            {"role": "assistant", "text": "当前报告处于草稿阶段，可继续绑定出口关税和竞品发布数据。"}
        ],
        "outline": [
            {"title": "一、行业摘要", "points": ["政策窗口", "供需结构", "价格趋势"]},
            {"title": "二、竞争格局", "points": ["头部企业产能", "新品发布", "渠道策略"]},
            {"title": "三、机会判断", "points": ["短期机会", "中期变量", "跟踪指标"]},
        ],
        "detail": {
            "lead": "新能源行业需求仍保持韧性，但政策补贴节奏、出口关税和竞品新品周期会影响短期订单释放。",
            "sections": [
                {"title": "市场趋势", "content": "装机量月度趋势显示需求高峰后移，头部企业继续扩充高端产能。"},
                {"title": "待补数据", "list": ["出口关税变化尚未绑定。", "竞品发布节奏需要补充最近 30 天样本。"]},
            ],
        },
    },
    {
        "id": "r-customer",
        "title": "企业客户满意度分析",
        "date": "2026-05-18",
        "owner": "客户成功部",
        "status": "已归档",
        "summary": "梳理 NPS、续约意向和服务响应效率。",
        "metrics": [
            {"label": "NPS", "value": "62"},
            {"label": "续约意向", "value": "78%"},
            {"label": "响应时长", "value": "2.4h"},
        ],
        "tags": ["客户成功", "满意度", "续约"],
        "boundData": [
            {"title": "客户反馈", "children": [{"title": "NPS 问卷", "bound": True}, {"title": "访谈纪要", "bound": True}]},
            {"title": "服务工单", "children": [{"title": "响应效率", "bound": True}, {"title": "升级工单", "bound": False}]},
        ],
        "chat": [{"role": "assistant", "text": "已归档报告可查看详情，也可以发送问题生成补充建议。"}],
        "outline": [
            {"title": "一、满意度概览", "points": ["NPS", "核心正负反馈"]},
            {"title": "二、续约因素", "points": ["价值感知", "服务体验", "价格敏感度"]},
        ],
        "detail": {
            "lead": "企业客户整体满意度稳定，服务响应体验是影响续约意向的关键变量。",
            "sections": [
                {"title": "关键发现", "content": "NPS 达到 62，续约意向为 78%，但升级工单的处理体验仍需改善。"},
                {"title": "建议", "list": ["建立重点客户专属响应机制。", "补齐升级工单闭环数据。"]},
            ],
        },
    },
    {
        "id": "r-risk",
        "title": "供应链风险月报",
        "date": "2026-04-30",
        "owner": "运营管理部",
        "status": "已生成",
        "summary": "追踪供应商交付、库存安全线与成本波动。",
        "metrics": [
            {"label": "风险供应商", "value": "7家"},
            {"label": "安全库存", "value": "19天"},
            {"label": "成本波动", "value": "+6.2%"},
        ],
        "tags": ["供应链", "风险", "月报"],
        "boundData": [
            {"title": "供应商", "children": [{"title": "交付准时率", "bound": True}, {"title": "质量异常", "bound": True}]},
            {"title": "库存", "children": [{"title": "安全库存线", "bound": True}, {"title": "成本价格曲线", "bound": True}]},
        ],
        "chat": [{"role": "assistant", "text": "供应链风险月报已生成，可继续追问具体供应商或库存策略。"}],
        "outline": [
            {"title": "一、风险概览", "points": ["供应商风险", "库存风险", "成本风险"]},
            {"title": "二、处置建议", "points": ["替代供应商", "安全库存", "采购节奏"]},
        ],
        "detail": {
            "lead": "供应链整体可控，但部分供应商交付稳定性下降，关键物料安全库存需要上调。",
            "sections": [
                {"title": "风险概览", "content": "7 家供应商进入风险观察名单，关键物料安全库存约 19 天。"},
                {"title": "处置建议", "list": ["启动二供报价。", "对高波动物料建立周度采购节奏。"]},
            ],
        },
    },
]


class SelectReportRequest(BaseModel):
    session_id: str = "demo-session"
    report_id: str


class ChatRequest(BaseModel):
    session_id: str = "demo-session"
    message: str


class BindingToggleRequest(BaseModel):
    session_id: str = "demo-session"
    group_title: str
    item_title: str


def report_summary(report: dict[str, Any]) -> dict[str, str]:
    return {key: report[key] for key in ["id", "title", "date", "owner", "status", "summary"]}


def find_report(report_id: str) -> dict[str, Any]:
    for report in REPORT_FIXTURES:
        if report["id"] == report_id:
            return deepcopy(report)
    raise HTTPException(status_code=404, detail="报告不存在")


def current_report(state: dict[str, Any]) -> dict[str, Any]:
    if state["report"] is None:
        select_report(state, REPORT_FIXTURES[0]["id"])
    return state["report"]


def select_report(state: dict[str, Any], report_id: str) -> dict[str, Any]:
    report = find_report(report_id)
    state["report"] = report
    state["outline"] = report["outline"]
    state["phase"] = "outline" if report["status"] == "草稿" else "report"
    state["confirmed"] = report["status"] != "草稿"
    if not state["history"]:
        state["history"] = [report_summary(item) for item in REPORT_FIXTURES]
    return report


def build_state_response(session_id: str) -> dict[str, Any]:
    state = get_state(session_id)
    report = current_report(state)
    if not state["history"]:
        state["history"] = [report_summary(item) for item in REPORT_FIXTURES]
    return {
        "session_id": session_id,
        "phase": state["phase"],
        "confirmed": state["confirmed"],
        "history": state["history"],
        "activeReport": report,
        "outline": state["outline"],
    }


def build_assistant_reply(message: str, report: dict[str, Any]) -> str:
    bound_items = [
        item["title"]
        for group in report.get("boundData", [])
        for item in group.get("children", [])
        if item.get("bound")
    ]
    sample = "、".join(bound_items[:4]) or "当前已选数据"
    if "大纲" in message or "outline" in message.lower():
        return f"已根据《{report['title']}》刷新大纲，优先使用 {sample} 等已绑定数据。"
    if "风险" in message:
        return f"已补充风险分析：将结合 {sample} 重点提示现金流、客户集中度与外部价格波动。"
    return f"已收到：{message}。我会基于《{report['title']}》和 {sample} 生成补充内容，并同步更新预览。"


def append_generated_section(report: dict[str, Any], message: str) -> None:
    report["chat"].append({"role": "user", "text": message})
    report["chat"].append({"role": "assistant", "text": build_assistant_reply(message, report)})
    report["detail"]["sections"].append(
        {
            "title": "对话补充",
            "content": f"根据最新请求“{message}”，报告已追加一段模拟分析内容，用于验证前端发送请求、后端维护会话状态和详情预览刷新的完整链路。",
        }
    )
    report["outline"].append({"title": "五、对话补充", "points": ["用户最新请求", "自动生成建议", "后续待确认事项"]})


@app.get("/api/state")
def read_state(session_id: str = "demo-session") -> dict[str, Any]:
    return build_state_response(session_id)


@app.post("/api/reports/select")
def select_report_endpoint(payload: SelectReportRequest) -> dict[str, Any]:
    state = get_state(payload.session_id)
    select_report(state, payload.report_id)
    return build_state_response(payload.session_id)


@app.post("/api/chat")
def chat_endpoint(payload: ChatRequest) -> dict[str, Any]:
    message = payload.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="消息不能为空")
    state = get_state(payload.session_id)
    report = current_report(state)
    append_generated_section(report, message)
    state["outline"] = report["outline"]
    state["report"] = report
    state["phase"] = "report"
    state["confirmed"] = True
    return build_state_response(payload.session_id)


@app.post("/api/bindings/toggle")
def toggle_binding(payload: BindingToggleRequest) -> dict[str, Any]:
    state = get_state(payload.session_id)
    report = current_report(state)
    for group in report.get("boundData", []):
        if group["title"] != payload.group_title:
            continue
        for item in group.get("children", []):
            if item["title"] == payload.item_title:
                item["bound"] = not item.get("bound", False)
                state["report"] = report
                return build_state_response(payload.session_id)
    raise HTTPException(status_code=404, detail="绑定数据不存在")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(BASE_DIR / "index.html")


app.mount("/static", StaticFiles(directory=BASE_DIR), name="static")
