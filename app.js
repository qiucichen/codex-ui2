const mockReports = [
  {
    id: 'r-2026-q2',
    title: '2026 Q2 智能经营分析报告',
    date: '2026-06-05',
    owner: '战略分析组',
    status: '已生成',
    summary: '聚焦收入增长、客户结构与风险提示。',
    metrics: [
      { label: '收入规模', value: '¥8,420万' },
      { label: '同比增长', value: '+18.6%' },
      { label: '风险事项', value: '5项' }
    ],
    tags: ['经营分析', '季度复盘', '董事会材料'],
    boundData: [
      {
        title: '经营数据',
        children: [
          { title: '销售收入明细', bound: true },
          { title: '区域渠道贡献', bound: true },
          { title: '重点客户续约率', bound: true }
        ]
      },
      {
        title: '财务数据',
        children: [
          { title: '成本费用结构', bound: true },
          { title: '现金流预测', bound: false },
          { title: '毛利率拆解', bound: true }
        ]
      },
      {
        title: '外部数据',
        children: [
          { title: '行业景气指数', bound: false },
          { title: '竞品价格监测', bound: true }
        ]
      }
    ],
    chat: [
      { role: 'user', text: '请基于已绑定的数据生成一份经营分析报告。' },
      { role: 'assistant', text: '已读取销售、财务与竞品监测数据，建议报告采用“整体表现—结构拆解—风险建议”的叙事结构。' },
      { role: 'user', text: '风险提示需要突出现金流和大客户集中度。' },
      { role: 'assistant', text: '已将现金流预测缺口、大客户续约波动纳入风险章节，并在详情预览中增加行动建议。' }
    ],
    outline: [
      { title: '一、执行摘要', points: ['核心结论', '关键指标变化', '管理层关注事项'] },
      { title: '二、经营表现', points: ['收入规模与增长', '区域渠道贡献', '客户结构变化'] },
      { title: '三、财务与风险', points: ['成本费用结构', '现金流压力', '大客户集中度'] },
      { title: '四、行动建议', points: ['短期跟进事项', '中期优化方向', '指标监控机制'] }
    ],
    detail: {
      lead: '本季度公司收入保持双位数增长，核心区域延续高景气，但费用投入节奏和大客户续约不确定性需要持续跟踪。',
      sections: [
        {
          title: '经营表现',
          content: 'Q2 收入达到 ¥8,420 万，同比增长 18.6%。华东与华南渠道合计贡献 63% 的新增收入，其中企业级客户套餐升级是主要拉动因素。'
        },
        {
          title: '风险提示',
          list: ['现金流预测数据尚未完全绑定，建议补齐未来 12 周回款计划。', '前五大客户收入占比升至 41%，续约波动可能影响下季度确认收入。', '竞品在中端产品线出现价格下探，需要评估促销策略与毛利影响。']
        },
        {
          title: '建议动作',
          content: '建议将重点客户续约、费用使用率和现金回款纳入周度追踪看板，并由销售、财务、运营共同维护数据口径。'
        }
      ]
    }
  },
  {
    id: 'r-market',
    title: '新能源行业洞察报告',
    date: '2026-05-28',
    owner: '行业研究组',
    status: '草稿',
    summary: '分析政策变化、供需结构与竞品动态。'
  },
  {
    id: 'r-customer',
    title: '企业客户满意度分析',
    date: '2026-05-18',
    owner: '客户成功部',
    status: '已归档',
    summary: '梳理 NPS、续约意向和服务响应效率。'
  },
  {
    id: 'r-risk',
    title: '供应链风险月报',
    date: '2026-04-30',
    owner: '运营管理部',
    status: '已生成',
    summary: '追踪供应商交付、库存安全线与成本波动。'
  }
];

const activeReport = mockReports[0];

function renderHistory() {
  const history = document.querySelector('#history-list');
  history.innerHTML = mockReports
    .map(
      report => `
        <article class="history-card ${report.id === activeReport.id ? 'active' : ''}">
          <h3>${report.title}</h3>
          <p>${report.summary}</p>
          <div class="history-meta">
            <span>${report.date}</span>
            <span class="status-dot">${report.status}</span>
          </div>
        </article>
      `
    )
    .join('');
}

function renderDataTree() {
  const tree = document.querySelector('#data-tree');
  tree.innerHTML = activeReport.boundData
    .map(
      group => `
        <div class="tree-group" role="group">
          <div class="tree-title" role="treeitem" aria-expanded="true">${group.title}</div>
          ${group.children
            .map(item => `<div class="tree-item ${item.bound ? 'bound' : ''}" role="treeitem">${item.title}</div>`)
            .join('')}
        </div>
      `
    )
    .join('');
}

function renderChat() {
  document.querySelector('#current-report-chip').textContent = activeReport.title;
  const messages = document.querySelector('#chat-messages');
  messages.innerHTML = activeReport.chat
    .map(message => `<div class="message ${message.role}">${message.text}</div>`)
    .join('');
}

function renderOutline() {
  const outline = document.querySelector('#outline-preview');
  outline.innerHTML = activeReport.outline
    .map(
      (item, index) => `
        <section class="outline-card">
          <span class="outline-index">${index + 1}</span>
          <h3>${item.title}</h3>
          <ul>${item.points.map(point => `<li>${point}</li>`).join('')}</ul>
        </section>
      `
    )
    .join('');
}

function renderDetail() {
  const detail = document.querySelector('#report-detail');
  detail.innerHTML = `
    <header class="report-cover">
      <h2>${activeReport.title}</h2>
      <p>${activeReport.owner} · ${activeReport.date} · 模拟数据生成</p>
    </header>
    <section class="metrics">
      ${activeReport.metrics
        .map(metric => `<div class="metric"><span>${metric.label}</span><strong>${metric.value}</strong></div>`)
        .join('')}
    </section>
    <section class="detail-section">
      <h3>摘要</h3>
      <p>${activeReport.detail.lead}</p>
      <div class="tag-row">${activeReport.tags.map(tag => `<span class="tag">${tag}</span>`).join('')}</div>
    </section>
    ${activeReport.detail.sections
      .map(section => {
        const body = section.list
          ? `<ul>${section.list.map(item => `<li>${item}</li>`).join('')}</ul>`
          : `<p>${section.content}</p>`;
        return `<section class="detail-section"><h3>${section.title}</h3>${body}</section>`;
      })
      .join('')}
  `;
}

renderHistory();
renderDataTree();
renderChat();
renderOutline();
renderDetail();
