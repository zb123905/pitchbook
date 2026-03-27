"""
VC/PE Prompt Templates for DeepSeek LLM
Specialized prompts for VC/PE industry content analysis
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class VCPEPromptTemplates:
    """
    VC/PE industry-specific prompt templates for content analysis
    """

    # Enhanced system prompt defining the LLM's role
    SYSTEM_PROMPT = """你是一位资深 VC/PE 行业分析师，具有以下专业能力：

## 专业领域
- 风险投资与私募股权市场分析
- 并购交易与投后管理
- 创业生态与投资趋势研究
- 跨行业赛道分析（TMT、医疗、消费、硬科技等）

## 分析原则
1. **准确性优先**: 所有数据必须有明确来源
2. **结构化输出**: 严格遵循 JSON 格式
3. **市场洞察**: 不仅描述事实，更要提供趋势判断
4. **中文表达**: 使用专业术语，保持通俗易懂

## 输出要求
- 投资金额必须包含货币单位和数值（如"5000万美元"、"2.5亿人民币"）
- 公司角色分类要准确（被投公司/投资方/收购方/被收购方）
- 市场情绪要基于数据支撑（交易量增长、大额融资频次等）
- 关键洞察要突出投资价值判断，而非简单罗列事实

请始终以指定的 JSON 格式响应，所有字段值使用中文。"""

    def get_analysis_prompt(
        self,
        content: str,
        analysis_type: str = 'email',
        metadata: Optional[Dict] = None
    ) -> List[Dict[str, str]]:
        """
        Generate analysis prompt for VC/PE content

        Args:
            content: Text content to analyze
            analysis_type: Content type ('email', 'report', 'scraped')
            metadata: Additional context (subject, url, date)

        Returns:
            Messages list for chat completion
        """
        # Truncate content if too long
        max_content_length = 8000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "\n[Content truncated...]"

        # Build user prompt
        user_prompt = self._build_user_prompt(content, analysis_type, metadata)

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]

        return messages

    def _build_user_prompt(
        self,
        content: str,
        analysis_type: str,
        metadata: Optional[Dict]
    ) -> str:
        """Build user prompt based on content type"""

        metadata = metadata or {}

        # Few-shot example to guide the LLM
        few_shot_example = """
## 分析示例

### 示例输入
"红杉资本领投 AI 芯片初创公司 DeepChip A 轮融资 5000 万美元，估值达 2.5 亿美元。本轮融资由经纬创投跟投，资金将用于研发下一代边缘计算芯片。DeepChip 成立于2022年，专注于为自动驾驶和工业物联网提供高性能 AI 推理芯片。"

### 示例输出
```json
{
  "content_type": "交易公告",
  "industries": ["人工智能", "半导体", "汽车科技"],
  "key_topics": ["AI芯片", "边缘计算", "自动驾驶"],
  "mentioned_companies": [
    {"name": "DeepChip", "role": "被投公司"},
    {"name": "红杉资本", "role": "投资方"},
    {"name": "经纬创投", "role": "投资方"}
  ],
  "investment_deals": [
    {
      "company": "DeepChip",
      "amount": "5000万美元",
      "round": "A轮",
      "investors": ["红杉资本", "经纬创投"],
      "valuation": "2.5亿美元"
    }
  ],
  "market_sentiment": "积极",
  "key_insights": [
    "AI 芯片赛道持续火热，大额 A 轮融资显示市场信心",
    "边缘计算成为 AI 芯片新细分赛道，自动驾驶需求强劲",
    "2022年成立的初创公司能在A轮达到2.5亿美元估值，反映资本市场对硬科技的追捧"
  ],
  "summary_chinese": "红杉资本领投 DeepChip A 轮 5000 万美元，估值达 2.5 亿美元。该公司专注 AI 推理芯片，服务于自动驾驶和工业物联网场景。",
  "analysis_full": "本轮融资体现了资本市场对 AI 芯片细分赛道的持续关注。DeepChip 聚焦边缘计算场景，避开了云端训练芯片的红海竞争，选择差异化路线。从投资方组合看，红杉领投、经纬跟投的配置也印证了头部机构对该赛道的共识。估值方面，成立两年的公司能达到 2.5 亿美元估值，反映出当前市场对硬科技初创企业的较高容忍度和预期。"
}
```
"""

        prompt = f"""分析以下 VC/PE 行业内容并提取结构化信息。

{few_shot_example}

---

## 内容类型: {analysis_type.upper()}
"""

        # Add metadata context
        if metadata.get('subject'):
            prompt += f"\n### 主题: {metadata['subject']}\n"

        if metadata.get('url'):
            prompt += f"\n### 来源链接: {metadata['url']}\n"

        if metadata.get('date'):
            prompt += f"\n### 日期: {metadata['date']}\n"

        prompt += f"""

## 待分析内容:

{content}

---

## 要求的输出格式 (JSON):

```json
{{
  "content_type": "周报|市场报告|交易公告|趋势分析|综合新闻",
  "industries": ["风险投资", "私募股权", "并购", "金融科技", "医疗健康", "人工智能", "企业软件", "清洁技术"],
  "key_topics": ["关键主题1", "关键主题2", "关键主题3"],
  "mentioned_companies": [
    {{"name": "公司名称", "role": "被投公司|投资方|收购方|被收购方"}}
  ],
  "investment_deals": [
    {{
      "company": "公司名称",
      "amount": "X百万美元",
      "round": "A轮/B轮/C轮/种子轮/私募/并购",
      "investors": ["投资方1", "投资方2"],
      "valuation": "估值（如有）"
    }}
  ],
  "market_sentiment": "积极|中性|消极",
  "key_insights": ["核心洞察1", "核心洞察2", "核心洞察3"],
  "summary_chinese": "简短的内容摘要",
  "analysis_full": "完整的中文分析（包括市场背景、交易亮点、趋势解读）"
}}
```

请仅输出 JSON 格式，不要包含其他文本。"""

        return prompt

    def get_summary_prompt(
        self,
        analyses: List[Dict],
        time_range: str = "past week"
    ) -> List[Dict[str, str]]:
        """
        Generate prompt for summarizing multiple analyses

        Args:
            analyses: List of individual analysis results
            time_range: Time period being summarized

        Returns:
            Messages list for summary generation
        """
        # Build summary context
        total_deals = sum(len(a.get('investment_deals', [])) for a in analyses)
        companies = []
        for a in analyses:
            companies.extend([c.get('name', '') for c in a.get('mentioned_companies', [])])

        unique_companies = list(set(companies))[:20]

        summary_prompt = f"""生成过去 {time_range} 的 VC/PE 市场活动综合总结。

## 上下文:
- 分析项目总数: {len(analyses)}
- 识别交易总数: {total_deals}
- 提及的主要公司: {', '.join(unique_companies[:10])}

## 各项分析:

"""

        for i, analysis in enumerate(analyses[:5], 1):  # Limit to 5 for context
            summary_prompt += f"""
### 项目 {i}: {analysis.get('content_type', '未知')}
- 主题: {', '.join(analysis.get('key_topics', []))}
- 市场情绪: {analysis.get('market_sentiment', '中性')}
- 交易数: {len(analysis.get('investment_deals', []))}

"""

        summary_prompt += """
## 要求的输出格式 (JSON):

```json
{
  "market_overview": "整体市场趋势总结",
  "key_trends": ["关键趋势1", "关键趋势2", "关键趋势3"],
  "active_sectors": ["活跃领域1", "活跃领域2"],
  "notable_deals": ["重点交易1", "重点交易2"],
  "investor_activity": "投资者行为总结",
  "market_outlook": "积极|中性|消极",
  "summary_chinese": "综合市场总结（中文）"
}
```

请仅输出 JSON 格式，不要包含其他文本。"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": summary_prompt}
        ]

        return messages

    def get_entity_extraction_prompt(self, text: str) -> List[Dict[str, str]]:
        """
        Generate prompt for focused entity extraction

        Args:
            text: Text to extract entities from

        Returns:
            Messages list for entity extraction
        """
        max_length = 6000
        if len(text) > max_length:
            text = text[:max_length] + "\n[Text truncated...]"

        prompt = f"""Extract structured entities from the following VC/PE text.

## Text:

{text}

## Required Output (JSON):

```json
{{
  "companies": [
    {{"name": "Company Name", "type": "startup|corporate|fund|spac"}}
  ],
  "investors": [
    {{"name": "Investor Name", "type": "vc|pe|angel|corporate_vc"}}
  ],
  "people": [
    {{"name": "Person Name", "role": "founder|ceo|partner|investor"}}
  ],
  "amounts": [
    {{"value": "$X million", "context": "description"}}
  ],
  "dates": [
    {{"value": "date string", "context": "description"}}
  ]
}}
```

Respond ONLY with valid JSON."""

        return [
            {"role": "system", "content": "You are a financial entity extraction expert."},
            {"role": "user", "content": prompt}
        ]

    # ==================== Report Generation Prompts ====================

    def get_executive_summary_prompt(
        self,
        analyses: List[Dict],
        time_range: str = "本周"
    ) -> List[Dict[str, str]]:
        """
        生成执行摘要的prompt（800字中文）

        Args:
            analyses: 分析结果列表
            time_range: 时间范围

        Returns:
            Messages列表
        """
        # 构建上下文
        total_count = len(analyses)
        deal_count = sum(len(a.get('investment_deals', [])) for a in analyses)

        # 提取热门主题
        all_topics = []
        for a in analyses:
            all_topics.extend(a.get('key_topics', []))
        from collections import Counter
        top_topics = [t for t, c in Counter(all_topics).most_common(5)]

        # 提取重点交易
        notable_deals = []
        for a in analyses:
            for deal in a.get('investment_deals', [])[:3]:
                notable_deals.append(f"{deal.get('company', '')} {deal.get('round', '')} {deal.get('amount', '')}")

        prompt = f"""请基于以下VC/PE市场分析数据，生成一份专业的执行摘要（约800字中文）。

## 分析周期
{time_range}

## 数据概览
- 分析内容总数: {total_count}
- 涉及交易数量: {deal_count}
- 热门主题: {', '.join(top_topics)}
- 重点交易: {'; '.join(notable_deals[:5])}

## 各项详细分析

"""

        # 添加每个分析的摘要
        for i, a in enumerate(analyses[:10], 1):
            prompt += f"""
### 内容 {i}
- 类型: {a.get('content_type', '未知')}
- 主题: {', '.join(a.get('key_topics', [])[:3])}
- 市场情绪: {a.get('market_sentiment', '中性')}
- 摘要: {a.get('summary_chinese', a.get('summary', ''))[:100]}
"""

        prompt += """
## 要求的输出格式（纯文本，约800字）：

请按以下结构生成执行摘要：

1. **本周整体情况**（150字）
   - 市场整体表现概述
   - 交易活跃度分析
   - 投资者情绪判断

2. **重点交易概述**（250字）
   - 大额融资交易详情
   - 重要并购事件
   - 亮点项目分析

3. **热门赛道分析**（200字）
   - 本周最热门的投资领域
   - 赛道活跃度变化
   - 新兴趋势识别

4. **市场情绪研判**（200字）
   - 整体市场情绪（积极/中性/消极）
   - 影响因素分析
   - 后续走势预判

请使用专业的VC/PE行业术语，保持客观中立的语调，用中文撰写所有内容。"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        return messages

    def get_key_trends_prompt(
        self,
        analyses: List[Dict],
        time_range: str = "本周"
    ) -> List[Dict[str, str]]:
        """
        生成关键趋势分析的prompt（600字中文）

        Args:
            analyses: 分析结果列表
            time_range: 时间范围

        Returns:
            Messages列表
        """
        from collections import Counter

        # 统计内容类型
        content_types = [a.get('content_type', '') for a in analyses]
        type_counts = Counter(content_types)

        # 统计热门行业
        all_industries = []
        for a in analyses:
            all_industries.extend(a.get('industries', []))
        industry_counts = Counter(all_industries)

        # 统计投资阶段
        all_rounds = []
        for a in analyses:
            for deal in a.get('investment_deals', []):
                all_rounds.append(deal.get('round', ''))
        round_counts = Counter(all_rounds)

        # 市场情绪统计
        sentiments = [a.get('market_sentiment', 'neutral') for a in analyses]
        sentiment_counts = Counter(sentiments)

        prompt = f"""请基于以下VC/PE市场数据，分析关键趋势（约600字中文）。

## 分析周期
{time_range}

## 内容类型分布
{dict(type_counts.most_common())}

## 行业分布
{dict(industry_counts.most_common(10))}

## 投资阶段分布
{dict(round_counts.most_common())}

## 市场情绪分布
{dict(sentiment_counts)}

## 关键洞察汇总
"""

        # 添加各分析的关键洞察
        for i, a in enumerate(analyses[:8], 1):
            insights = a.get('key_insights', [])
            if insights:
                prompt += f"\n内容{i}: {insights[0] if insights else ''}"

        prompt += """
## 要求的输出格式（纯文本，约600字）：

请按以下结构生成趋势分析：

1. **赛道热度分析**（180字）
   - 本周最热门的投资赛道
   - 赛道热度变化趋势
   - 跨赛道比较分析

2. **投资阶段变化**（150字）
   - 各阶段投资活跃度
   - 早中后期项目分布
   - 阶段偏好变化

3. **估值趋势判断**（150字）
   - 整体估值水平
   - 大额交易估值特点
   - 估值预期变化

4. **政策与市场影响**（120字）
   - 相关政策影响
   - 市场环境变化
   - 国际因素考量

请使用专业的VC/PE行业术语，基于数据支撑你的判断，用中文撰写所有内容。"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        return messages

    def get_recommendations_prompt(
        self,
        analyses: List[Dict],
        time_range: str = "本周"
    ) -> List[Dict[str, str]]:
        """
        生成投资建议的prompt（400字中文）

        Args:
            analyses: 分析结果列表
            time_range: 时间范围

        Returns:
            Messages列表
        """
        from collections import Counter

        # 提取热门赛道
        all_topics = []
        for a in analyses:
            all_topics.extend(a.get('key_topics', []))
        hot_sectors = [t for t, c in Counter(all_topics).most_common(5)]

        # 统计交易活跃度
        deal_count = sum(len(a.get('investment_deals', [])) for a in analyses)

        # 市场情绪
        sentiments = [a.get('market_sentiment', 'neutral') for a in analyses]
        from collections import Counter
        overall_sentiment = Counter(sentiments).most_common(1)[0][0] if sentiments else 'neutral'

        prompt = f"""请基于以下VC/PE市场数据，生成投资建议（约400字中文）。

## 分析周期
{time_range}

## 市场概况
- 交易总数: {deal_count}
- 整体情绪: {overall_sentiment}
- 热门赛道: {', '.join(hot_sectors)}

## 市场观察要点

"""

        # 添加各分析的关键洞察
        for i, a in enumerate(analyses[:5], 1):
            insights = a.get('key_insights', [])
            if insights:
                prompt += f"\n观察点{i}: {insights[0]}"

        prompt += """
## 要求的输出格式（纯文本，约400字）：

请按以下结构生成投资建议：

1. **关注赛道建议**（120字）
   - 值得重点关注的投资领域
   - 有潜力的细分赛道
   - 需要谨慎观望的领域

2. **投资策略建议**（140字）
   - 当前阶段适合的投资策略
   - 投资节奏建议
   - 项目筛选标准

3. **风险控制建议**（140字）
   - 主要风险点识别
   - 风险规避策略
   - 分散投资建议

请基于市场数据给出务实的建议，避免空泛的表述，用中文撰写所有内容。"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        return messages

    def get_email_analysis_prompt(
        self,
        analysis: Dict,
        email_index: int
    ) -> List[Dict[str, str]]:
        """
        生成单封邮件深度分析的prompt（400字中文）

        Args:
            analysis: 单个邮件分析结果
            email_index: 邮件序号

        Returns:
            Messages列表
        """
        subject = analysis.get('subject', '未知主题')
        content_type = analysis.get('content_type', '未知类型')
        topics = analysis.get('key_topics', [])
        industries = analysis.get('industries', [])
        deals = analysis.get('investment_deals', [])
        companies = analysis.get('mentioned_companies', [])
        summary = analysis.get('summary_chinese', analysis.get('summary', ''))
        full_analysis = analysis.get('analysis_full', '')
        insights = analysis.get('key_insights', [])
        sentiment = analysis.get('market_sentiment', 'neutral')

        # 构建交易信息
        deal_info = ""
        if deals:
            for deal in deals[:3]:
                deal_info += f"""
    - 公司: {deal.get('company', '')}
    - 轮次: {deal.get('round', '')}
    - 金额: {deal.get('amount', '')}
    - 投资方: {', '.join(deal.get('investors', []))}
    - 估值: {deal.get('valuation', '未知')}
"""

        # 构建公司信息
        company_info = ""
        if companies:
            company_info = "\n".join([f"- {c.get('name', '')} ({c.get('role', '')})" for c in companies[:5]])

        prompt = f"""请对以下VC/PE行业邮件内容进行深度分析（约400字中文）。

## 邮件基本信息
- 邮件主题: {subject}
- 内容类型: {content_type}
- 市场情绪: {sentiment}

## 分析结果
- 关键主题: {', '.join(topics)}
- 涉及行业: {', '.join(industries)}

## 涉及的公司
{company_info}

## 交易详情
{deal_info if deal_info else '无具体交易信息'}

## 已有的AI分析摘要
{summary}

## 完整分析
{full_analysis}

## 关键洞察
{chr(10).join([f'- {insight}' for insight in insights])}

## 要求的输出格式（纯文本，约400字）：

请按以下结构生成邮件深度分析：

1. **邮件内容核心要点**（100字）
   - 邮件主要内容概述
   - 最重要信息的提炼
   - 对读者的价值

2. **涉及的公司和投资方**（80字）
   - 重要公司背景介绍
   - 投资方特点分析
   - 产业链位置分析

3. **交易亮点分析**（120字）
   - 交易亮点提炼
   - 投资逻辑解读
   - 行业意义分析

4. **市场影响评估**（100字）
   - 对行业的影响
   - 对投资风向的指示
   - 后续关注要点

请基于已有分析结果进行深化和拓展，使用专业的VC/PE行业术语，用中文撰写所有内容。"""

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        return messages
