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

    def __init__(self):
        self.processed_emails = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

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

    def download_report_from_link(self, url, save_dir=None):
        """Download report file from link"""
        if save_dir is None:
            save_dir = config.DOWNLOADS_DIR

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
