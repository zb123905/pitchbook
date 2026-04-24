"""
Repository pattern for data access layer
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from urllib.parse import urlparse
import logging

from database.models import (
    Email, EmailLink, EmailAttachment, DownloadedReport,
    ExtractedContent, AnalysisResult, ScrapedWebContent,
    MarketOverview, ProcessingLog
)

logger = logging.getLogger(__name__)


class EmailRepository:
    """Repository for Email operations"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, email_data: Dict[str, Any]) -> Email:
        """Create a new email record"""
        email = Email(
            message_id=email_data.get('message_id'),
            subject=email_data.get('subject', ''),
            from_address=email_data.get('from', ''),
            date_sent=self._parse_date(email_data.get('date')),
            body_text=email_data.get('body', ''),
            body_html=email_data.get('html_body', ''),
            source_file=email_data.get('source_file', '')
        )
        self.session.add(email)
        self.session.flush()  # Get the ID
        return email

    def get_by_message_id(self, message_id: str) -> Optional[Email]:
        """Get email by Outlook message ID"""
        return self.session.query(Email).filter(
            Email.message_id == message_id
        ).first()

    def get_by_id(self, email_id: int) -> Optional[Email]:
        """Get email by primary key ID"""
        return self.session.query(Email).filter(Email.id == email_id).first()

    def get_recent(self, limit: int = 50, offset: int = 0) -> List[Email]:
        """Get recent emails"""
        return self.session.query(Email).order_by(
            Email.date_sent.desc()
        ).offset(offset).limit(limit).all()

    def search(self, query: str, limit: int = 50) -> List[Email]:
        """Full-text search emails"""
        return self.session.query(Email).filter(
            Email.subject.ilike(f'%{query}%')
        ).order_by(Email.date_sent.desc()).limit(limit).all()

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse email date string to datetime"""
        if not date_str:
            return None
        try:
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
        except Exception:
            return None


class EmailLinkRepository:
    """Repository for EmailLink operations"""

    def __init__(self, session: Session):
        self.session = session

    def create_batch(self, email_id: int, links: List[Dict[str, Any]]) -> List[EmailLink]:
        """Create multiple links for an email"""
        link_objects = []
        for link_data in links:
            url = link_data.get('url', '')
            link = EmailLink(
                email_id=email_id,
                url=url,
                link_text=link_data.get('text', ''),
                domain=self._extract_domain(url),
                link_type=self._classify_link(url),
                is_pitchbook='pitchbook.com' in url.lower()
            )
            link_objects.append(link)

        self.session.add_all(link_objects)
        self.session.flush()
        return link_objects

    def get_pitchbook_links(self, email_id: int) -> List[EmailLink]:
        """Get all PitchBook links for an email"""
        return self.session.query(EmailLink).filter(
            EmailLink.email_id == email_id,
            EmailLink.is_pitchbook == True
        ).all()

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            return urlparse(url).netloc
        except Exception:
            return ''

    def _classify_link(self, url: str) -> str:
        """Classify link type"""
        url_lower = url.lower()
        if 'pitchbook.com' in url_lower:
            return 'pitchbook'
        elif any(ext in url_lower for ext in ['.pdf', '.xlsx', '.docx']):
            return 'attachment'
        else:
            return 'external'


class EmailAttachmentRepository:
    """Repository for EmailAttachment operations"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, attachment_data: Dict[str, Any]) -> EmailAttachment:
        """Create an attachment record"""
        attachment = EmailAttachment(
            email_id=attachment_data.get('email_id'),
            filename=attachment_data.get('filename', ''),
            file_size_bytes=attachment_data.get('size'),
            content_type=attachment_data.get('content_type', 'application/octet-stream'),
            file_path=attachment_data.get('file_path', '')
        )
        self.session.add(attachment)
        self.session.flush()
        return attachment


class DownloadedReportRepository:
    """Repository for DownloadedReport operations"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, report_data: Dict[str, Any]) -> DownloadedReport:
        """Create a downloaded report record"""
        report = DownloadedReport(
            link_id=report_data.get('link_id'),
            url=report_data.get('url', ''),
            filename=report_data.get('filename', ''),
            file_path=report_data.get('filepath', ''),
            file_size_bytes=report_data.get('file_size_bytes'),
            content_type=report_data.get('content_type', 'application/pdf'),
            download_status=report_data.get('download_status', 'success'),
            error_message=report_data.get('error_message'),
            download_started_at=report_data.get('download_started_at'),
            download_completed_at=datetime.now()
        )
        self.session.add(report)
        self.session.flush()
        return report

    def get_by_status(self, status: str, limit: int = 100) -> List[DownloadedReport]:
        """Get reports by download status"""
        return self.session.query(DownloadedReport).filter(
            DownloadedReport.download_status == status
        ).order_by(DownloadedReport.created_at.desc()).limit(limit).all()

    def mark_failed(self, report_id: int, error_message: str):
        """Mark a report as failed"""
        report = self.session.query(DownloadedReport).filter(
            DownloadedReport.id == report_id
        ).first()
        if report:
            report.download_status = 'failed'
            report.error_message = error_message
            report.download_completed_at = datetime.now()

    def get_by_url(self, url: str) -> Optional[DownloadedReport]:
        """Check if report URL already exists (for deduplication)"""
        return self.session.query(DownloadedReport).filter(
            DownloadedReport.url == url
        ).first()

    def get_all_downloaded_urls(self, limit: int = 1000) -> set:
        """Get set of all successfully downloaded URLs"""
        reports = self.session.query(DownloadedReport).filter(
            DownloadedReport.download_status == 'success'
        ).limit(limit).all()
        return set(r.url for r in reports)


class AnalysisResultRepository:
    """Repository for AnalysisResult operations"""

    def __init__(self, session: Session):
        self.session = session

    def create_from_analysis(self, analysis_data: Dict[str, Any]) -> AnalysisResult:
        """Create analysis result from analyzer output"""
        result = AnalysisResult(
            email_id=analysis_data.get('email_id'),
            report_id=analysis_data.get('report_id'),
            scraped_content_id=analysis_data.get('scraped_content_id'),
            content_type=analysis_data.get('content_type'),
            categories=analysis_data.get('categories'),
            key_topics=analysis_data.get('key_topics'),
            content_classification=analysis_data.get('content_type'),
            metrics=analysis_data.get('metrics'),
            entities=analysis_data.get('entities'),
            relations=analysis_data.get('relations'),
            investment_deals=analysis_data.get('investment_deals'),
            nlp_metrics=analysis_data.get('nlp_metrics'),
            llm_analysis=analysis_data.get('llm_analysis'),
            llm_quality_score=analysis_data.get('llm_quality_score')
        )
        self.session.add(result)
        self.session.flush()
        return result

    def get_by_date_range(self, start_date: date, end_date: date) -> List[AnalysisResult]:
        """Get analyses within date range"""
        return self.session.query(AnalysisResult).filter(
            AnalysisResult.analyzed_at >= start_date,
            AnalysisResult.analyzed_at <= end_date
        ).order_by(AnalysisResult.analyzed_at.desc()).all()


class ExtractedContentRepository:
    """Repository for ExtractedContent operations"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, content_data: Dict[str, Any]) -> ExtractedContent:
        """Create extracted content record"""
        content = ExtractedContent(
            report_id=content_data.get('report_id'),
            content_type=content_data.get('content_type'),
            raw_content=content_data.get('raw_content', ''),
            word_count=content_data.get('word_count', 0)
        )
        self.session.add(content)
        self.session.flush()
        return content
