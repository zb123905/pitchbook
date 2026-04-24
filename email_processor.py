"""
Email Processing Module
For processing PitchBook subscription emails, extracting text and links
"""
import os
import logging
import re
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
import requests
import config

# Database support (optional)
DATABASE_AVAILABLE = False
if config.DB_ENABLED:
    try:
        from database.base import init_database, get_db_session, is_database_enabled
        from database.repositories import (
            EmailRepository, EmailLinkRepository,
            EmailAttachmentRepository, DownloadedReportRepository
        )
        DATABASE_AVAILABLE = True
        logger = logging.getLogger(__name__)
        logger.info("Database support enabled")
    except ImportError as e:
        logger = logging.getLogger(__name__)
        logger.warning(f"Database modules not available: {e}")

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOGS_DIR, 'email_processor.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class EmailProcessor:
    """Main class for processing PitchBook emails"""

    def __init__(self, use_database=None):
        self.processed_emails = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Database support
        self.use_database = use_database if use_database is not None else (config.DB_ENABLED and DATABASE_AVAILABLE)

        if self.use_database:
            logger.info("Database persistence enabled")
            # Initialize database connection
            if not is_database_enabled():
                init_database(config)

    def parse_email_file(self, email_file_path):
        """Parse single email file"""
        logger.info(f"Starting to process email file: {email_file_path}")

        try:
            file_extension = os.path.splitext(email_file_path)[1].lower()

            if file_extension in ['.eml', '.msg']:
                return self._parse_eml_file(email_file_path)
            elif file_extension == '.txt':
                return self._parse_text_email(email_file_path)
            else:
                logger.warning(f"Unsupported file format: {file_extension}")
                return None

        except Exception as e:
            logger.error(f"Error processing email file: {str(e)}")
            return None

    def _parse_eml_file(self, email_file_path):
        """Parse .eml format email file"""
        try:
            with open(email_file_path, 'rb') as f:
                msg = BytesParser(policy=policy.default).parse(f)

            # Extract basic information
            email_data = {
                'subject': self._get_email_subject(msg),
                'from': self._get_email_from(msg),
                'date': self._get_email_date(msg),
                'body': '',
                'html_body': '',
                'links': [],
                'attachments': [],
                'source_file': os.path.basename(email_file_path)
            }

            # Extract email body
            self._extract_email_body(msg, email_data)

            # Extract links
            email_data['links'] = self._extract_links(email_data['html_body'] or email_data['body'])

            # Extract attachment information
            email_data['attachments'] = self._extract_attachments(msg)

            # Extract structured data (companies, amounts, transaction types, etc.)
            email_data['structured_data'] = self.extract_structured_data(email_data)

            logger.info(f"Successfully parsed email: {email_data['subject']}")
            logger.info(f"Found {len(email_data['links'])} links")
            logger.info(f"Found {len(email_data['attachments'])} attachments")

            return email_data

        except Exception as e:
            logger.error(f"Failed to parse email file: {str(e)}")
            return None

    def _parse_text_email(self, email_file_path):
        """Parse plain text format email file"""
        try:
            with open(email_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            email_data = {
                'subject': self._extract_subject_from_text(content),
                'from': '',
                'date': '',
                'body': content,
                'html_body': '',
                'links': [],
                'attachments': [],
                'source_file': os.path.basename(email_file_path)
            }

            # Extract links
            email_data['links'] = self._extract_links(content)

            # Extract structured data
            email_data['structured_data'] = self.extract_structured_data(email_data)

            logger.info(f"Successfully parsed text email: {email_data['subject'] or 'No subject'}")
            logger.info(f"Found {len(email_data['links'])} links")

            return email_data

        except Exception as e:
            logger.error(f"Failed to parse text email: {str(e)}")
            return None

    def _get_email_subject(self, msg):
        """Get email subject"""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == 'text/plain':
                        return str(part.get('subject', ''))
            return str(msg.get('subject', ''))
        except:
            return str(msg.get('subject', ''))

    def _get_email_from(self, msg):
        """Get email sender"""
        try:
            return str(msg.get('from', ''))
        except:
            return ''

    def _get_email_date(self, msg):
        """Get email date"""
        try:
            return str(msg.get('date', ''))
        except:
            return ''

    def _extract_email_body(self, msg, email_data):
        """Extract email body"""
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get('Content-Disposition', ''))

                    # Skip attachments
                    if 'attachment' in content_disposition:
                        continue

                    # Process body
                    if content_type == 'text/plain':
                        payload = part.get_payload(decode=True)
                        if payload:
                            try:
                                email_data['body'] += payload.decode('utf-8', errors='ignore')
                            except:
                                email_data['body'] += payload.decode('gbk', errors='ignore')
                    elif content_type == 'text/html':
                        payload = part.get_payload(decode=True)
                        if payload:
                            try:
                                email_data['html_body'] += payload.decode('utf-8', errors='ignore')
                            except:
                                email_data['html_body'] += payload.decode('gbk', errors='ignore')
            else:
                # Single part email
                content_type = msg.get_content_type()
                if content_type == 'text/plain':
                    payload = msg.get_payload(decode=True)
                    if payload:
                        try:
                            email_data['body'] = payload.decode('utf-8', errors='ignore')
                        except:
                            email_data['body'] = payload.decode('gbk', errors='ignore')
                elif content_type == 'text/html':
                    payload = msg.get_payload(decode=True)
                    if payload:
                        try:
                            email_data['html_body'] = payload.decode('utf-8', errors='ignore')
                        except:
                            email_data['html_body'] = payload.decode('gbk', errors='ignore')

        except Exception as e:
            logger.warning(f"Error extracting email body: {str(e)}")

    def _extract_attachments(self, msg):
        """Extract attachment information"""
        attachments = []
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_disposition = str(part.get('Content-Disposition', ''))
                    if 'attachment' in content_disposition:
                        filename = part.get_filename()
                        if filename:
                            attachments.append({
                                'filename': filename,
                                'size': len(part.get_payload(decode=True) or b'')
                            })
        except Exception as e:
            logger.warning(f"Error extracting attachment information: {str(e)}")

        return attachments

    def _extract_links(self, content):
        """Extract all links from content"""
        links = []

        if not content:
            return links

        try:
            # If HTML content
            if '<' in content and '>' in content:
                try:
                    soup = BeautifulSoup(content, 'html.parser')
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag['href'].strip()
                        link_text = a_tag.get_text(strip=True) or '无链接文本'

                        # 只保存有效的链接
                        if href and not href.startswith('#') and not href.startswith('mailto:'):
                            # 清理链接
                            href = self._clean_link(href)
                            if href:
                                links.append({
                                    'url': href,
                                    'text': link_text[:100]
                                })
                except Exception as e:
                    logger.warning(f"Failed to parse HTML links: {str(e)}")

            # Extract URLs from plain text
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]\{\}\(\)\$\s]+'
            text_links = re.findall(url_pattern, content)

            for url in text_links:
                url = self._clean_link(url)
                if url and not any(link['url'] == url for link in links):
                    links.append({
                        'url': url,
                        'text': '直接链接'
                    })

        except Exception as e:
            logger.warning(f"Error extracting links: {str(e)}")

        logger.info(f"Total extracted {len(links)} links")
        return links

    def _clean_link(self, url):
        """Clean and validate links"""
        if not url:
            return None

        # Remove trailing punctuation
        url = url.rstrip('.,;:!?)\'"`')

        # Keep only valid characters
        url = re.sub(r'[^\w\-._~:/?#\[\]@!$&\'()*+,;=%]', '', url)

        # Ensure starts with http
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url

        return url if url.startswith('http://') or url.startswith('https://') else None

    def _extract_subject_from_text(self, content):
        """Extract email subject from text content"""
        subject_match = re.search(r'[Ss]ubject[:\s]+(.*?)(?:\n|$)', content, re.IGNORECASE)
        if subject_match:
            return subject_match.group(1).strip()
        return 'No subject'

    def extract_structured_data(self, email_data):
        """
        从邮件中提取结构化数据（公司、金额、交易类型等）

        Args:
            email_data: 已解析的邮件数据字典

        Returns:
            dict: 包含结构化数据的字典
        """
        content = (email_data.get('html_body') or email_data.get('body') or '')
        subject = email_data.get('subject', '')

        structured_data = {
            'company_names': [],
            'deal_amounts': [],
            'transaction_types': [],
            'industries': [],
            'key_numbers': [],
            'titles': []
        }

        # 1. 提取标题（从邮件主题和正文中）
        titles = set()

        # 从主题提取
        if subject:
            titles.add(subject.strip())

        # 从HTML内容提取标题（h1-h3标签）
        if '<' in content:
            try:
                soup = BeautifulSoup(content, 'html.parser')
                for tag in soup.find_all(['h1', 'h2', 'h3']):
                    title_text = tag.get_text(strip=True)
                    if len(title_text) > 5 and len(title_text) < 200:
                        titles.add(title_text)
            except:
                pass

        structured_data['titles'] = list(titles)

        # 2. 提取公司名称（常见VC/PE公司模式）
        # 匹配 "Company X raises $Y" 模式
        company_pattern = r'([A-Z][A-Za-z\s&]+?)(?:\s+(?:raises|raised|secures|secured|announces|acquires|merges with|IPO|files for))'
        companies = re.findall(company_pattern, content, re.IGNORECASE)
        structured_data['company_names'] = list(set([c.strip() for c in companies if len(c.strip()) > 2]))

        # 3. 提取交易金额
        # 匹配 $1M, $100 million, ¥500亿 等模式
        amount_pattern = r'[$¥€£]([\d.,]+(?:\s*(?:million|billion|b|m|bn|万|亿|万|千))?)'
        amounts = re.findall(amount_pattern, content, re.IGNORECASE)
        structured_data['deal_amounts'] = amounts

        # 4. 识别交易类型
        transaction_keywords = {
            'VC': ['Series A', 'Series B', 'Series C', 'Seed', 'Angel', 'Venture Capital', 'VC funding'],
            'PE': ['Private Equity', 'Buyout', 'LBO', 'Leveraged Buyout'],
            'M&A': ['merger', 'acquisition', 'acquires', 'M&A', 'buyout'],
            'IPO': ['IPO', 'initial public offering', 'goes public', 'listed'],
            'Fundraising': ['raises', 'raised', 'secures', 'funding round', 'investment'],
        }

        content_lower = content.lower()
        for trans_type, keywords in transaction_keywords.items():
            if any(keyword.lower() in content_lower for keyword in keywords):
                structured_data['transaction_types'].append(trans_type)

        # 5. 提取行业关键词
        industry_keywords = [
            'fintech', 'healthcare', 'SaaS', 'AI', 'machine learning', 'biotech',
            'crypto', 'blockchain', 'e-commerce', 'consumer', 'enterprise software',
            'clean energy', 'edtech', 'proptech', 'insurtech'
        ]

        for industry in industry_keywords:
            if industry.lower() in content_lower:
                structured_data['industries'].append(industry)

        # 6. 提取关键数字（估值、倍数等）
        # 匹配 "x revenue", "x ARR" 等模式
        metric_pattern = r'(\d+(?:\.\d+)?)\s*(?:x|times|ARR|revenue|EBITDA|GM|margin)'
        metrics = re.findall(metric_pattern, content, re.IGNORECASE)
        structured_data['key_numbers'] = metrics

        # 记录提取的统计信息
        logger.info(f"提取结构化数据: "
                   f"{len(structured_data['titles'])} 个标题, "
                   f"{len(structured_data['company_names'])} 个公司, "
                   f"{len(structured_data['deal_amounts'])} 个金额, "
                   f"{len(structured_data['transaction_types'])} 个交易类型")

        return structured_data

    def download_report_from_link(self, url, save_dir=None, use_enhanced=False):
        """Download report file from link

        Args:
            url: Report URL
            save_dir: Directory to save the file (default: config.FILE_DOWNLOAD_DIR)
            use_enhanced: Use enhanced download service with file type detection and retry
        """
        if save_dir is None:
            save_dir = config.FILE_DOWNLOAD_DIR

        # Use enhanced download service if available and enabled
        if use_enhanced and config.DB_ENABLED:
            try:
                from services.download_service import EnhancedDownloadService
                service = EnhancedDownloadService()
                result = service.download_report(url, save_dir)
                service.close()
                return result
            except Exception as e:
                logger.warning(f"Enhanced download service failed, falling back to default: {e}")

        try:
            logger.info(f"Attempting to download: {url}")

            # Set timeout and retry
            response = self.session.get(url, timeout=30, allow_redirects=True)

            if response.status_code == 200:
                # Determine filename
                content_type = response.headers.get('Content-Type', 'application/pdf')

                # Try to get filename from URL or Content-Disposition
                filename = None

                # Try to get filename from Content-Disposition
                content_disposition = response.headers.get('Content-Disposition', '')
                if content_disposition:
                    filename_match = re.search(r'filename=["\']?([^"\']+)', content_disposition)
                    if filename_match:
                        filename = filename_match.group(1)

                # If no filename, extract from URL
                if not filename or len(filename) < 3:
                    url_path = url.split('?')[0]
                    filename = os.path.basename(url_path)

                # Ensure filename is valid
                if not filename or len(filename) < 3:
                    filename = f"report_{hash(url) % 10000}.pdf"

                # Save file
                filepath = os.path.join(save_dir, filename)

                with open(filepath, 'wb') as f:
                    f.write(response.content)

                logger.info(f"Successfully downloaded: {filepath}")
                return {
                    'success': True,
                    'filepath': filepath,
                    'filename': filename,
                    'content_type': content_type,
                    'url': url
                }
            else:
                logger.warning(f"Download failed, status code: {response.status_code}")
                return {
                    'success': False,
                    'error': f'Status code: {response.status_code}',
                    'url': url
                }

        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'url': url
            }

    def process_email_directory(self, email_dir):
        """Process all email files in directory in batch"""
        logger.info(f"Starting to process directory: {email_dir}")

        if not os.path.exists(email_dir):
            logger.error(f"Directory does not exist: {email_dir}")
            return []

        # Supported email file formats
        supported_extensions = ['.eml', '.msg', '.txt']
        processed_emails = []

        for filename in os.listdir(email_dir):
            if any(filename.lower().endswith(ext) for ext in supported_extensions):
                file_path = os.path.join(email_dir, filename)
                email_data = self.parse_email_file(file_path)
                if email_data:
                    processed_emails.append(email_data)

        logger.info(f"Successfully processed {len(processed_emails)} emails")
        return processed_emails

    def save_processed_emails(self, emails=None, save_dir=None):
        """Save processed email data"""
        if emails is None:
            emails = self.processed_emails

        if save_dir is None:
            save_dir = config.EMAIL_EXTRACTION_DIR

        if not emails:
            logger.warning("No email data to save")
            return None

        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filepath = os.path.join(save_dir, f'processed_emails_AI分析_{timestamp}.json')

        try:
            import json
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(emails, f, ensure_ascii=False, indent=2)

            logger.info(f"Email processing results saved to: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to save email data: {str(e)}")
            return None

    def save_processed_emails_to_db(self, emails=None):
        """Save processed emails to database"""
        if not self.use_database:
            logger.debug("Database persistence disabled")
            return None

        if emails is None:
            emails = self.processed_emails

        if not emails:
            logger.warning("No email data to save to database")
            return None

        try:
            saved_count = 0

            with get_db_session() as session:
                email_repo = EmailRepository(session)
                link_repo = EmailLinkRepository(session)
                attachment_repo = EmailAttachmentRepository(session)

                for email_data in emails:
                    # Check if email already exists
                    message_id = email_data.get('message_id')
                    if message_id and email_repo.get_by_message_id(message_id):
                        logger.debug(f"Email {message_id} already exists, skipping")
                        continue

                    # Create email record
                    db_email = email_repo.create(email_data)

                    # Create link records
                    if email_data.get('links'):
                        link_repo.create_batch(db_email.id, email_data['links'])

                    # Create attachment records
                    if email_data.get('attachments'):
                        for attachment in email_data['attachments']:
                            attachment_repo.create({
                                'email_id': db_email.id,
                                'filename': attachment.get('filename'),
                                'size': attachment.get('size'),
                                'content_type': 'application/octet-stream'
                            })

                    saved_count += 1

            logger.info(f"Saved {saved_count}/{len(emails)} emails to database")
            return saved_count

        except Exception as e:
            logger.error(f"Failed to save emails to database: {e}")
            return None

    def save_to_both(self, emails=None, save_dir=None):
        """Save to both JSON file and database"""
        results = {'json': None, 'database': None}

        # Save to JSON
        if config.KEEP_JSON_BACKUP:
            results['json'] = self.save_processed_emails(emails, save_dir)

        # Save to database
        if self.use_database:
            results['database'] = self.save_processed_emails_to_db(emails)

        return results
