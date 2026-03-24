"""
Financial Entity Extractor
Extracts financial entities from VC/PE industry content using spaCy and custom patterns.
Supports both Chinese and English text processing.
"""
import re
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    logger.warning("spaCy not available, using rule-based extraction only")

from utils.chinese_utils import has_chinese, extract_chinese_amount, is_chinese_char
from utils.date_utils import parse_flexible_date, extract_dates_from_text


class FinancialEntityExtractor:
    """
    Financial domain entity extractor for VC/PE industry content.

    Extracts:
    - Company names (Chinese and English)
    - Investment amounts (multi-currency)
    - Investor/VC firm names
    - Person names (founders, CEOs)
    - Dates (deal dates, report dates)
    - Locations (cities, countries)
    - Deal stages (Seed, Series A, B, C, etc.)
    """

    # Financial entity patterns
    COMPANY_SUFFIXES = [
        'Inc', 'Corp', 'Ltd', 'LLC', 'LLP', 'Group', 'Company', 'Co', 'Technologies',
        'Tech', 'Solutions', 'Systems', 'Labs', 'Studios', 'Networks', 'Holdings',
        '公司', '科技', '集团', '有限', '股份', '企业', '工作室'
    ]

    INVESTOR_SUFFIXES = [
        'Capital', 'Ventures', 'Partners', 'Investment', 'Investments', 'VC', 'PE',
        'Fund', 'Management', 'Advisors', 'Group', 'Holdings',
        '资本', '创投', '投资', '基金', '管理', '资产'
    ]

    DEAL_STAGES = [
        'Pre-Seed', 'Seed', 'Angel', 'Pre-A', 'Pre-A Round',
        'Series A', 'Series B', 'Series C', 'Series D', 'Series E', 'Series F',
        'A轮', 'B轮', 'C轮', 'D轮', 'E轮', 'F轮',
        'Pre-IPO', 'IPO', 'Post-IPO',
        '天使轮', '种子轮', 'Pre-IPO轮', 'IPO轮',
        'Strategic', 'Acquisition', 'M&A', 'Buyout',
        '战略投资', '并购', '收购', '杠杆收购'
    ]

    CURRENCIES = [
        'USD', 'EUR', 'GBP', 'JPY', 'CNY', 'HKD', 'SGD',
        'dollar', 'dollars', 'euro', 'euros', 'pound', 'pounds', 'yen', 'yuan',
        '美元', '欧元', '英镑', '日元', '人民币', '港币', '新加坡元',
        '$', '€', '£', '¥', '￥'
    ]

    def __init__(self, use_spacy: bool = True):
        """
        Initialize entity extractor

        Args:
            use_spacy: Whether to use spaCy for NER (fallback to rule-based if False)
        """
        self.use_spacy = use_spacy and SPACY_AVAILABLE
        self.nlp_zh = None
        self.nlp_en = None

        if self.use_spacy:
            self._load_spacy_models()

    def _load_spacy_models(self):
        """Load spaCy language models"""
        try:
            import spacy

            # Load Chinese model
            try:
                self.nlp_zh = spacy.load("zh_core_web_sm")
                logger.info("✓ Loaded Chinese spaCy model (zh_core_web_sm)")
            except OSError:
                logger.warning("Chinese model not found, run: python -m spacy download zh_core_web_sm")
                self.nlp_zh = None

            # Load English model
            try:
                self.nlp_en = spacy.load("en_core_web_sm")
                logger.info("✓ Loaded English spaCy model (en_core_web_sm)")
            except OSError:
                logger.warning("English model not found, run: python -m spacy download en_core_web_sm")
                self.nlp_en = None

            if not self.nlp_zh and not self.nlp_en:
                self.use_spacy = False
                logger.warning("No spaCy models loaded, using rule-based extraction")

        except Exception as e:
            logger.error(f"Error loading spaCy models: {e}")
            self.use_spacy = False

    def extract_entities(self, text: str) -> Dict[str, List]:
        """
        Extract all entities from text

        Args:
            text: Input text (can be mixed Chinese/English)

        Returns:
            Dictionary with entity lists:
            {
                'companies': [...],
                'amounts': [...],
                'investors': [...],
                'persons': [...],
                'dates': [...],
                'locations': [...],
                'deal_stages': [...]
            }
        """
        if not text or not isinstance(text, str):
            return self._empty_result()

        # Detect language
        has_chinese_text = has_chinese(text)

        # Use spaCy if available, otherwise use rule-based extraction
        if self.use_spacy:
            return self._extract_with_spacy(text, has_chinese_text)
        else:
            return self._extract_rule_based(text, has_chinese_text)

    def _empty_result(self) -> Dict[str, List]:
        """Return empty result structure"""
        return {
            'companies': [],
            'amounts': [],
            'investors': [],
            'persons': [],
            'dates': [],
            'locations': [],
            'deal_stages': []
        }

    def _extract_with_spacy(self, text: str, has_chinese: bool) -> Dict[str, List]:
        """Extract entities using spaCy NER"""
        result = self._empty_result()

        # Choose appropriate model
        nlp = self.nlp_zh if has_chinese and self.nlp_zh else self.nlp_en

        if not nlp:
            return self._extract_rule_based(text, has_chinese)

        try:
            doc = nlp(text)

            # Extract entities using spaCy NER
            for ent in doc.ents:
                entity_text = ent.text.strip()

                if ent.label_ == 'ORG':
                    # Determine if it's a company or investor
                    if self._is_investor(entity_text):
                        result['investors'].append(entity_text)
                    else:
                        result['companies'].append(entity_text)

                elif ent.label_ == 'PERSON':
                    result['persons'].append(entity_text)

                elif ent.label_ in ['GPE', 'LOC']:
                    result['locations'].append(entity_text)

                elif ent.label_ == 'DATE':
                    parsed_date = parse_flexible_date(entity_text)
                    if parsed_date:
                        result['dates'].append({
                            'text': entity_text,
                            'date': parsed_date.isoformat()
                        })

            # Extract amounts and deal stages with custom patterns
            result['amounts'].extend(self._extract_amounts(text))
            result['deal_stages'].extend(self._extract_deal_stages(text))

            # Deduplicate results
            for key in result:
                result[key] = list(set(result[key]))

        except Exception as e:
            logger.warning(f"spaCy extraction error: {e}, falling back to rule-based")
            return self._extract_rule_based(text, has_chinese)

        return result

    def _extract_rule_based(self, text: str, has_chinese: bool) -> Dict[str, List]:
        """Extract entities using rule-based patterns"""
        result = self._empty_result()

        result['companies'].extend(self._extract_companies(text))
        result['investors'].extend(self._extract_investors(text))
        result['persons'].extend(self._extract_persons(text))
        result['amounts'].extend(self._extract_amounts(text))
        result['dates'].extend(self._extract_dates(text))
        result['locations'].extend(self._extract_locations(text))
        result['deal_stages'].extend(self._extract_deal_stages(text))

        return result

    def _extract_companies(self, text: str) -> List[str]:
        """Extract company names using patterns"""
        companies = []

        # Pattern 0: Known company brands (highest priority, check first)
        # This is important for Chinese tech companies that might not match other patterns
        known_brands = [
            r'\bByteDance\b', r'字节跳动',
            r'\bTikTok\b', r'抖音',
            r'\bAlibaba\b', r'阿里',
            r'\bTencent\b', r'腾讯',
            r'\bMeituan\b', r'美团',
            r'\bDidi\b', r'滴滴',
            r'\bXiaomi\b', r'小米',
            r'\bHuawei\b', r'华为',
            r'\bKuaishou\b', r'快手',
            r'\bPinduoduo\b', r'拼多多',
            r'\bJD\.com\b', r'京东',
            r'\bBilibili\b', r'\bB站\b',
            r'\bAnt Group\b', r'蚂蚁集团',
            r'\bEle\.me\b', r'饿了么',
        ]

        for brand in known_brands:
            matches = re.findall(brand, text, re.IGNORECASE)
            companies.extend(matches)

        # Pattern 1: Company name + suffix
        for suffix in self.COMPANY_SUFFIXES:
            # Company Name + Suffix
            pattern = rf'\b[A-Z][A-Za-z\u4e00-\u9fff0-9\s&]+(?:{re.escape(suffix)})\b'
            matches = re.findall(pattern, text, re.IGNORECASE)
            companies.extend(matches)

        # Pattern 2: Chinese companies (consecutive Chinese chars + company suffix)
        if has_chinese(text):
            # Broader pattern for Chinese companies
            cn_patterns = [
                r'[\u4e00-\u9fff]{2,12}(?:公司|科技|集团|有限|股份|企业)',
                r'[\u4e00-\u9fff]{2,12}(?:网络|科技|信息技术|智能|数据)',
            ]
            for cn_pattern in cn_patterns:
                matches = re.findall(cn_pattern, text)
                companies.extend(matches)

        return list(set([c.strip() for c in companies if c.strip()]))

    def _extract_investors(self, text: str) -> List[str]:
        """Extract investor/VC firm names"""
        investors = []

        # Known VC firms (highest priority)
        known_vcs = [
            r'\bSequoia Capital\b', r'红杉资本',
            r'\bIDG Capital\b', r'\bIDG\b',
            r'\bMatrix Partners China\b', r'经纬中国', r'经纬',
            r'\bZhenFund\b', r'真格基金',
            r'\bQiming Venture Partners\b', r'启明创投',
            r'\bDCM Ventures\b', r'\bDCM\b',
            r'\bHillhouse Capital\b', r'高瓴资本',
            r'\bSinovation Ventures\b', r'创新工场',
            r'\bGaorong Capital\b', r'高榕资本',
            r'\bAngelplus\b',
            r'\bDST\b', r'DST',
        ]

        for vc in known_vcs:
            matches = re.findall(vc, text, re.IGNORECASE)
            investors.extend(matches)

        # Pattern: Investor name + investor suffix
        for suffix in self.INVESTOR_SUFFIXES:
            pattern = rf'[A-Z][A-Za-z\u4e00-\u9fff\s&]+(?:{re.escape(suffix)})\b'
            matches = re.findall(pattern, text, re.IGNORECASE)
            investors.extend(matches)

        # Chinese VC firms
        if has_chinese(text):
            cn_patterns = [
                r'[\u4e00-\u9fff]{2,8}(?:资本|创投|投资|基金|管理|资产)',
                r'[\u4e00-\u9fff]{2,8}(?:资本|创投|投资|基金)',
            ]
            for cn_pattern in cn_patterns:
                matches = re.findall(cn_pattern, text)
                investors.extend(matches)

        return list(set([i.strip() for i in investors if i.strip()]))

    def _extract_persons(self, text: str) -> List[str]:
        """Extract person names"""
        persons = []

        # Pattern: Title + Name (common in VC/PE news)
        title_pattern = r'(?:CEO|Founder|Co-Founder|CTO|CFO|President|Director|合伙人|创始人|CEO|董事长|总裁|总监)\s+[A-Z][A-Za-z\u4e00-\u9fff\s]{2,20}'
        matches = re.findall(title_pattern, text)
        persons.extend([m.split()[-1] if ' ' in m else m for m in matches])

        # Chinese names (2-4 Chinese characters)
        if has_chinese(text):
            cn_pattern = r'[\u4e00-\u9fff]{2,4}(?:，|。|、|说|表示|认为|宣布)'
            matches = re.findall(cn_pattern, text)
            # Remove the punctuation
            persons.extend([m[:-1] for m in matches])

        return list(set([p.strip() for p in persons if p.strip()]))

    def _extract_amounts(self, text: str) -> List[dict]:
        """Extract investment amounts with currency"""
        amounts = []

        # Pattern 1: Symbol + number + unit
        # Examples: $100M, €50B, ¥1.5亿
        symbol_patterns = [
            r'[\$€£¥]\s*(\d+(?:\.\d+)?)\s*(K|M|B|T|k|m|b|t|万|亿|千)?',  # $100M
            r'(\d+(?:\.\d+)?)\s*(K|M|B|T|k|m|b|t|万|亿|千)\s*(?:USD|EUR|GBP|CNY|HKD)?',  # 100M USD
        ]

        for pattern in symbol_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    amount_dict = self._parse_amount_match(match, text)
                    if amount_dict:
                        amounts.append(amount_dict)
                except:
                    continue

        # Pattern 2: Chinese format (数字+单位+货币)
        if has_chinese(text):
            chinese_amounts = extract_chinese_amount(text)
            amounts.extend(chinese_amounts)

        # Pattern 3: Written format
        # Examples: 100 million dollars, 1.5 billion euros
        written_pattern = r'(\d+(?:\.\d+)?)\s*(million|billion|trillion|thousand)\s*(dollars?|euros?|pounds?|yuan|USD|EUR|GBP|CNY)?'
        matches = re.finditer(written_pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                amount_dict = self._parse_written_amount(match, text)
                if amount_dict:
                    amounts.append(amount_dict)
            except:
                continue

        return amounts

    def _parse_amount_match(self, match, text) -> Optional[dict]:
        """Parse amount regex match"""
        full_match = match.group(0)

        # Extract number and unit
        if len(match.groups()) >= 2:
            number = float(match.group(1))
            unit = match.group(2) if match.group(2) else ''

            # Normalize unit
            unit_multiplier = {
                'K': 1e3, 'k': 1e3, '千': 1e3,
                'M': 1e6, 'm': 1e6, '万': 1e4,
                'B': 1e9, 'b': 1e9, '亿': 1e8,
                'T': 1e12, 't': 1e12
            }

            multiplier = unit_multiplier.get(unit, 1)
            amount = number * multiplier

            # Detect currency
            currency = self._detect_currency(full_match)

            return {
                'amount': amount,
                'currency': currency,
                'original_text': full_match,
                'normalized': f'{amount:,.0f} {currency}'
            }

        return None

    def _parse_written_amount(self, match, text) -> Optional[dict]:
        """Parse written amount (e.g., '100 million dollars')"""
        number = float(match.group(1))
        unit_word = match.group(2).lower()
        currency_word = match.group(3)

        # Convert unit word to multiplier
        unit_multipliers = {
            'thousand': 1e3,
            'million': 1e6,
            'billion': 1e9,
            'trillion': 1e12
        }

        multiplier = unit_multipliers.get(unit_word, 1)
        amount = number * multiplier

        # Detect currency
        if currency_word:
            currency_map = {
                'dollars': 'USD', 'dollar': 'USD',
                'euros': 'EUR', 'euro': 'EUR',
                'pounds': 'GBP', 'pound': 'GBP',
                'yuan': 'CNY'
            }
            currency = currency_map.get(currency_word.lower(), 'USD')
        else:
            currency = self._detect_currency(match.group(0))

        return {
            'amount': amount,
            'currency': currency,
            'original_text': match.group(0),
            'normalized': f'{amount:,.0f} {currency}'
        }

    def _detect_currency(self, text: str) -> str:
        """Detect currency from text"""
        text_lower = text.lower()

        currency_map = {
            'usd': 'USD', 'dollar': 'USD', '$': 'USD', '美元': 'USD',
            'cny': 'CNY', 'yuan': 'CNY', '¥': 'CNY', '￥': 'CNY', '人民币': 'CNY',
            'eur': 'EUR', 'euro': 'EUR', '€': 'EUR', '欧元': 'EUR',
            'gbp': 'GBP', 'pound': 'GBP', '£': 'GBP', '英镑': 'GBP',
            'hkd': 'HKD', '港币': 'HKD',
            'jpy': 'JPY', 'yen': 'JPY', '日元': 'JPY',
            'sgd': 'SGD', '新加坡元': 'SGD'
        }

        for symbol, code in currency_map.items():
            if symbol in text_lower:
                return code

        return 'USD'  # Default to USD

    def _extract_dates(self, text: str) -> List[dict]:
        """Extract dates from text"""
        dates = extract_dates_from_text(text)
        return dates

    def _extract_locations(self, text: str) -> List[str]:
        """Extract geographic locations"""
        locations = []

        # Common locations in VC/PE news
        known_locations = [
            r'\bSilicon Valley\b', r'\bNew York\b', r'\bSan Francisco\b',
            r'\bBeijing\b', r'\bShanghai\b', r'\bShenzhen\b', r'\bHangzhou\b',
            r'\b北京\b', r'\b上海\b', r'\b深圳\b', r'\b杭州\b',
            r'\bSingapore\b', r'\b新加坡\b',
            r'\bLondon\b', r'\bLondon\b', r'\b伦敦\b',
            r'\bHong Kong\b', r'\b香港\b',
            r'\bTokyo\b', r'\b东京\b',
        ]

        for loc in known_locations:
            matches = re.findall(loc, text, re.IGNORECASE)
            locations.extend(matches)

        return list(set(locations))

    def _extract_deal_stages(self, text: str) -> List[str]:
        """Extract deal stages/rounds"""
        found_stages = []

        text_lower = text.lower()

        for stage in self.DEAL_STAGES:
            if stage.lower() in text_lower:
                found_stages.append(stage)

        return list(set(found_stages))

    def _is_investor(self, entity_text: str) -> bool:
        """Check if entity is likely an investor/VC firm"""
        entity_lower = entity_text.lower()

        for suffix in self.INVESTOR_SUFFIXES:
            if suffix.lower() in entity_lower:
                return True

        return False


# Demo and testing
if __name__ == "__main__":
    # Test the extractor
    extractor = FinancialEntityExtractor(use_spacy=False)

    test_text = """
    红杉资本投资了字节跳动公司C轮，投资金额为2亿美元。
    Sequoia Capital led the Series C round of ByteDance with $200 million investment.
    创新工场投资了快手，金额达到1.5亿人民币。
    """

    entities = extractor.extract_entities(test_text)

    print("="*70)
    print("Entity Extraction Test")
    print("="*70)

    for entity_type, entity_list in entities.items():
        if entity_list:
            print(f"\n{entity_type.upper()}:")
            for entity in entity_list:
                if isinstance(entity, dict):
                    print(f"  - {entity}")
                else:
                    print(f"  - {entity}")
