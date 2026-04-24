"""
SQLAlchemy ORM Models for VC/PE PitchBook Database
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, BigInteger, DECIMAL, Date, JSON, Index
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Email(Base):
    """邮件主表"""
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True)
    message_id = Column(String(255), unique=True, nullable=True)
    subject = Column(Text, nullable=False)
    from_address = Column(String(512))
    date_sent = Column(DateTime(timezone=True))
    date_received = Column(DateTime(timezone=True), server_default=func.now())
    body_text = Column(Text)
    body_html = Column(Text)
    source_file = Column(String(512))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    links = relationship("EmailLink", back_populates="email", cascade="all, delete-orphan")
    attachments = relationship("EmailAttachment", back_populates="email", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="email", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_emails_message_id', 'message_id'),
        Index('idx_emails_date_sent', 'date_sent'),
        Index('idx_emails_from_address', 'from_address'),
        Index('idx_emails_created_at', 'created_at'),
    )


class EmailLink(Base):
    """邮件链接表"""
    __tablename__ = 'email_links'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id', ondelete='CASCADE'))
    url = Column(Text, nullable=False)
    link_text = Column(Text)
    domain = Column(String(255))
    link_type = Column(String(50))
    is_pitchbook = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    email = relationship("Email", back_populates="links")
    downloaded_reports = relationship("DownloadedReport", back_populates="link", cascade="all, delete-orphan")
    scraped_content = relationship("ScrapedWebContent", back_populates="link", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_email_links_email_id', 'email_id'),
        Index('idx_email_links_domain', 'domain'),
        Index('idx_email_links_is_pitchbook', 'is_pitchbook'),
    )


class EmailAttachment(Base):
    """邮件附件表"""
    __tablename__ = 'email_attachments'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id', ondelete='CASCADE'))
    filename = Column(String(512), nullable=False)
    file_size_bytes = Column(BigInteger)
    content_type = Column(String(100))
    file_path = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    email = relationship("Email", back_populates="attachments")

    __table_args__ = (
        Index('idx_email_attachments_email_id', 'email_id'),
        Index('idx_email_attachments_filename', 'filename'),
    )


class DownloadedReport(Base):
    """下载报告表"""
    __tablename__ = 'downloaded_reports'

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey('email_links.id', ondelete='SET NULL'), nullable=True)
    url = Column(Text, nullable=False)
    filename = Column(String(512), nullable=False)
    file_path = Column(Text, nullable=False)
    file_size_bytes = Column(BigInteger)
    content_type = Column(String(100))
    download_status = Column(String(50), default='success')
    error_message = Column(Text)
    download_started_at = Column(DateTime(timezone=True))
    download_completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    link = relationship("EmailLink", back_populates="downloaded_reports")
    extracted_content = relationship("ExtractedContent", back_populates="report", uselist=False, cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="report", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_downloaded_reports_link_id', 'link_id'),
        Index('idx_downloaded_reports_status', 'download_status'),
        Index('idx_downloaded_reports_created_at', 'created_at'),
    )


class ExtractedContent(Base):
    """提取内容表"""
    __tablename__ = 'extracted_content'

    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey('downloaded_reports.id', ondelete='CASCADE'))
    content_type = Column(String(50))
    raw_content = Column(Text)
    word_count = Column(Integer)
    extracted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    report = relationship("DownloadedReport", back_populates="extracted_content")

    __table_args__ = (
        Index('idx_extracted_content_report_id', 'report_id'),
    )


class AnalysisResult(Base):
    """分析结果表"""
    __tablename__ = 'analysis_results'

    id = Column(Integer, primary_key=True)
    email_id = Column(Integer, ForeignKey('emails.id', ondelete='CASCADE'), nullable=True)
    report_id = Column(Integer, ForeignKey('downloaded_reports.id', ondelete='CASCADE'), nullable=True)
    scraped_content_id = Column(Integer, nullable=True)

    content_type = Column(String(50))
    analysis_version = Column(String(20), default='1.0')

    categories = Column(JSON)
    key_topics = Column(JSON)
    content_classification = Column(String(100))

    metrics = Column(JSON)
    entities = Column(JSON)
    relations = Column(JSON)
    investment_deals = Column(JSON)
    nlp_metrics = Column(JSON)

    llm_analysis = Column(JSON)
    llm_quality_score = Column(DECIMAL(3, 2))

    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    email = relationship("Email", back_populates="analysis_results")
    report = relationship("DownloadedReport", back_populates="analysis_results")

    __table_args__ = (
        Index('idx_analysis_results_email_id', 'email_id'),
        Index('idx_analysis_results_report_id', 'report_id'),
        Index('idx_analysis_results_content_type', 'content_type'),
        Index('idx_analysis_results_analyzed_at', 'analyzed_at'),
    )


class ScrapedWebContent(Base):
    """网页内容表"""
    __tablename__ = 'scraped_web_content'

    id = Column(Integer, primary_key=True)
    link_id = Column(Integer, ForeignKey('email_links.id', ondelete='SET NULL'), nullable=True)
    url = Column(Text, nullable=False)
    title = Column(Text)
    markdown_path = Column(Text)
    pdf_path = Column(Text)
    word_count = Column(Integer)
    scrape_status = Column(String(50), default='success')
    skip_reason = Column(Text)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    link = relationship("EmailLink", back_populates="scraped_content")

    __table_args__ = (
        Index('idx_scraped_web_content_link_id', 'link_id'),
        Index('idx_scraped_web_content_url', 'url'),
        Index('idx_scraped_web_content_scraped_at', 'scraped_at'),
    )


class MarketOverview(Base):
    """市场概览表"""
    __tablename__ = 'market_overviews'

    id = Column(Integer, primary_key=True)
    overview_date = Column(Date, unique=True, nullable=False)
    total_emails = Column(Integer)
    content_type_distribution = Column(JSON)
    top_topics = Column(JSON)
    market_sentiment = Column(String(20))
    generated_reports = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_market_overviews_overview_date', 'overview_date'),
    )


class ProcessingLog(Base):
    """处理日志表"""
    __tablename__ = 'processing_logs'

    id = Column(BigInteger, primary_key=True)
    log_level = Column(String(20), nullable=False)
    logger_name = Column(String(100))
    message = Column(Text, nullable=False)
    module = Column(String(100))
    function_name = Column(String(100))
    line_number = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('idx_processing_logs_created_at', 'created_at'),
        Index('idx_processing_logs_level', 'log_level'),
    )
