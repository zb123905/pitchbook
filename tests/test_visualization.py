"""
Visualization System Test Suite
Tests for Phase 3: Data Visualization and Trend Analysis
"""
import os
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Test data with realistic VC/PE content
TEST_ANALYSES = [
    {
        'email_index': 1,
        'subject': '红杉资本投资字节跳动C轮',
        'from': 'news@pitchbook.com',
        'date': '2024-03-15',
        'key_topics': ['AI/Machine Learning', 'FinTech'],
        'categories': ['VC', 'AI/ML'],
        'content_type': 'Deal Announcement',
        'links': [],
        'source_file': 'email1.eml',

        # NLP entities (Phase 2)
        'entities': {
            'companies': ['字节跳动', 'ByteDance'],
            'investors': ['红杉资本', 'Sequoia Capital', '高瓴资本', 'Hillhouse Capital'],
            'amounts': [
                {'amount': 200000000, 'currency': 'USD', 'normalized': '$200M'},
                {'amount': 500000000, 'currency': 'USD', 'normalized': '$500M'}
            ],
            'deal_stages': ['C轮', 'Series C']
        },

        # NLP relations (Phase 2)
        'relations': [
            {
                'type': 'investment',
                'investor': '红杉资本',
                'target': '字节跳动',
                'stage': 'C轮',
                'amount': {'amount': 200000000, 'currency': 'USD', 'normalized': '$200M'},
                'date': '2024-03-15',
                'confidence': 0.9,
                'text': '红杉资本领投了字节跳动C轮融资'
            },
            {
                'type': 'investment',
                'investor': 'Hillhouse Capital',
                'target': 'ByteDance',
                'stage': 'Series C',
                'amount': {'amount': 500000000, 'currency': 'USD', 'normalized': '$500M'},
                'date': '2024-03-15',
                'confidence': 0.9,
                'text': 'Hillhouse Capital participated in Series C round'
            }
        ],

        # Structured deals (Phase 2)
        'investment_deals': [
            {
                'company': '字节跳动',
                'investors': ['红杉资本', '高瓴资本'],
                'lead_investor': '红杉资本',
                'stage': 'C轮',
                'amount': {'amount': 200000000, 'currency': 'USD', 'normalized': '$200M'},
                'date': '2024-03-15',
                'description': '红杉资本领投了字节跳动C轮融资',
                'confidence': 0.9
            }
        ],

        'nlp_metrics': {
            'entity_count': 15,
            'relation_count': 2,
            'deal_count': 1,
            'company_count': 2,
            'amount_count': 2
        }
    },
    {
        'email_index': 2,
        'subject': '创新工场投资快手',
        'from': 'news@pitchbook.com',
        'date': '2024-02-20',
        'key_topics': ['E-commerce', 'Social Media'],
        'categories': ['VC'],
        'content_type': 'Deal Announcement',
        'links': [],
        'source_file': 'email2.eml',

        'entities': {
            'companies': ['快手', 'Kuaishou'],
            'investors': ['创新工场', 'Sinovation Ventures', 'DST'],
            'amounts': [
                {'amount': 1000000, 'currency': 'USD', 'normalized': '$1M'},
                {'amount': 100000000, 'currency': 'USD', 'normalized': '$100M'}
            ],
            'deal_stages': ['种子轮', 'Series B']
        },

        'relations': [
            {
                'type': 'investment',
                'investor': '创新工场',
                'target': '快手',
                'stage': '种子轮',
                'amount': {'amount': 1000000, 'currency': 'USD', 'normalized': '$1M'},
                'date': '2024-02-20',
                'confidence': 0.8,
                'text': '创新工场投资快手种子轮'
            },
            {
                'type': 'investment',
                'investor': 'DST',
                'target': 'Kuaishou',
                'stage': 'Series B',
                'amount': {'amount': 100000000, 'currency': 'USD', 'normalized': '$100M'},
                'date': '2024-02-20',
                'confidence': 0.85,
                'text': 'DST投资快手B轮'
            }
        ],

        'investment_deals': [
            {
                'company': '快手',
                'investors': ['创新工场'],
                'lead_investor': '创新工场',
                'stage': '种子轮',
                'amount': {'amount': 1000000, 'currency': 'USD', 'normalized': '$1M'},
                'date': '2024-02-20',
                'description': '创新工场投资快手种子轮',
                'confidence': 0.8
            }
        ],

        'nlp_metrics': {
            'entity_count': 10,
            'relation_count': 2,
            'deal_count': 2,
            'company_count': 2,
            'amount_count': 2
        }
    },
    {
        'email_index': 3,
        'subject': '阿里巴巴收购饿了么',
        'from': 'news@pitchbook.com',
        'date': '2024-01-10',
        'key_topics': ['E-commerce', 'M&A', 'Food Delivery'],
        'categories': ['PE', 'M&A'],
        'content_type': 'Deal Announcement',
        'links': [],
        'source_file': 'email3.eml',

        'entities': {
            'companies': ['阿里巴巴', 'Alibaba', '饿了么', 'Ele.me'],
            'investors': [],
            'amounts': [
                {'amount': 9500000000, 'currency': 'USD', 'normalized': '$9.5B'}
            ],
            'deal_stages': ['Acquisition', '收购', '并购']
        },

        'relations': [
            {
                'type': 'ma',
                'acquirer': '阿里巴巴',
                'target': '饿了么',
                'amount': {'amount': 9500000000, 'currency': 'USD', 'normalized': '$9.5B'},
                'date': '2024-01-10',
                'confidence': 0.95,
                'text': '阿里巴巴收购饿了么'
            }
        ],

        'investment_deals': [],

        'nlp_metrics': {
            'entity_count': 8,
            'relation_count': 1,
            'deal_count': 0,
            'company_count': 4,
            'amount_count': 1
        }
    }
]


def test_chart_config():
    """Test chart configuration"""
    print("\n" + "="*70)
    print("Test 1: Chart Configuration")
    print("="*70)

    from visualization.chart_config import (
        setup_chinese_font,
        get_color_for_label,
        apply_chart_style,
        COLOR_SCHEMES
    )

    # Test Chinese font setup
    font_ok = setup_chinese_font()
    print(f"\n✓ Chinese font setup: {'SUCCESS' if font_ok else 'WARNING - Font may not display correctly'}")

    # Test color schemes
    print(f"\n✓ Color schemes loaded:")
    for scheme_name in COLOR_SCHEMES.keys():
        print(f"  - {scheme_name}: {len(COLOR_SCHEMES[scheme_name])} colors")

    # Test color retrieval
    test_label = 'AI/Machine Learning'
    color = get_color_for_label(test_label, 'industry')
    print(f"\n✓ Color for '{test_label}': {color}")

    return True


def test_investment_network():
    """Test investment network generation"""
    print("\n" + "="*70)
    print("Test 2: Investment Network Generator")
    print("="*70)

    from visualization.investment_network import InvestmentNetworkGenerator

    generator = InvestmentNetworkGenerator()

    # Extract relations from test data
    all_relations = []
    for analysis in TEST_ANALYSES:
        all_relations.extend(analysis.get('relations', []))

    print(f"\n📊 Testing with {len(all_relations)} relations")

    # Generate network
    output_path = 'E:/pitch/数据储存/temp_charts/test_network.png'
    fig = generator.generate_network_graph(
        all_relations,
        output_path=output_path,
        layout='spring'
    )

    if fig:
        print(f"✓ Network graph generated: {output_path}")
        print(f"  Nodes: Investment relationships visualized")
        print(f"  Layout: Spring layout with weighted edges")

        # Check if file was created
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"  File size: {file_size:,} bytes")
            return True
        else:
            print(f"  ⚠ File not created")
            return False
    else:
        print(f"✗ Failed to generate network graph")
        return False


def test_trend_analyzer():
    """Test trend analysis"""
    print("\n" + "="*70)
    print("Test 3: Market Trend Analyzer")
    print("="*70)

    from visualization.trend_analyzer import MarketTrendAnalyzer

    analyzer = MarketTrendAnalyzer()

    print(f"\n📊 Analyzing {len(TEST_ANALYSES)} analyses")

    trends = analyzer.analyze_investment_trends(TEST_ANALYSES, time_period='monthly')

    print(f"\n✓ Trend analysis completed:")
    print(f"  Total deals analyzed: {trends['total_deals_analyzed']}")
    print(f"  Timeline trends: {len(trends['timeline_trends'])} periods")
    print(f"  Hot sectors: {len(trends['hot_sectors'])} sectors")
    print(f"  Stage distribution: {len(trends['stage_distribution'])} stages")
    print(f"  Top investors: {len(trends['top_investors'])} investors")
    print(f"  Geographic distribution: {len(trends['geo_distribution'])} regions")

    # Show top results
    if trends['hot_sectors']:
        print(f"\n  Hot sectors:")
        for sector in trends['hot_sectors'][:3]:
            print(f"    - {sector['sector']}: {sector['deal_count']} deals")

    if trends['top_investors']:
        print(f"\n  Top investors:")
        for investor in trends['top_investors'][:3]:
            print(f"    - {investor['investor']}: {investor['deal_count']} deals")

    return True


def test_visualizer():
    """Test complete visualizer"""
    print("\n" + "="*70)
    print("Test 4: Report Visualizer")
    print("="*70)

    from visualization.visualizer import ReportVisualizer

    visualizer = ReportVisualizer()

    print(f"\n📊 Creating dashboard from {len(TEST_ANALYSES)} analyses")

    output_dir = 'E:/pitch/数据储存/temp_charts'
    os.makedirs(output_dir, exist_ok=True)

    charts = visualizer.create_dashboard(TEST_ANALYSES, output_dir)

    print(f"\n✓ Dashboard created with {len(charts)} charts:")

    chart_count = 0
    for chart_type, path in charts.items():
        if path and os.path.exists(path):
            file_size = os.path.getsize(path)
            print(f"  ✓ {chart_type}: {os.path.basename(path)} ({file_size:,} bytes)")
            chart_count += 1
        else:
            print(f"  ✗ {chart_type}: Failed to generate")

    success = chart_count >= 4  # At least 4 charts should be generated
    print(f"\n  {'✓ PASSED' if success else '✗ FAILED'}: {chart_count} charts generated successfully")

    return success


def test_report_integration():
    """Test integration with report generator"""
    print("\n" + "="*70)
    print("Test 5: Report Generator Integration")
    print("="*70)

    from report_generator import WeeklyReportGenerator

    # Create generator with charts enabled
    generator = WeeklyReportGenerator(enable_charts=True)

    print(f"\n✓ Report generator initialized with charts enabled")

    # Check if visualization is available
    if hasattr(generator, 'visualizer') and generator.visualizer:
        print(f"✓ Visualizer module loaded")
    else:
        print(f"✗ Visualizer module not available")
        return False

    # Check if trend analyzer is available
    if hasattr(generator, 'trend_analyzer') and generator.trend_analyzer:
        print(f"✓ Trend analyzer module loaded")
    else:
        print(f"✗ Trend analyzer module not available")
        return False

    print(f"\n✓ Report generator integration test PASSED")
    return True


def save_test_results(results: dict):
    """Save test results to JSON file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data',
        f'visualization_test_results_{timestamp}.json'
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Test results saved to: {output_path}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("VC/PE Visualization System - Test Suite")
    print("Phase 3: Data Visualization and Trend Analysis")
    print("="*70)

    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }

    try:
        # Test 1: Chart Configuration
        config_ok = test_chart_config()
        results['tests']['chart_config'] = {'passed': config_ok}

        # Test 2: Investment Network
        network_ok = test_investment_network()
        results['tests']['investment_network'] = {'passed': network_ok}

        # Test 3: Trend Analyzer
        trend_ok = test_trend_analyzer()
        results['tests']['trend_analyzer'] = {'passed': trend_ok}

        # Test 4: Visualizer
        visualizer_ok = test_visualizer()
        results['tests']['visualizer'] = {'passed': visualizer_ok}

        # Test 5: Report Integration
        integration_ok = test_report_integration()
        results['tests']['report_integration'] = {'passed': integration_ok}

        # Final summary
        print("\n" + "="*70)
        print("Test Suite Summary")
        print("="*70)

        all_tests = [
            ('Chart Configuration', config_ok),
            ('Investment Network', network_ok),
            ('Trend Analyzer', trend_ok),
            ('Visualizer', visualizer_ok),
            ('Report Integration', integration_ok)
        ]

        for test_name, passed in all_tests:
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"  {status}: {test_name}")

        all_passed = all(passed for _, passed in all_tests)
        final_status = "✓ ALL TESTS PASSED" if all_passed else "✗ SOME TESTS FAILED"
        print(f"\n{final_status}")

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
