"""
Investment Relation Extractor
Extracts investment relationships, M&A deals, and partnerships from financial text.
Builds upon entity extraction to identify structured relationships.
"""
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from nlp.entity_extractor import FinancialEntityExtractor


class InvestmentRelationExtractor:
    """
    Extract investment and financial relationships from text.

    Supported relation types:
    - Investment: Investor → Target Company (with stage, amount)
    - M&A: Acquirer → Target Company
    - Partnership: Company A ↔ Company B
    - Funding: Company ← Round Amount from Investors
    """

    # Investment action verbs
    INVESTMENT_VERBS = [
        'invested', 'invests', 'lead', 'led', 'participated', 'backed',
        'funded', '投资', '领投', '参投', '支持', '注资'
    ]

    # M&A verbs
    MA_VERBS = [
        'acquired', 'acquires', 'bought', 'buys', 'merged', 'merges with',
        'acquisition', 'takeover', 'buyout',
        '收购', '并购', '兼并', '收购了', '合并', '并购交易'
    ]

    # Partnership verbs
    PARTNERSHIP_VERBS = [
        'partnered', 'partners', 'collaborated', 'collaborates', 'joint venture',
        'strategic partnership', 'alliance',
        '合作', '战略合作', '联手', '合资', '伙伴关系'
    ]

    # Deal stage indicators
    STAGE_INDICATORS = [
        'seed', 'series a', 'series b', 'series c', 'series d', 'series e',
        'pre-seed', 'pre-a', 'pre-ipo', 'ipo',
        '种子轮', '天使轮', 'A轮', 'B轮', 'C轮', 'D轮', 'E轮', 'Pre-IPO', 'IPO'
    ]

    def __init__(self, entity_extractor: Optional[FinancialEntityExtractor] = None):
        """
        Initialize relation extractor

        Args:
            entity_extractor: Optional entity extractor instance
        """
        self.entity_extractor = entity_extractor or FinancialEntityExtractor(use_spacy=False)

    def extract_relations(self, text: str, entities: Optional[Dict] = None) -> List[Dict]:
        """
        Extract all relations from text

        Args:
            text: Input text
            entities: Pre-extracted entities (optional, will extract if not provided)

        Returns:
            List of relation dictionaries:
            [{
                'type': 'investment|ma|partnership',
                'investor': 'Investor name',
                'target': 'Target company',
                'stage': 'Deal stage',
                'amount': {'amount': float, 'currency': str},
                'date': 'ISO date string',
                'confidence': float,
                'text': 'Original text snippet'
            }]
        """
        if not text or not isinstance(text, str):
            return []

        # Extract entities if not provided
        if entities is None:
            entities = self.entity_extractor.extract_entities(text)

        relations = []

        # Extract different relation types
        relations.extend(self._extract_investment_relations(text, entities))
        relations.extend(self._extract_ma_relations(text, entities))
        relations.extend(self._extract_partnership_relations(text, entities))

        # Deduplicate and score
        relations = self._deduplicate_relations(relations)

        return relations

    def _extract_investment_relations(self, text: str, entities: Dict) -> List[Dict]:
        """Extract investment relationships"""
        relations = []

        investors = entities.get('investors', [])
        companies = entities.get('companies', [])
        amounts = entities.get('amounts', [])
        deal_stages = entities.get('deal_stages', [])

        # Pattern 1: Investor + verb + Company + (stage) + (amount)
        # Example: "红杉资本投资了字节跳动的C轮融资2亿美元"
        # "红杉资本领投了字节跳动C轮融资"

        for investor in investors:
            # Find sentences with this investor
            # Make patterns more flexible for Chinese text (allow "了", "的", etc.)
            investor_patterns = [
                # Chinese patterns - use double {{ }} for regex quantifiers in f-strings
                rf'{re.escape(investor)}\s*(?:领投了|领投|投资了|投资)\s*([^\n。.]{{2,200}})',
                rf'{re.escape(investor)}\s*(?:参投|跟投)\s*([^\n。.]{{2,200}})',
                # English patterns
                rf'{re.escape(investor)}\s+(?:invested\s+in|invests\s+in|invested)\s+([^\n。.]{{2,200}})',
                rf'{re.escape(investor)}\s+(?:led|lead\s+the|lead)\s+([^\n。.]{{2,200}})',
                rf'{re.escape(investor)}\s+(?:participated\s+in)\s+([^\n。.]{{2,200}})',
            ]

            for pattern in investor_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    context = match.group(0)

                    # Extract target company from context
                    target = self._extract_target_from_context(context, companies)
                    if not target:
                        continue

                    # Extract deal stage
                    stage = self._extract_stage_from_context(context, deal_stages)

                    # Extract amount
                    amount = self._extract_amount_from_context(context, amounts)

                    # Extract date
                    date = self._extract_date_from_context(context)

                    # Calculate confidence
                    confidence = self._calculate_investment_confidence(
                        investor, target, stage, amount, context
                    )

                    relation = {
                        'type': 'investment',
                        'investor': investor,
                        'target': target,
                        'stage': stage,
                        'amount': amount,
                        'date': date,
                        'confidence': confidence,
                        'text': context.strip()
                    }

                    relations.append(relation)

        # Pattern 2: Company + raised/secured + amount + from + investors
        # Example: "字节跳动完成了C轮2亿美元融资，由红杉资本领投"

        for company in companies:
            funding_patterns = [
                rf'{re.escape(company)}\s+(?:完成|completed|raised|secured|announced)\s+([^\n。.]{{10,200}})',
            ]

            for pattern in funding_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    context = match.group(0)

                    # Extract investors from context
                    context_investors = [inv for inv in investors if inv in context]
                    if not context_investors:
                        continue

                    # Lead investor is usually mentioned first or with specific keywords
                    lead_investor = self._extract_lead_investor(context, context_investors)

                    # Extract stage
                    stage = self._extract_stage_from_context(context, deal_stages)

                    # Extract amount
                    amount = self._extract_amount_from_context(context, amounts)

                    relation = {
                        'type': 'investment',
                        'investor': lead_investor,
                        'target': company,
                        'stage': stage,
                        'amount': amount,
                        'date': self._extract_date_from_context(context),
                        'confidence': 0.8,
                        'text': context.strip()
                    }

                    relations.append(relation)

        return relations

    def _extract_ma_relations(self, text: str, entities: Dict) -> List[Dict]:
        """Extract M&A relationships"""
        relations = []

        companies = entities.get('companies', [])
        amounts = entities.get('amounts', [])

        # Pattern: Acquirer + acquired/bought + Target
        for company_a in companies:
            for company_b in companies:
                if company_a == company_b:
                    continue

                # Check for M&A relation
                ma_patterns = [
                    rf'{re.escape(company_a)}\s+(?:acquired|收购|bought|并购|兼并)\s+{re.escape(company_b)}',
                    rf'{re.escape(company_b)}\s+(?:was\s+acquired\s+by|被.*收购|被.*并购)\s+{re.escape(company_a)}',
                ]

                for pattern in ma_patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        context = match.group(0)

                        # Extract amount if present
                        amount = self._extract_amount_from_context(context, amounts)

                        # Extract date
                        date = self._extract_date_from_context(context)

                        relation = {
                            'type': 'ma',
                            'acquirer': company_a,
                            'target': company_b,
                            'amount': amount,
                            'date': date,
                            'confidence': 0.85,
                            'text': context.strip()
                        }

                        relations.append(relation)

        return relations

    def _extract_partnership_relations(self, text: str, entities: Dict) -> List[Dict]:
        """Extract partnership relationships"""
        relations = []

        companies = entities.get('companies', [])

        # Pattern: Company A + partnered/collaborated + with + Company B
        for i, company_a in enumerate(companies):
            for company_b in companies[i+1:]:
                partnership_patterns = [
                    rf'{re.escape(company_a)}\s+(?:partnered|collaborated|合作|联手)\s+(?:with|和|与)\s+{re.escape(company_b)}',
                    rf'{re.escape(company_b)}\s+(?:partnered|collaborated|合作|联手)\s+(?:with|和|与)\s+{re.escape(company_a)}',
                ]

                for pattern in partnership_patterns:
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        context = match.group(0)

                        relation = {
                            'type': 'partnership',
                            'company_a': company_a,
                            'company_b': company_b,
                            'date': self._extract_date_from_context(context),
                            'confidence': 0.7,
                            'text': context.strip()
                        }

                        relations.append(relation)

        return relations

    def _extract_target_from_context(self, context: str, companies: List[str]) -> Optional[str]:
        """Extract target company from context"""
        # Find companies mentioned in context
        for company in companies:
            if company in context:
                return company

    def _extract_target_from_context(self, context: str, companies: List[str]) -> Optional[str]:
        """Extract target company from context"""
        # Find companies mentioned in context
        for company in companies:
            if company in context:
                return company

        # If no pre-extracted company found, try to extract company from context
        # Use more flexible patterns

        # Pattern 1: After investment verbs, look for company names
        # Handles: "投资了字节跳动的", "led ByteDance's", "invested in TikTok"
        patterns = [
            # Chinese: 投资/领投 + company + 的/轮
            r'(?:投资了|投资|领投|参投)\s*([^\s,。]{2,20}?)(?:的|的C|的D|的A|的B|轮)',
            # English: invested/led + company + 's/round/Series
            r'(?:invested\s+in|led|lead)\s+([A-Z][A-Za-z\u4e00-\u9fff]{2,20}?)(?:\'s|\'|\'s\s+Series|\'s\s+[A-Z]|\'s\s+\d)',
        ]

        for pattern in patterns:
            match = re.search(pattern, context, re.IGNORECASE)
            if match:
                potential_company = match.group(1).strip()
                # Filter out common non-company words
                if len(potential_company) >= 2 and not any(
                    word in potential_company.lower()
                    for word in ['the', 'this', 'that', 'a', 'an', 'in', 'round', 'series']
                ):
                    return potential_company

        # Pattern 2: Known brands fallback
        known_brands = ['字节跳动', 'ByteDance', 'TikTok', '抖音', '快手', 'Kuaishou',
                        '饿了么', 'Ele.me', 'Alibaba', '阿里', 'Tencent', '腾讯',
                        '美团', 'Meituan', '滴滴', 'Didi', '小米', 'Xiaomi']
        for brand in known_brands:
            if brand in context:
                return brand

        return None

    def _extract_lead_investor(self, context: str, investors: List[str]) -> Optional[str]:
        """Extract lead investor from context"""
        # Check for lead investor keywords
        lead_keywords = ['领投', 'lead', 'leading', '主导']

        for investor in investors:
            # Check if investor is mentioned with lead keywords
            for keyword in lead_keywords:
                if keyword in context.lower() and investor in context:
                    return investor

        # Return first investor if no lead indicator found
        return investors[0] if investors else None

    def _extract_stage_from_context(self, context: str, deal_stages: List[str]) -> Optional[str]:
        """Extract deal stage from context"""
        context_lower = context.lower()

        for stage in deal_stages:
            if stage.lower() in context_lower:
                return stage

        return None

    def _extract_amount_from_context(self, context: str, amounts: List[dict]) -> Optional[dict]:
        """Extract amount from context"""
        # Find amounts mentioned in context
        for amount in amounts:
            if amount.get('original_text', '') in context:
                return amount

        return None

    def _extract_date_from_context(self, context: str) -> Optional[str]:
        """Extract date from context"""
        # Date patterns
        date_patterns = [
            r'\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?',
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, context)
            if match:
                return match.group(0)

        return None

    def _calculate_investment_confidence(
        self,
        investor: str,
        target: str,
        stage: Optional[str],
        amount: Optional[dict],
        context: str
    ) -> float:
        """Calculate confidence score for investment relation"""
        confidence = 0.5  # Base confidence

        # Increase confidence if stage is specified
        if stage:
            confidence += 0.15

        # Increase confidence if amount is specified
        if amount:
            confidence += 0.15

        # Increase confidence for known investors
        known_investors = ['sequoia', 'idg', 'matrix', '红杉', '经纬', '高瓴']
        if any(kw in investor.lower() for kw in known_investors):
            confidence += 0.1

        # Increase confidence for clear action verbs
        strong_verbs = ['领投', 'lead', '完成', 'completed', 'announced']
        if any(verb in context.lower() for verb in strong_verbs):
            confidence += 0.1

        return min(confidence, 1.0)

    def _deduplicate_relations(self, relations: List[Dict]) -> List[Dict]:
        """Remove duplicate relations, keep highest confidence"""
        if not relations:
            return []

        # Group by unique key
        unique_relations = {}

        for relation in relations:
            # Create unique key
            if relation['type'] == 'investment':
                key = (
                    relation['type'],
                    relation.get('investor', ''),
                    relation.get('target', ''),
                    relation.get('stage', '')
                )
            elif relation['type'] == 'ma':
                key = (
                    relation['type'],
                    relation.get('acquirer', ''),
                    relation.get('target', '')
                )
            else:  # partnership
                key = (
                    relation['type'],
                    tuple(sorted([relation.get('company_a', ''), relation.get('company_b', '')]))
                )

            # Keep highest confidence
            if key not in unique_relations or relation['confidence'] > unique_relations[key]['confidence']:
                unique_relations[key] = relation

        return list(unique_relations.values())

    def extract_deals(self, text: str) -> List[Dict]:
        """
        Extract complete deal information

        Returns structured deal data:
        [{
            'company': 'Company name',
            'investors': ['Investor 1', 'Investor 2'],
            'lead_investor': 'Lead investor',
            'stage': 'Deal stage',
            'amount': {'amount': float, 'currency': str, 'normalized': str},
            'date': 'Date string',
            'valuation': {'amount': float, 'currency': str},
            'description': 'Deal description'
        }]
        """
        entities = self.entity_extractor.extract_entities(text)
        relations = self.extract_relations(text, entities)

        deals = []

        # Group investment relations by target company
        for relation in relations:
            if relation['type'] != 'investment':
                continue

            deal = {
                'company': relation.get('target', ''),
                'investors': [relation.get('investor', '')],
                'lead_investor': relation.get('investor', ''),
                'stage': relation.get('stage'),
                'amount': relation.get('amount'),
                'date': relation.get('date'),
                'valuation': None,  # Valuation extraction is complex, could be added later
                'description': relation.get('text', ''),
                'confidence': relation.get('confidence', 0.5)
            }

            deals.append(deal)

        # Merge deals for same company/stage (multiple investors)
        merged_deals = self._merge_deals(deals)

        return merged_deals

    def _merge_deals(self, deals: List[Dict]) -> List[Dict]:
        """Merge deals for the same company and stage"""
        if not deals:
            return []

        merged = {}

        for deal in deals:
            key = (deal['company'], deal.get('stage', ''))

            if key not in merged:
                merged[key] = deal
            else:
                # Add investors to existing deal
                existing_investors = set(merged[key]['investors'])
                new_investors = set(deal['investors'])
                merged[key]['investors'] = list(existing_investors | new_investors)

                # Update lead investor if confidence is higher
                if deal.get('confidence', 0) > merged[key].get('confidence', 0):
                    merged[key]['lead_investor'] = deal.get('lead_investor')
                    merged[key]['confidence'] = deal.get('confidence', 0)

        return list(merged.values())


# Demo and testing
if __name__ == "__main__":
    # Test the extractor
    extractor = InvestmentRelationExtractor()

    test_text = """
    红杉资本领投了字节跳动的C轮融资，投资金额为2亿美元。
    Sequoia Capital led the Series C round of ByteDance with $200 million.
    估值达到2000亿元。

    创新工场投资了快手的D轮，金额达到1.5亿人民币。
    Sinovation Ventures participated in Kuaishou's Series D round with 150 million RMB.

    此外，阿里巴巴收购了饿了么，交易金额为95亿美元。
    """

    print("="*70)
    print("Investment Relation Extraction Test")
    print("="*70)

    entities = extractor.entity_extractor.extract_entities(test_text)

    print("\nExtracted Entities:")
    for entity_type, entity_list in entities.items():
        if entity_list:
            print(f"\n{entity_type.upper()}:")
            for entity in entity_list[:5]:  # Show first 5
                print(f"  - {entity}")

    relations = extractor.extract_relations(test_text, entities)

    print(f"\n\nExtracted Relations ({len(relations)}):")
    for idx, relation in enumerate(relations, 1):
        print(f"\n{idx}. {relation.get('type', 'unknown').upper()}")
        for key, value in relation.items():
            if key != 'type':
                print(f"   {key}: {value}")

    deals = extractor.extract_deals(test_text)

    print(f"\n\nExtracted Deals ({len(deals)}):")
    for idx, deal in enumerate(deals, 1):
        print(f"\n{idx}. {deal.get('company', 'Unknown')} - {deal.get('stage', 'Unknown Round')}")
        print(f"   Investors: {', '.join(deal.get('investors', []))}")
        if deal.get('amount'):
            print(f"   Amount: {deal['amount'].get('normalized', 'N/A')}")
        print(f"   Confidence: {deal.get('confidence', 0):.2f}")
