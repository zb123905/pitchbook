"""
NLP Entity Recognition System Test Suite
Tests for Phase 2: Intelligent Entity Recognition
"""
import os
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp.entity_extractor import FinancialEntityExtractor
from nlp.relation_extractor import InvestmentRelationExtractor
from content_analyzer import VCPEContentAnalyzer


# Test data - realistic VC/PE industry content
TEST_SAMPLES = [
    {
        'name': 'Chinese Investment Round',
        'text': '''
        红杉资本领投了字节跳动的C轮融资，投资金额为2亿美元。
        高瓴资本和经纬中国跟投，本轮融资总额达到5亿美元。
        估值达到2000亿元人民币。

        创始人张一鸣表示，资金将用于海外扩张和技术研发。
        北京时间2024年3月15日，公司宣布完成此轮融资。
        '''
    },
    {
        'name': 'English Investment Round',
        'text': '''
        Sequoia Capital led the Series C round of ByteDance with $200 million investment.
        Hillhouse Capital and Matrix Partners China participated in the round,
        bringing the total funding to $500 million at a valuation of $20 billion.

        Founder Zhang Yiming stated that the funds will be used for
        international expansion and R&D. The company announced the
        completion of this round on March 15, 2024.
        '''
    },
    {
        'name': 'M&A Deal',
        'text': '''
        阿里巴巴宣布收购饿了么，交易金额为95亿美元。
        此次并购完成后，饿了么将成为阿里巴巴全资子公司。
        交易预计于2018年第四季度完成。

        Alibaba announced the acquisition of Ele.me for $9.5 billion.
        Upon completion of the merger, Ele.me will become a wholly-owned
        subsidiary of Alibaba. The transaction is expected to close in Q4 2018.
        '''
    },
    {
        'name': 'Multi-Stage Funding',
        'text': '''
        快手先后完成了种子轮、A轮、B轮和D轮融资。
        创新工场投资了种子轮，金额为100万美元。
        DST投资了B轮，金额为1亿美元。
        红杉资本领投D轮，金额达到10亿美元。

        上市前估值约为300亿美元。
        '''
    },
    {
        'name': 'Partnership Deal',
        'text': '''
        腾讯与京东达成战略合作，双方将在电商和支付领域展开深度合作。
        Tencent and JD.com announced a strategic partnership to collaborate
        in e-commerce and payment sectors.
        '''
    }
]


def test_entity_extractor():
    """Test entity extraction functionality"""
    print("\n" + "="*70)
    print("Test 1: Entity Extractor")
    print("="*70)

    extractor = FinancialEntityExtractor(use_spacy=False)

    total_entities = {
        'companies': 0,
        'amounts': 0,
        'investors': 0,
        'persons': 0,
        'dates': 0,
        'deal_stages': 0
    }

    for sample in TEST_SAMPLES:
        print(f"\n📄 Testing: {sample['name']}")
        print("-" * 70)

        entities = extractor.extract_entities(sample['text'])

        for entity_type, entity_list in entities.items():
            if entity_list:
                count = len(entity_list) if isinstance(entity_list, list) else 1
                total_entities[entity_type] += count
                print(f"  ✓ {entity_type}: {count}")

                # Show first few entities
                if isinstance(entity_list, list):
                    for entity in entity_list[:3]:
                        if isinstance(entity, dict):
                            print(f"      - {entity.get('original_text', entity)}")
                        else:
                            print(f"      - {entity}")
                    if len(entity_list) > 3:
                        print(f"      ... and {len(entity_list) - 3} more")

    print("\n" + "="*70)
    print("Entity Extraction Summary")
    print("="*70)
    for entity_type, count in total_entities.items():
        print(f"  {entity_type}: {count} total")

    return total_entities


def test_relation_extractor():
    """Test relationship extraction functionality"""
    print("\n" + "="*70)
    print("Test 2: Relation Extractor")
    print("="*70)

    extractor = InvestmentRelationExtractor()

    total_relations = 0
    total_deals = 0

    for sample in TEST_SAMPLES:
        print(f"\n📄 Testing: {sample['name']}")
        print("-" * 70)

        # Extract relations
        relations = extractor.extract_relations(sample['text'])
        total_relations += len(relations)

        print(f"  Relations found: {len(relations)}")
        for idx, relation in enumerate(relations[:3], 1):
            print(f"    {idx}. {relation.get('type', 'unknown').upper()}")
            if relation.get('type') == 'investment':
                print(f"       {relation.get('investor', 'N/A')} → {relation.get('target', 'N/A')}")
                if relation.get('stage'):
                    print(f"       Stage: {relation['stage']}")
                if relation.get('amount'):
                    print(f"       Amount: {relation['amount'].get('normalized', 'N/A')}")
            elif relation.get('type') == 'ma':
                print(f"       {relation.get('acquirer', 'N/A')} acquired {relation.get('target', 'N/A')}")
            elif relation.get('type') == 'partnership':
                print(f"       {relation.get('company_a', 'N/A')} ↔ {relation.get('company_b', 'N/A')}")

        # Extract deals
        deals = extractor.extract_deals(sample['text'])
        total_deals += len(deals)

        print(f"\n  Deals found: {len(deals)}")
        for idx, deal in enumerate(deals[:2], 1):
            print(f"    {idx}. {deal.get('company', 'Unknown')} - {deal.get('stage', 'Unknown Round')}")
            print(f"       Investors: {', '.join(deal.get('investors', [])[:3])}")
            if deal.get('amount'):
                print(f"       Amount: {deal['amount'].get('normalized', 'N/A')}")

    print("\n" + "="*70)
    print("Relation Extraction Summary")
    print("="*70)
    print(f"  Total relations: {total_relations}")
    print(f"  Total deals: {total_deals}")

    return {'relations': total_relations, 'deals': total_deals}


def test_content_analyzer_integration():
    """Test integration with content analyzer"""
    print("\n" + "="*70)
    print("Test 3: Content Analyzer Integration")
    print("="*70)

    analyzer = VCPEContentAnalyzer(use_nlp=True)

    # Create mock email data
    mock_email = {
        'subject': '红杉资本投资字节跳动C轮',
        'from': 'news@pitchbook.com',
        'date': '2024-03-15',
        'body': TEST_SAMPLES[0]['text'],
        'links': [],
        'source_file': 'test.eml'
    }

    analyses = analyzer.analyze_batch([mock_email])

    print(f"\n✓ Analyzed {len(analyses)} email(s)")

    for analysis in analyses:
        print(f"\n  Subject: {analysis.get('subject', 'N/A')}")

        # Check for NLP enhancements
        if 'entities' in analysis:
            entities = analysis['entities']
            print(f"  ✓ NLP entities extracted:")
            print(f"    - Companies: {len(entities.get('companies', []))}")
            print(f"    - Investors: {len(entities.get('investors', []))}")
            print(f"    - Amounts: {len(entities.get('amounts', []))}")
            print(f"    - Deal stages: {len(entities.get('deal_stages', []))}")

        if 'relations' in analysis:
            print(f"  ✓ Relations extracted: {len(analysis['relations'])}")

        if 'investment_deals' in analysis:
            print(f"  ✓ Structured deals: {len(analysis['investment_deals'])}")

        if 'nlp_metrics' in analysis:
            print(f"  ✓ NLP metrics: {analysis['nlp_metrics']}")

    return analyses


def test_accuracy():
    """Test extraction accuracy against expected results"""
    print("\n" + "="*70)
    print("Test 4: Accuracy Validation")
    print("="*70)

    extractor = FinancialEntityExtractor(use_spacy=False)

    # Expected results for validation
    test_case = TEST_SAMPLES[0]  # Chinese Investment Round

    expected_companies = ['字节跳动']
    expected_investors = ['红杉资本', '高瓴资本', '经纬中国']
    expected_amounts = 3  # 2亿美元, 5亿美元, 2000亿人民币
    expected_stages = ['C轮']

    entities = extractor.extract_entities(test_case['text'])

    print(f"\n📄 Testing: {test_case['name']}")

    # Validate companies
    found_companies = entities.get('companies', [])
    company_match_rate = len([c for c in expected_companies if any(c in fc for fc in found_companies)]) / len(expected_companies)
    print(f"\n  Company Recognition: {company_match_rate*100:.0f}%")
    print(f"    Expected: {expected_companies}")
    print(f"    Found: {found_companies[:5]}")

    # Validate investors
    found_investors = entities.get('investors', [])
    investor_match_rate = len([i for i in expected_investors if any(i in fi for fi in found_investors)]) / len(expected_investors)
    print(f"\n  Investor Recognition: {investor_match_rate*100:.0f}%")
    print(f"    Expected: {expected_investors}")
    print(f"    Found: {found_investors[:5]}")

    # Validate amounts
    found_amounts = entities.get('amounts', [])
    amount_match = len(found_amounts) >= expected_amounts
    print(f"\n  Amount Recognition: {'✓ PASS' if amount_match else '✗ FAIL'}")
    print(f"    Expected at least: {expected_amounts}")
    print(f"    Found: {len(found_amounts)}")
    for amt in found_amounts[:3]:
        print(f"      - {amt.get('normalized', amt)}")

    # Validate deal stages
    found_stages = entities.get('deal_stages', [])
    stage_match = any(s in found_stages for s in expected_stages)
    print(f"\n  Deal Stage Recognition: {'✓ PASS' if stage_match else '✗ FAIL'}")
    print(f"    Expected: {expected_stages}")
    print(f"    Found: {found_stages}")

    # Calculate overall accuracy
    overall_accuracy = (company_match_rate + investor_match_rate + (1.0 if amount_match else 0) + (1.0 if stage_match else 0)) / 4

    print(f"\n  Overall Accuracy: {overall_accuracy*100:.0f}%")

    # Performance target check
    targets = {
        'company_target': company_match_rate >= 0.85,
        'investor_target': investor_match_rate >= 0.85,
        'amount_target': amount_match,
        'stage_target': stage_match
    }

    print("\n  Target Achievement:")
    for target, passed in targets.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"    {target}: {status}")

    all_passed = all(targets.values())
    print(f"\n  {'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")

    return overall_accuracy, all_passed


def save_test_results(results: dict):
    """Save test results to JSON file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data',
        f'nlp_test_results_{timestamp}.json'
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Test results saved to: {output_path}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("VC/PE NLP Entity Recognition System - Test Suite")
    print("Phase 2: Intelligent Entity Recognition")
    print("="*70)

    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }

    try:
        # Test 1: Entity Extraction
        entity_results = test_entity_extractor()
        results['tests']['entity_extraction'] = entity_results

        # Test 2: Relation Extraction
        relation_results = test_relation_extractor()
        results['tests']['relation_extraction'] = relation_results

        # Test 3: Content Analyzer Integration
        analyzer_results = test_content_analyzer_integration()
        results['tests']['analyzer_integration'] = {
            'analyses_count': len(analyzer_results),
            'has_nlp_features': bool(analyzer_results and 'entities' in analyzer_results[0])
        }

        # Test 4: Accuracy Validation
        accuracy, all_passed = test_accuracy()
        results['tests']['accuracy'] = {
            'overall_accuracy': accuracy,
            'all_passed': all_passed
        }

        # Final summary
        print("\n" + "="*70)
        print("Test Suite Summary")
        print("="*70)

        print(f"\n✓ Entity Extraction: {sum(entity_results.values())} entities extracted")
        print(f"✓ Relation Extraction: {relation_results['relations']} relations, {relation_results['deals']} deals")
        print(f"✓ Integration Test: {'PASSED' if analyzer_results else 'FAILED'}")
        print(f"✓ Accuracy Test: {accuracy*100:.0f}% - {'PASSED' if all_passed else 'FAILED'}")

        final_status = "✓ ALL TESTS PASSED" if all_passed else "⚠ SOME TESTS FAILED"
        print(f"\n{final_status}")

        # Save results
        results['final_status'] = 'PASSED' if all_passed else 'FAILED'
        save_test_results(results)

        return all_passed

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

        results['error'] = str(e)
        results['final_status'] = 'ERROR'
        save_test_results(results)

        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
