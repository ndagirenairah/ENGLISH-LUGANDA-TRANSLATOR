# ============================================================================
# LUGANDA TRANSLATION QUALITY FIXER
# ============================================================================
# Rule-based correction layer to fix common translation errors
# and improve cultural accuracy
# ============================================================================

"""
This module provides corrections for common Luganda translation errors.
Why? Because pre-trained models like Helsinki-NLP/opus-mt-en-lg are trained on:
- Mixed Luganda styles (formal/religious/colloquial)
- Limited and inconsistent data
- No cultural context

This layer fixes:
1. Incorrect cultural terms (Omukama → Kabaka)
2. Unnatural grammar (Ndi okulya → Ndi kulya)
3. Wrong word choices
4. Missing culturally appropriate alternatives
"""

class LugandaTranslationFixer:
    """
    Fixes common errors in Luganda translations
    by applying rule-based corrections
    """
    
    def __init__(self):
        """Initialize correction rules"""
        
        # RULE 1: Cultural & Royal Title Corrections
        self.royal_corrections = {
            "omukama": "Kabaka",
            "Omukama": "Kabaka",
            "the king": "Kabaka",
            "the queen": "Nnabagereka",
            "omukazi wakabaka": "Nnabagereka",
        }
        
        # RULE 2: Grammar Fixes (unnatural constructions)
        self.grammar_fixes = {
            "ndi okulya": "ndi kulya",          # I am eating
            "ndi okunnyonnyola": "ndi kunnyonnyola",  # I am speaking
            "ndi okugenda": "ndi kugenda",      # I am going
            "ndi okutegeeza": "ndi kutegeeza",  # I am telling
            "ndi okukyamu": "ndi kukyamu",      # I am leaving
            "okulinga": "kulinga",              # to play
            "okutegeeza": "kutegeeza",          # to tell
            "okukyamu": "kukyamu",              # to leave
        }
        
        # RULE 3: Clan & Totem Corrections
        self.clan_corrections = {
            "the mamba clan": "kika kya Mmamba",
            "mamba": "Mmamba",
            "ngabi clan": "kika kya Ngabi",
            "clan totem": "muzizo gw'ekika",
            "to not eat": "tolyanga",           # respect totem
            "do not eat": "tolyanga",
        }
        
        # RULE 4: Respect & Tradition Terms
        self.cultural_terms = {
            "respect": "ossegeze",              # show respect
            "respect your elders": "ossegeze abakulu",
            "elder": "omukulu",
            "the elders": "abakulu",
            "tradition": "enkola",
            "customs": "enkola",
            "blessed": "amuwe ekifo",
            "blessing": "ekifo",
        }
        
        # RULE 5: Common Sense Fixes
        self.common_fixes = {
            "the people": "abantu",
            "the country": "eggwanga",
            "love your country": "kukyamu eggwanga",
            "i am": "ndi",
            "you are": "oli",
            "we are": "twali",
            "they are": "bali",
        }
    
    def apply_corrections(self, text, debug=False):
        """
        Apply all correction rules to text
        
        Args:
            text (str): Luganda translation to fix
            debug (bool): Print corrections applied
        
        Returns:
            str: Corrected Luganda text
        """
        original = text
        
        # Apply each rule set
        text = self._apply_rules(text, self.royal_corrections, "Royal/Cultural", debug)
        text = self._apply_rules(text, self.grammar_fixes, "Grammar", debug)
        text = self._apply_rules(text, self.clan_corrections, "Clan/Totem", debug)
        text = self._apply_rules(text, self.cultural_terms, "Cultural Terms", debug)
        text = self._apply_rules(text, self.common_fixes, "Common Fixes", debug)
        
        if debug and text != original:
            print(f"   [CORRECTED] {original} → {text}")
        
        return text
    
    def _apply_rules(self, text, rules_dict, category, debug=False):
        """Apply a set of correction rules"""
        for incorrect, correct in rules_dict.items():
            if incorrect.lower() in text.lower():
                text = text.replace(incorrect, correct)
                text = text.replace(incorrect.capitalize(), correct)
                if debug:
                    print(f"      [{category}] {incorrect} → {correct}")
        return text
    
    def validate_translation(self, english, luganda):
        """
        Check if translation seems reasonable
        
        Args:
            english (str): English source
            luganda (str): Luganda translation
        
        Returns:
            dict: Validation results
        """
        issues = []
        
        # Check 1: Empty translation
        if not luganda or luganda.strip() == "":
            issues.append("Empty translation")
        
        # Check 2: Too short (might be truncated)
        elif len(luganda.split()) < max(1, len(english.split()) - 3):
            issues.append("Translation too short (might be truncated)")
        
        # Check 3: Special tokens not removed
        elif "<" in luganda or ">" in luganda:
            issues.append("Contains special tokens")
        
        # Check 4: Repeated words (common error)
        elif self._has_excessive_repetition(luganda):
            issues.append("Excessive word repetition detected")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "english": english,
            "luganda": luganda
        }
    
    def _has_excessive_repetition(self, text, threshold=2):
        """Check if text has too many repeated words"""
        words = text.split()
        for word in set(words):
            if words.count(word) > threshold:
                return True
        return False
    
    def compare_translations(self, english_input, original_output, corrected_output):
        """
        Compare original and corrected translations
        
        Args:
            english_input (str): English source
            original_output (str): Model's original output
            corrected_output (str): After corrections applied
        
        Returns:
            dict: Comparison results
        """
        return {
            "english": english_input,
            "original_luganda": original_output,
            "corrected_luganda": corrected_output,
            "improved": original_output != corrected_output,
            "changes": self._highlight_changes(original_output, corrected_output)
        }
    
    def _highlight_changes(self, original, corrected):
        """Highlight what changed between versions"""
        original_words = set(original.split())
        corrected_words = set(corrected.split())
        
        added = corrected_words - original_words
        removed = original_words - corrected_words
        
        return {
            "words_changed": len(added) + len(removed),
            "words_added": list(added),
            "words_removed": list(removed)
        }


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("LUGANDA TRANSLATION QUALITY FIXER - TEST")
    print("=" * 70 + "\n")
    
    fixer = LugandaTranslationFixer()
    
    # Test cases with common errors
    test_cases = [
        {
            "english": "The Kabaka is respected",
            "model_output": "Omukama assibwamu ekitiibwa",
            "description": "Wrong royal title"
        },
        {
            "english": "I am eating",
            "model_output": "Ndi okulya",
            "description": "Unnatural grammar"
        },
        {
            "english": "I belong to the Mamba clan",
            "model_output": "Ndi wa kika ky'omamba",
            "description": "Clan name not capitalized properly"
        },
        {
            "english": "Respect your elders",
            "model_output": "Ossegeza abakulu b'ene",
            "description": "Grammar issue with possessive"
        },
        {
            "english": "Do not eat your totem",
            "model_output": "Tolyanga muzizo gw'oyennyezeza",
            "description": "Unclear construction"
        }
    ]
    
    print("Testing correction rules:\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. {test['description']}")
        print(f"   English:      {test['english']}")
        print(f"   Model output: {test['model_output']}")
        
        corrected = fixer.apply_corrections(test['model_output'], debug=False)
        print(f"   ✅ Corrected:  {corrected}")
        
        validation = fixer.validate_translation(test['english'], corrected)
        if validation['valid']:
            print(f"   Status:       ✅ Looks good")
        else:
            print(f"   Status:       ⚠️  Issues: {validation['issues']}")
        
        print()
    
    print("=" * 70)
    print("IMPROVEMENT SUMMARY")
    print("=" * 70 + "\n")
    
    print("This fixer corrects:")
    print("  ✓ Royal titles (Omukama → Kabaka)")
    print("  ✓ Grammar errors (Ndi okulya → Ndi kulya)")
    print("  ✓ Clan terminology (mamba → Mmamba)")
    print("  ✓ Cultural terms (respect → ossegeza)")
    print("  ✓ Common sense phrases")
    print("\n" + "=" * 70 + "\n")
