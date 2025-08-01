"""
Caption Pattern Estimator

This module provides utilities for estimating caption patterns in PDF documents.
"""

import re
import fitz
from typing import Optional, Dict, List


class CaptionPatternEstimator:
    """Estimates caption patterns from PDF documents."""
    
    def __init__(self):
        self.patterns = {
            'figure': [
                r'Figure\s+(\d+)',
                r'Fig\.\s*(\d+)',
                r'FIG\.\s*(\d+)',
                r'Figure\s*(\d+)\.',
                r'Fig\.\s*(\d+)\.'
            ],
            'table': [
                r'Table\s+(\d+)',
                r'Tab\.\s*(\d+)',
                r'TABLE\s+(\d+)',
                r'Table\s*(\d+)\.',
                r'Tab\.\s*(\d+)\.'
            ]
        }
    
    def estimate_pattern_from_pdf(self, pdf_path: str) -> Optional[Dict]:
        """Estimate caption patterns from a PDF document."""
        try:
            doc = fitz.open(pdf_path)
            pattern_counts = {'figure': {}, 'table': {}}
            
            # Sample first few pages for pattern estimation
            sample_pages = min(5, len(doc))
            
            for page_num in range(sample_pages):
                page = doc[page_num]
                text_blocks = page.get_text("dict")["blocks"]
                
                for block in text_blocks:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                text = span["text"].strip()
                                self._analyze_text_pattern(text, pattern_counts)
            
            doc.close()
            
            # Determine most common patterns
            result = {}
            for element_type in ['figure', 'table']:
                if pattern_counts[element_type]:
                    most_common = max(pattern_counts[element_type].items(), 
                                    key=lambda x: x[1])
                    result[element_type] = most_common[0]
            
            # Store the result and set confidence
            if result:
                self._estimated_pattern = result
                self._confidence = "中"  # Default confidence
                self._suggested_threshold = 50.0  # Default threshold
            else:
                self._estimated_pattern = None
                self._confidence = "低"
                self._suggested_threshold = 30.0
            
            return result if result else None
            
        except Exception as e:
            print(f"Warning: Could not estimate patterns: {e}")
            return None
    
    def _analyze_text_pattern(self, text: str, pattern_counts: Dict):
        """Analyze text for caption patterns."""
        for element_type, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    pattern_counts[element_type][pattern] = \
                        pattern_counts[element_type].get(pattern, 0) + 1
    
    def get_estimated_pattern(self) -> Optional[Dict]:
        """Get the estimated pattern from the last analysis."""
        return getattr(self, '_estimated_pattern', None)
    
    def get_confidence(self) -> str:
        """Get confidence level of the pattern estimation."""
        return getattr(self, '_confidence', '低')
    
    def get_suggested_threshold(self) -> float:
        """Get suggested threshold for processing."""
        return getattr(self, '_suggested_threshold', 50.0)
    
    def should_prefer_position(self) -> bool:
        """Whether to prefer position-based matching over pattern-based matching."""
        return getattr(self, '_prefer_position', False)


def create_pattern_estimator() -> CaptionPatternEstimator:
    """Create a new caption pattern estimator instance."""
    return CaptionPatternEstimator() 