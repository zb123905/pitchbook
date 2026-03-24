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

    # System prompt defining the LLM's role
    SYSTEM_PROMPT = """你是一位专业的 VC/PE 行业分析师，深耕风险投资、私募股权、并购和创业生态领域。

你的任务是分析来自 PitchBook 邮件、市场报告和新闻的内容，提取：
1. 内容类型（周报、市场分析、交易公告等）
2. 行业分类（VC/PE 关注领域）
3. 关键主题和趋势
4. 提及的公司及其角色
5. 投资交易（公司、金额、轮次、投资方）
6. 市场情绪指标
7. 中文综合摘要

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

        prompt = f"""分析以下 VC/PE 行业内容并提取结构化信息。

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
