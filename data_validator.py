#!/usr/bin/env python3
"""
Data Validation & Quality Checker for English-Luganda Translation Model
Identifies problematic translations and checks for accuracy
"""

import json
from typing import Dict, List, Tuple

# Known problematic patterns to flag
FLAGGED_ISSUES = {
    "good morning": {
        "current": "Wasuubire nnyo",
        "issue": "Likely incorrect - relates to 'sleep' not 'morning'",
        "suggested": "Wasuze otya? (sg) or Mwasuze mutya? (pl) - 'How have you slept?'",
        "confidence": "HIGH"
    },
    "welcome to uganda": {
        "current": "Bawaayo mu Uganda",
        "issue": "Bawaayo = 'they give' - incorrect meaning",
        "suggested": "Tukusanyukidwa mu Uganda (sg) or Tubasanyukidwa mu Uganda (pl)",
        "confidence": "HIGH"
    },
    "education is important": {
        "current": "Kikulu nnyo okuyigirizibwa",
        "issue": "English-like word order, missing noun class agreement",
        "suggested": "Okuyigirizibwa kukulu nnyo - proper noun class agreement",
        "confidence": "MEDIUM"
    }
}

# Luganda linguistic patterns to check
LUGANDA_CHECKS = {
    "noun_class_agreement": {
        "pattern": "Class prefixes must agree (oku-, ki-, ba-, etc.)",
        "examples": [
            ("Education is important", "okuyigirizibwa kukulu nnyo", "oku- infinitive, ku- class 15 copula"),
            ("The man came", "Omusajja yajja", "omu- class 1, y- class 1 verb marker"),
        ]
    },
    "tense_markers": {
        "pattern": "Tense/aspect shown through verb prefixes and infixes",
        "examples": [
            ("I am", "Ndi", "present continuous"),
            ("I was", "Nnali", "past continuous"),
            ("I will be", "Ndibanga", "future"),
        ]
    },
    "subject_object_agreement": {
        "pattern": "Verbs must agree with subject and object noun classes",
        "warning": "Check if -ba-, -ki-, -mu-, etc. prefixes match subject"
    }
}

class DataValidator:
    def __init__(self):
        self.flagged = []
        self.verified = []
        self.issues = []
    
    def validate_translations(self, translations_dict: Dict[str, str]) -> Dict:
        """Validate all translations in dictionary"""
        results = {
            "total": len(translations_dict),
            "flagged": [],
            "verified": [],
            "high_confidence_flags": 0,
            "requires_review": [],
            "issues": []
        }
        
        for english, luganda in translations_dict.items():
            english_lower = english.lower()
            
            # Check against known problematic patterns
            if english_lower in FLAGGED_ISSUES:
                issue = FLAGGED_ISSUES[english_lower]
                results["flagged"].append({
                    "english": english,
                    "current_luganda": luganda,
                    "issue": issue["issue"],
                    "suggested": issue["suggested"],
                    "confidence": issue["confidence"]
                })
                if issue["confidence"] == "HIGH":
                    results["high_confidence_flags"] += 1
            else:
                results["verified"].append(english)
            
            # Run linguistic checks
            ling_issues = self._check_luganda_patterns(luganda)
            if ling_issues:
                results["requires_review"].append({
                    "english": english,
                    "luganda": luganda,
                    "checks": ling_issues
                })
        
        return results
    
    def _check_luganda_patterns(self, text: str) -> List[str]:
        """Check for common Luganda linguistic patterns"""
        issues = []
        
        # Check for obvious noun class markers
        valid_prefixes = ["oku", "ki", "ba", "mu", "n", "a", "ka", "lu", "ku", "nne", "e"]
        if text and not any(text.startswith(prefix) for prefix in valid_prefixes):
            issues.append("Missing expected noun class prefix")
        
        # Check for valid tense markers
        if "yy" in text or "dd" in text or "ll" in text:
            # Potential gemination issues
            issues.append("Check gemination (doubled consonants)")
        
        # Check length - short translations might be incomplete
        words = text.split()
        if len(words) == 1 and len(text) < 4:
            issues.append("Unusually short - may be incomplete")
        
        return issues
    
    def compare_quality(self, old_luganda: str, new_luganda: str) -> Dict:
        """Compare quality of two Luganda translations"""
        return {
            "old": old_luganda,
            "new": new_luganda,
            "old_length": len(old_luganda),
            "new_length": len(new_luganda),
            "old_words": len(old_luganda.split()),
            "new_words": len(new_luganda.split()),
            "confidence_change": "NEW LONGER" if len(new_luganda) > len(old_luganda) else "NEW SHORTER"
        }

def generate_validation_report(translations_dict: Dict[str, str]) -> str:
    """Generate comprehensive validation report"""
    validator = DataValidator()
    results = validator.validate_translations(translations_dict)
    
    report = []
    report.append("=" * 80)
    report.append("🔍 DATA VALIDATION REPORT - ENGLISH-LUGANDA TRANSLATIONS")
    report.append("=" * 80)
    report.append("")
    
    # Summary
    report.append(f"📊 SUMMARY")
    report.append(f"  Total translations: {results['total']}")
    report.append(f"  ✅ Verified: {len(results['verified'])}")
    report.append(f"  🚩 Flagged for review: {len(results['flagged'])}")
    report.append(f"  ⚠️  High-confidence flags: {results['high_confidence_flags']}")
    report.append(f"  🔎 Requires linguistic review: {len(results['requires_review'])}")
    report.append("")
    
    # Flagged translations
    if results["flagged"]:
        report.append("=" * 80)
        report.append("🚩 HIGH-PRIORITY ISSUES REQUIRING FIX")
        report.append("=" * 80)
        for i, item in enumerate(results["flagged"], 1):
            report.append(f"\n{i}. English: '{item['english']}'")
            report.append(f"   Current Luganda: '{item['current_luganda']}'")
            report.append(f"   Issue: {item['issue']}")
            report.append(f"   Suggested: '{item['suggested']}'")
            report.append(f"   Confidence: {item['confidence']}")
    
    # Requires linguistic review
    if results["requires_review"]:
        report.append("\n" + "=" * 80)
        report.append("🔎 REQUIRES LINGUISTIC REVIEW")
        report.append("=" * 80)
        for i, item in enumerate(results["requires_review"][:10], 1):  # Show first 10
            report.append(f"\n{i}. English: '{item['english']}'")
            report.append(f"   Luganda: '{item['luganda']}'")
            report.append(f"   Issues: {', '.join(item['checks'])}")
    
    report.append("\n" + "=" * 80)
    report.append("✅ VALIDATION COMPLETE")
    report.append("=" * 80)
    
    return "\n".join(report)

if __name__ == "__main__":
    # Test with sample translations
    from app import GUARANTEED_TRANSLATIONS
    
    report = generate_validation_report(GUARANTEED_TRANSLATIONS)
    print(report)
    
    # Save report
    with open("validation_report.txt", "w", encoding="utf-8") as f:
        f.write(report)
    print("\n✅ Report saved to: validation_report.txt")
