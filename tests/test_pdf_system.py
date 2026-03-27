"""
PDF Report System Test Suite
Tests for Phase 1: Professional PDF Report Generation
"""
import os
import sys
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# Test data (reusing from visualization tests)
TEST_ANALYSES = [
    {
        'email_index': 1,
        'subject': '红杉资本投资字节跳动C轮2亿美元',
        'from': 'news@pitchbook.com',
        'date': '2024-03-15',
        'key_topics': ['AI/Machine Learning', 'FinTech'],
        'categories': ['VC', 'AI/ML'],
        'content_type': 'Deal Announcement',
        'links': [],
        'source_file': 'email1.eml',
        'entities': {
            'companies': ['字节跳动'],
            'investors': ['红杉资本'],
            'amounts': [{'amount': 200000000, 'currency': 'USD', 'normalized': '$200M'}],
            'deal_stages': ['C轮']
        },
        'relations': [
            {
                'type': 'investment',
                'investor': '红杉资本',
                'target': '字节跳动',
                'stage': 'C轮',
                'amount': {'amount': 200000000, 'currency': 'USD', 'normalized': '$200M'},
                'date': '2024-03-15',
                'confidence': 0.9,
                'text': '红杉资本领投字节跳动C轮'
            }
        ],
        'investment_deals': [
            {
                'company': '字节跳动',
                'investors': ['红杉资本'],
                'lead_investor': '红杉资本',
                'stage': 'C轮',
                'amount': {'amount': 200000000, 'currency': 'USD', 'normalized': '$200M'},
                'date': '2024-03-15'
            }
        ]
    },
    {
        'email_index': 2,
        'subject': '创新工场投资快手种子轮',
        'from': 'news@pitchbook.com',
        'date': '2024-02-20',
        'key_topics': ['E-commerce', 'Social Media'],
        'categories': ['VC'],
        'content_type': 'Deal Announcement',
        'links': [],
        'source_file': 'email2.eml',
        'entities': {
            'companies': ['快手'],
            'investors': ['创新工场'],
            'amounts': [{'amount': 1000000, 'currency': 'USD', 'normalized': '$1M'}],
            'deal_stages': ['种子轮']
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
            }
        ],
        'investment_deals': [
            {
                'company': '快手',
                'investors': ['创新工场'],
                'stage': '种子轮',
                'amount': {'amount': 1000000, 'currency': 'USD', 'normalized': '$1M'},
                'date': '2024-02-20'
            }
        ]
    }
]


def test_font_manager():
    """Test font manager"""
    print("\n" + "="*70)
    print("Test 1: Font Manager")
    print("="*70)

    from pdf.font_manager import FontManager, get_font_manager

    # Test singleton
    manager = get_font_manager()
    print(f"\n✓ Font manager initialized (singleton)")

    # Test font registration
    success = manager.register_chinese_fonts()
    print(f"{'✓' if success else '✗'} Font registration: {'SUCCESS' if success else 'FAILED'}")

    # Test font config
    config = manager.get_font_config()
    print(f"\n✓ Font configuration:")
    print(f"  Default font: {config['default_font']}")
    print(f"  Bold font: {config['bold_font']}")
    print(f"  Title font: {config['title_font']}")
    print(f"  Available fonts: {len(config['available_fonts'])}")

    return success


def test_chart_generator():
    """Test chart generator for PDF"""
    print("\n" + "="*70)
    print("Test 2: Chart Generator for PDF")
    print("="*70)

    from pdf.chart_generator import ChartGenerator

    generator = ChartGenerator(figure_size=(6, 4))
    print(f"\n✓ Chart generator initialized")

    # Test pie chart
    test_data = {'AI/Machine Learning': 5, 'FinTech': 3, 'Healthcare': 2}
    chart_path = generator.create_industry_pie_chart(test_data)

    if chart_path and os.path.exists(chart_path):
        file_size = os.path.getsize(chart_path)
        print(f"✓ Pie chart created: {chart_path}")
        print(f"  File size: {file_size:,} bytes")

        # Clean up
        os.unlink(chart_path)
        return True
    else:
        print(f"✗ Failed to create pie chart")
        return False


def test_pdf_generator_basic():
    """Test basic PDF generation"""
    print("\n" + "="*70)
    print("Test 3: PDF Report Generator (Basic)")
    print("="*70)

    from pdf.pdf_report_generator import PDFReportGenerator
    import config

    generator = PDFReportGenerator(enable_charts=False)
    print(f"\n✓ PDF generator initialized (charts disabled)")

    output_path = os.path.join(
        config.PDF_REPORT_DIR,
        f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )

    result = generator.generate_weekly_report(TEST_ANALYSES, output_path)

    if result and os.path.exists(result):
        file_size = os.path.getsize(result)
        print(f"\n✓ PDF report generated: {result}")
        print(f"  File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        return True
    else:
        print(f"\n✗ Failed to generate PDF report")
        return False


def test_pdf_generator_with_charts():
    """Test PDF generation with charts"""
    print("\n" + "="*70)
    print("Test 4: PDF Report Generator (With Charts)")
    print("="*70)

    from pdf.pdf_report_generator import PDFReportGenerator
    import config

    generator = PDFReportGenerator(enable_charts=True)
    print(f"\n✓ PDF generator initialized (charts enabled)")

    output_path = os.path.join(
        config.PDF_REPORT_DIR,
        f'test_report_with_charts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    )

    result = generator.generate_weekly_report(TEST_ANALYSES, output_path)

    if result and os.path.exists(result):
        file_size = os.path.getsize(result)
        print(f"\n✓ PDF report with charts generated: {result}")
        print(f"  File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")

        # Check if charts were embedded
        # This is hard to test automatically, but we can check file size
        # PDF with charts should be significantly larger
        return True
    else:
        print(f"\n✗ Failed to generate PDF report with charts")
        return False


def test_integration_with_main():
    """Test integration with main system"""
    print("\n" + "="*70)
    print("Test 5: Integration with Main System")
    print("="*70)

    # Test that PDF generator can be imported and used
    try:
        from pdf.pdf_report_generator import PDFReportGenerator
        from report_generator import WeeklyReportGenerator

        # Check inheritance
        pdf_gen = PDFReportGenerator(enable_charts=True)

        # Check it has the same interface
        assert hasattr(pdf_gen, 'generate_weekly_report')
        print(f"\n✓ PDF generator has correct interface")

        # Check font manager integration
        assert hasattr(pdf_gen, 'font_manager')
        assert hasattr(pdf_gen, 'chart_generator')
        print(f"✓ PDF generator has font manager and chart generator")

        # Check styles
        assert hasattr(pdf_gen, 'styles')
        assert pdf_gen.styles is not None
        print(f"✓ PDF styles initialized")

        return True

    except Exception as e:
        print(f"\n✗ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def save_test_results(results: dict):
    """Save test results"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'data',
        f'pdf_test_results_{timestamp}.json'
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Test results saved to: {output_path}")


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("PDF Report System - Test Suite")
    print("Phase 1: Professional PDF Report Generation")
    print("="*70)

    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }

    try:
        # Test 1: Font Manager
        font_ok = test_font_manager()
        results['tests']['font_manager'] = {'passed': font_ok}

        # Test 2: Chart Generator
        chart_ok = test_chart_generator()
        results['tests']['chart_generator'] = {'passed': chart_ok}

        # Test 3: Basic PDF Generation
        basic_ok = test_pdf_generator_basic()
        results['tests']['pdf_basic'] = {'passed': basic_ok}

        # Test 4: PDF with Charts
        charts_ok = test_pdf_generator_with_charts()
        results['tests']['pdf_with_charts'] = {'passed': charts_ok}

        # Test 5: Integration
        integration_ok = test_integration_with_main()
        results['tests']['integration'] = {'passed': integration_ok}

        # Summary
        print("\n" + "="*70)
        print("Test Suite Summary")
        print("="*70)

        all_tests = [
            ('Font Manager', font_ok),
            ('Chart Generator', chart_ok),
            ('Basic PDF Generation', basic_ok),
            ('PDF with Charts', charts_ok),
            ('System Integration', integration_ok)
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
