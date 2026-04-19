# ============================================================================
# POST-PROCESSING RULES FOR CULTURAL ACCURACY
# ============================================================================
# This script applies domain-specific rules to ensure culturally correct outputs
# (Runs after model translation)
# ============================================================================

import json
import re

# Load cultural dictionary
with open('data/cultural_dictionary.json', 'r', encoding='utf-8') as f:
    cultural_dict = json.load(f)

# ============================================================================
# POST-PROCESSING RULES
# ============================================================================

class CulturalPostProcessor:
    """
    Applies cultural-aware post-processing to translations
    to ensure correct terminology and context
    """
    
    def __init__(self, cultural_dict_path='data/cultural_dictionary.json'):
        """Initialize with cultural dictionary"""
        with open(cultural_dict_path, 'r', encoding='utf-8') as f:
            self.cultural_dict = json.load(f)
        
        print("✅ CulturalPostProcessor initialized")
        print(f"   - Clans: {len(self.cultural_dict['clans'])}")
        print(f"   - Terms: {len(self.cultural_dict['cultural_terms'])}")
    
    def correct_clan_names(self, text):
        """
        Correct clan names to proper Luganda spelling
        """
        for english_clan, luganda_clan in self.cultural_dict['clans'].items():
            # Pattern: "clan of XXXX" or "XXXX clan" patterns
            patterns = [
                rf'\bkika (?:ky)?a\s+\w*{english_clan}\w*\b',
                rf'\b{english_clan}\s+(?:clan)?(?:\s|$)',
            ]
            for pattern in patterns:
                text = re.sub(pattern, f'ekika kya {luganda_clan}', text, flags=re.IGNORECASE)
        return text
    
    def correct_royal_titles(self, text):
        """
        Ensure royal titles use correct Luganda terms
        """
        corrections = {
            r'\bking\b': 'Kabaka',
            r'\bqueen\b': 'Nnabagereka',
            r'\bprince\b': 'omwana wa kabaka',
            r'\bchief\b': 'omukulu',
            r'\bruler?\b': 'kabaka',
        }
        
        for english, luganda in corrections.items():
            text = re.sub(english, luganda, text, flags=re.IGNORECASE)
        
        return text
    
    def correct_cultural_terms(self, text):
        """
        Replace generic translations with culturally accurate ones
        """
        for english_term, luganda_term in self.cultural_dict['cultural_terms'].items():
            # Match whole words
            pattern = rf'\b{english_term}\b'
            text = re.sub(pattern, luganda_term, text, flags=re.IGNORECASE)
        
        return text
    
    def correct_kingdom_references(self, text):
        """
        Ensure Buganda kingdom references are correct
        """
        for english_ref, luganda_ref in self.cultural_dict['kingdom'].items():
            pattern = rf'\b{english_ref}\b'
            text = re.sub(pattern, luganda_ref, text, flags=re.IGNORECASE)
        
        return text
    
    def apply_context_rules(self, text, context=None):
        """
        Apply context-specific rules
        """
        if context == 'ROYAL':
            # Royal context: capitalize Kabaka
            text = re.sub(r'\bkabaka\b', 'Kabaka', text)
            text = re.sub(r'\bnnabagereka\b', 'Nnabagereka', text)
        
        elif context == 'TOTEM':
            # Totem context: emphasize respect
            text = re.sub(r'muzizo', 'muzizo (totem)', text)
        
        elif context == 'TRADITION':
            # Tradition context: emphasize cultural value
            text = re.sub(r'\benkola\b', 'enkola (tradition)', text, flags=re.IGNORECASE)
        
        return text
    
    def post_process(self, translation, input_text=None, context=None):
        """
        Apply all post-processing rules to ensure cultural accuracy
        
        Args:
            translation: The model's translation output
            input_text: The original input (for context detection)
            context: Optional context tag (CLAN, ROYAL, TOTEM, etc.)
        
        Returns:
            Culturally corrected translation
        """
        # Apply rules in sequence
        text = translation
        text = self.correct_clan_names(text)
        text = self.correct_royal_titles(text)
        text = self.correct_cultural_terms(text)
        text = self.correct_kingdom_references(text)
        
        if context:
            text = self.apply_context_rules(text, context)
        
        return text
    
    def batch_post_process(self, translations, inputs=None, contexts=None):
        """
        Apply post-processing to a batch of translations
        
        Args:
            translations: List of translations
            inputs: List of input texts (optional)
            contexts: List of context tags (optional)
        
        Returns:
            List of corrected translations
        """
        results = []
        for i, trans in enumerate(translations):
            input_text = inputs[i] if inputs else None
            context = contexts[i] if contexts else None
            results.append(self.post_process(trans, input_text, context))
        
        return results


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("🎭 CULTURAL POST-PROCESSOR TEST")
    print("=" * 70 + "\n")
    
    processor = CulturalPostProcessor()
    
    # Test cases
    test_cases = [
        {
            "input": "I belong to the Mamba clan",
            "translation": "Ndi wa kika kya mbwa",
            "context": "CLAN"
        },
        {
            "input": "The king is respected",
            "translation": "Kabaka assibwamu ekitiibwa",
            "context": "ROYAL"
        },
        {
            "input": "Do not eat your totem",
            "translation": "Tolyanga muzizo gwo",
            "context": "TOTEM"
        }
    ]
    
    print("Testing post-processing rules:\n")
    
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. Input: {test['input']}")
        print(f"   Context: {test['context']}")
        print(f"   Model output: {test['translation']}")
        corrected = processor.post_process(test['translation'], test['input'], test['context'])
        print(f"   ✅ Corrected: {corrected}\n")
    
    print("=" * 70)
