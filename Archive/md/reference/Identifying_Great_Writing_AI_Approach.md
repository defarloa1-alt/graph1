# Identifying Great Writing: AI Approach to Poignant Prose Detection

## The Challenge

**Human Recognition:**
- Humans recognize "great writing" through:
  - **Aesthetic appreciation** - beauty, rhythm, cadence
  - **Emotional resonance** - evokes feelings, empathy
  - **Rhetorical power** - persuasive, memorable
  - **Semantic density** - layers of meaning
  - **Historical significance** - captures moment/insight
  - **Universal truth** - transcends context

**AI Challenge:**
- ❌ No universal definition of "great writing"
- ❌ Subjective quality (varies by reader)
- ❌ Context-dependent (what's great in one era/style may not be in another)
- ❌ Requires cultural/historical understanding
- ❌ Combines multiple dimensions (style + meaning + impact)

---

## Multi-Dimensional Approach

### 1. **Stylistic Quality Detection**

**Features to Detect:**
- **Rhetorical devices** (metaphor, alliteration, parallelism)
- **Sentence structure** (variation, complexity, rhythm)
- **Vocabulary richness** (lexical diversity, rare words)
- **Cohesion** (flow, transitions, coherence)

**Implementation:**
```python
def detect_stylistic_quality(text):
    features = {
        'rhetorical_devices': detect_rhetorical_devices(text),
        'sentence_variety': calculate_sentence_variety(text),
        'lexical_richness': calculate_vocabulary_diversity(text),
        'alliteration': count_alliteration(text),
        'parallelism': detect_parallel_structure(text),
        'metaphor_density': count_metaphors(text),
        'rhythm_score': analyze_sentence_rhythm(text)
    }
    return features
```

**Models:**
- **NLP Libraries:** spaCy (rhetorical device detection)
- **Style Analysis:** Textstat (readability + style metrics)
- **Literary Analysis:** CLiPS (Computational Linguistics for Literature)

---

### 2. **Semantic Significance Scoring**

**Features:**
- **Information density** - Amount of meaning per word
- **Conceptual complexity** - Abstract concepts, layered meaning
- **Insight novelty** - New perspective or synthesis
- **Universal applicability** - Transcends specific context

**Implementation:**
```python
def score_semantic_significance(text, context):
    scores = {
        'information_density': calculate_information_entropy(text),
        'concept_count': count_abstract_concepts(text),
        'insight_score': detect_insight_statements(text),
        'synthesis_score': detect_synthesis_statements(text),
        'universality': score_transcendent_meaning(text),
        'epistemic_verbs': count_insight_verbs(text)  # e.g., "reveals", "demonstrates"
    }
    return scores
```

**Models:**
- **Semantic Embeddings:** Sentence-BERT, Universal Sentence Encoder
- **Concept Extraction:** spaCy NER + Knowledge Graph linking
- **Insight Detection:** Fine-tuned models on annotated insights

---

### 3. **Emotional & Rhetorical Impact**

**Features:**
- **Emotional valence** - Positive/negative emotional content
- **Emotional intensity** - Strength of emotional language
- **Persuasive power** - Argument structure, evidence use
- **Memorability** - Phrases that stick (quotability)

**Implementation:**
```python
def assess_emotional_impact(text):
    features = {
        'emotional_valence': vader_sentiment(text)['compound'],
        'emotional_intensity': calculate_emotional_intensity(text),
        'persuasion_score': analyze_argument_structure(text),
        'quotability': detect_memorable_phrases(text),
        'pathos_score': detect_emotional_appeal(text),
        'ethos_score': detect_authority_claims(text),
        'logos_score': detect_logical_structure(text)
    }
    return features
```

**Models:**
- **Sentiment Analysis:** VADER, TextBlob, RoBERTa-large-sentiment
- **Emotion Detection:** GoEmotions, EmoRoBERTa
- **Rhetorical Analysis:** Custom models trained on rhetorical annotations

---

### 4. **Historical & Contextual Significance**

**Features:**
- **Temporal significance** - Marks turning point, captures era
- **Causal connections** - Explains why/how something happened
- **Character insight** - Reveals character motivation/nature
- **Historical synthesis** - Connects multiple events/concepts

**Implementation:**
```python
def assess_historical_significance(text, historical_context):
    features = {
        'temporal_markers': detect_turning_point_language(text),
        'causal_language': detect_causal_connections(text),
        'character_insight': detect_character_revelation(text),
        'synthesis_score': detect_historical_synthesis(text),
        'contextual_importance': score_contextual_relevance(text, historical_context),
        'uniqueness': compare_to_contemporary_sources(text, historical_context)
    }
    return features
```

**Models:**
- **Historical Event Detection:** Fine-tuned NER on historical texts
- **Causal Relation Extraction:** SemEval causal relation models
- **Contextual Embeddings:** Historical BERT (trained on period texts)

---

### 5. **Comparative Analysis**

**Features:**
- **Standout phrases** - Unusual compared to corpus
- **Author's peak writing** - Best work compared to author's other writings
- **Period comparison** - Stands out in historical period
- **Cross-source uniqueness** - Unique insight not found elsewhere

**Implementation:**
```python
def comparative_analysis(text, corpus, author_works, period_works):
    features = {
        'corpus_rarity': calculate_rarity_vs_corpus(text, corpus),
        'author_peak': compare_to_author_works(text, author_works),
        'period_standout': compare_to_period(text, period_works),
        'source_uniqueness': check_cross_source_uniqueness(text),
        'stylistic_deviation': measure_stylistic_uniqueness(text, corpus)
    }
    return features
```

**Models:**
- **Stylometry:** Author verification models, stylometric features
- **Topic Modeling:** LDA, BERTopic for theme comparison
- **Embedding Similarity:** Cosine similarity across corpus

---

## Integrated Scoring System

### Composite "Great Writing" Score

```python
def score_great_writing(text, context):
    """
    Multi-dimensional scoring of prose quality
    """
    
    # 1. Stylistic quality (30%)
    stylistic = detect_stylistic_quality(text)
    stylistic_score = (
        stylistic['rhetorical_devices'] * 0.3 +
        stylistic['sentence_variety'] * 0.2 +
        stylistic['lexical_richness'] * 0.2 +
        stylistic['rhythm_score'] * 0.3
    )
    
    # 2. Semantic significance (25%)
    semantic = score_semantic_significance(text, context)
    semantic_score = (
        semantic['information_density'] * 0.3 +
        semantic['insight_score'] * 0.4 +
        semantic['universality'] * 0.3
    )
    
    # 3. Emotional impact (20%)
    emotional = assess_emotional_impact(text)
    emotional_score = (
        abs(emotional['emotional_intensity']) * 0.4 +
        emotional['quotability'] * 0.3 +
        emotional['persuasion_score'] * 0.3
    )
    
    # 4. Historical significance (15%)
    historical = assess_historical_significance(text, context)
    historical_score = (
        historical['causal_language'] * 0.3 +
        historical['synthesis_score'] * 0.4 +
        historical['contextual_importance'] * 0.3
    )
    
    # 5. Comparative uniqueness (10%)
    comparative = comparative_analysis(text, context.corpus, 
                                       context.author_works, 
                                       context.period_works)
    comparative_score = (
        comparative['corpus_rarity'] * 0.4 +
        comparative['source_uniqueness'] * 0.6
    )
    
    # Weighted composite score
    composite_score = (
        stylistic_score * 0.30 +
        semantic_score * 0.25 +
        emotional_score * 0.20 +
        historical_score * 0.15 +
        comparative_score * 0.10
    )
    
    return {
        'composite_score': composite_score,
        'breakdown': {
            'stylistic': stylistic_score,
            'semantic': semantic_score,
            'emotional': emotional_score,
            'historical': historical_score,
            'comparative': comparative_score
        },
        'features': {
            'stylistic': stylistic,
            'semantic': semantic,
            'emotional': emotional,
            'historical': historical,
            'comparative': comparative
        }
    }
```

---

## Practical Implementation Strategy

### Phase 1: Rule-Based Heuristics (Quick Start)

**Immediate Signals:**
```python
def quick_heuristics(text):
    """Fast heuristics to identify potentially great writing"""
    
    signals = []
    
    # 1. Quotability markers
    if has_memorable_phrase_structure(text):
        signals.append('quotable')
    
    # 2. Rhetorical devices
    if count_rhetorical_devices(text) > threshold:
        signals.append('rhetorically_rich')
    
    # 3. Insight verbs
    insight_verbs = ['reveals', 'demonstrates', 'illustrates', 
                     'exemplifies', 'exposes', 'illuminates']
    if contains_insight_verbs(text, insight_verbs):
        signals.append('insightful')
    
    # 4. Metaphor density
    if metaphor_count(text) > threshold:
        signals.append('metaphorically_rich')
    
    # 5. Causal language
    if contains_causal_markers(text):
        signals.append('explanatory')
    
    # 6. Emotional intensity
    if abs(emotional_intensity(text)) > threshold:
        signals.append('emotionally_resonant')
    
    # 7. Contrast/comparison
    if contains_contrast_or_comparison(text):
        signals.append('analytical')
    
    return signals
```

---

### Phase 2: Fine-Tuned Models (Better Quality)

**Training Data:**
- Annotated corpus of "great writing" examples
- Human-rated passages (scholars, literary critics)
- Historical "famous quotes" databases

**Models:**
```python
# Fine-tuned model for "great writing" detection
from transformers import AutoModelForSequenceClassification

great_writing_model = AutoModelForSequenceClassification.from_pretrained(
    'chrystallum/great-writing-detector'
)

def detect_great_writing(text):
    inputs = tokenizer(text, return_tensors='pt')
    outputs = great_writing_model(**inputs)
    probability = torch.softmax(outputs.logits, dim=-1)
    return {
        'is_great_writing': probability[0][1] > 0.7,
        'confidence': probability[0][1].item(),
        'reasoning': extract_attention_weights(inputs)  # Why it's great
    }
```

---

### Phase 3: LLM-Assisted Detection (Current Best)

**Prompt Engineering:**
```python
GREAT_WRITING_PROMPT = """
You are analyzing historical prose to identify passages of exceptional 
literary and intellectual merit. Consider:

1. **Stylistic Excellence**: Rhetorical devices, sentence craft, vocabulary
2. **Semantic Depth**: Layers of meaning, insights, synthesis
3. **Emotional Resonance**: Power to move, evoke empathy, inspire
4. **Historical Significance**: Captures moment, explains causality
5. **Universal Truth**: Transcends time/context

Identify passages that exemplify "great writing" - prose that is:
- Beautiful and memorable
- Insightful and revealing
- Emotionally powerful
- Historically significant
- Universally applicable

Text to analyze:
{text}

Provide:
1. Passages that qualify as "great writing" (with scores 1-10)
2. Reasoning for each selection
3. Stylistic/semantic features that make it great
4. Historical/emotional context
"""
```

**LLM Response Structure:**
```json
{
  "great_passages": [
    {
      "text": "exact quote",
      "start_char": 1250,
      "end_char": 1380,
      "quality_score": 9.2,
      "reasoning": {
        "stylistic": "Parallel structure creates rhythm",
        "semantic": "Reveals character motivation through metaphor",
        "emotional": "Evokes empathy for difficult choice",
        "historical": "Captures turning point moment",
        "universal": "Speaks to timeless human dilemma"
      },
      "features": {
        "rhetorical_devices": ["metaphor", "parallelism", "alliteration"],
        "insight_type": "character_revelation",
        "emotional_valence": 0.75,
        "causal_language": true
      }
    }
  ]
}
```

---

## Integration with Chrystallum Extraction Pipeline

### Enhanced Citation Extraction

```python
def extract_citations_with_quality(text, author, work, context):
    """
    Extract citations, prioritizing "great writing" passages
    """
    
    # 1. Segment text into potential citations
    segments = segment_text(text, min_length=50, max_length=500)
    
    # 2. Score each segment
    scored_segments = []
    for segment in segments:
        scores = score_great_writing(segment, context)
        scored_segments.append({
            'text': segment,
            'scores': scores,
            'composite_score': scores['composite_score']
        })
    
    # 3. Filter and rank
    great_writing_threshold = 0.75
    top_passages = [
        s for s in scored_segments 
        if s['composite_score'] >= great_writing_threshold
    ]
    
    # 4. Create Citation entities
    citations = []
    for passage in sorted(top_passages, 
                         key=lambda x: x['composite_score'], 
                         reverse=True):
        citation = create_citation_entity(
            prose=passage['text'],
            author=author,
            work=work,
            quality_metadata={
                'great_writing_score': passage['composite_score'],
                'stylistic_score': passage['scores']['breakdown']['stylistic'],
                'semantic_score': passage['scores']['breakdown']['semantic'],
                'emotional_score': passage['scores']['breakdown']['emotional'],
                'historical_score': passage['scores']['breakdown']['historical'],
                'reasoning': passage['scores']['features']
            }
        )
        citations.append(citation)
    
    return citations
```

---

## Citation Entity Enhancement

### Add Quality Metadata to Citations

```cypher
(citation:Citation {
  // ... existing properties ...
  
  // Quality scoring
  great_writing_score: 9.2,
  stylistic_score: 8.5,
  semantic_score: 9.5,
  emotional_score: 8.8,
  historical_score: 9.0,
  
  // Quality reasoning
  quality_reasoning: {
    stylistic: 'Parallel structure creates rhythm, metaphor illuminates concept',
    semantic: 'Reveals character motivation, synthesizes historical forces',
    emotional: 'Evokes empathy for difficult choice, captures universal dilemma',
    historical: 'Captures turning point moment, explains causal chain'
  },
  
  // Detected features
  rhetorical_devices: ['metaphor', 'parallelism', 'alliteration'],
  insight_type: 'character_revelation',
  emotional_valence: 0.75,
  contains_causal_language: true,
  quotability_score: 9.5,
  
  // Classification
  is_great_writing: true,
  is_quotable: true,
  is_insightful: true,
  is_historically_significant: true
})
```

---

## Hybrid Approach: AI + Human Curation

### Best Strategy for Production

**1. AI Pre-filtering:**
- Extract all potential citations
- Score for "great writing" quality
- Flag top 10-20% for human review

**2. Human Curation:**
- Scholars review AI-selected passages
- Validate quality scores
- Add nuance AI misses
- Expand with human-identified gems

**3. Continuous Learning:**
- Use human corrections to improve models
- Track which AI-detected passages humans agree with
- Refine scoring weights based on feedback

```python
def hybrid_extraction(text, author, work, context, human_curator=None):
    # AI extraction
    ai_citations = extract_citations_with_quality(text, author, work, context)
    
    # Human curation (if available)
    if human_curator:
        human_citations = human_curator.identify_great_writing(text)
        
        # Merge and deduplicate
        all_citations = merge_citations(ai_citations, human_citations)
        
        # Learn from human selections
        update_model_weights(all_citations, human_feedback=True)
    else:
        all_citations = ai_citations
    
    return all_citations
```

---

## Example: Detecting Great Writing

### Sample Text (Suetonius)

> "When news was brought that Gaius Caesar was approaching with an army and was already on his way to Rome, Caesar crossed the Rubicon, saying 'The die is cast.' This act marked the beginning of civil war, setting in motion events that would end the Roman Republic and usher in the age of the Empire."

**AI Analysis:**

**Stylistic:**
- ✅ Parallel structure: "approaching... already on his way"
- ✅ Memorable quote: "The die is cast"
- ✅ Causal chain: "act marked... setting in motion... would end"
- Score: 8.5/10

**Semantic:**
- ✅ Synthesizes cause → immediate effect → long-term consequences
- ✅ Explains historical significance (Republic → Empire)
- ✅ Dense information: event + quote + consequences
- Score: 9.2/10

**Emotional:**
- ✅ Dramatic tension: approaching army
- ✅ Memorable phrase: quotable
- ✅ Historical weight: end of Republic
- Score: 8.8/10

**Historical:**
- ✅ Captures turning point moment
- ✅ Causal explanation of significance
- ✅ Links to broader historical narrative
- Score: 9.0/10

**Composite Score: 8.9/10** → **Great Writing** ✅

---

## Limitations & Considerations

### What AI Still Struggles With

1. **Cultural Context:**
   - Understanding period-appropriate beauty standards
   - Recognizing allusions to contemporary events
   - Appreciating period-specific humor/satire

2. **Subjective Taste:**
   - Different readers value different qualities
   - Personal preferences influence judgment
   - Cultural background affects appreciation

3. **Nuanced Judgment:**
   - Context-dependent quality (mediocre passage in great work)
   - Comparative quality (good vs. great)
   - Intentional "bad writing" for effect

### Mitigation Strategies

1. **Multi-model ensemble** - Combine different approaches
2. **Human-in-the-loop** - Always allow human override
3. **Community scoring** - Aggregate multiple human judgments
4. **Context-aware scoring** - Adjust thresholds by period/genre
5. **Continuous refinement** - Learn from feedback

---

## Recommended Implementation

### Immediate (Rule-Based)
- ✅ Implement quick heuristics
- ✅ Detect rhetorical devices
- ✅ Score quotability
- ✅ Identify insight verbs

### Short-Term (Fine-Tuned Models)
- ✅ Train on annotated "great writing" corpus
- ✅ Use historical quote databases as training data
- ✅ Fine-tune BERT/RoBERTa for quality detection

### Long-Term (Hybrid System)
- ✅ AI pre-filtering with quality scores
- ✅ Human curation layer
- ✅ Continuous learning from feedback
- ✅ Multi-dimensional quality metadata

---

## Summary

**The Challenge:**
Identifying "great writing" is inherently subjective and multi-dimensional. AI cannot perfectly replicate human aesthetic judgment, but can use **proxy signals** that correlate with what humans recognize as great.

**The Solution:**
1. **Multi-dimensional scoring** (stylistic, semantic, emotional, historical, comparative)
2. **Composite quality score** (weighted combination)
3. **LLM-assisted detection** (using sophisticated prompts)
4. **Hybrid approach** (AI pre-filtering + human curation)
5. **Quality metadata** (store scores and reasoning in Citation entities)

**Key Insight:**
AI can detect **signals that indicate great writing**:
- ✅ Rhetorical sophistication (devices, structure)
- ✅ Semantic density (insights per word)
- ✅ Emotional resonance (sentiment, intensity)
- ✅ Historical significance (causal explanations, turning points)
- ✅ Memorability (quotability, unique phrasing)

**This enables:**
- ✅ AI to identify potentially great writing
- ✅ Prioritize high-quality passages for extraction
- ✅ Store quality scores for citation ranking
- ✅ Support human curation workflow
- ✅ Learn and improve over time

**The result:** Citations in Chrystallum will include not just any prose, but the **particularly insightful and well-written** passages that humans recognize as valuable.

---

## Practical LLM Prompt Template

### For Use in Chrystallum Extraction Pipeline

```python
GREAT_WRITING_DETECTION_PROMPT = """
You are analyzing historical prose to identify passages of exceptional 
quality - the kind of writing that scholars quote, that captures moments 
profoundly, and that readers remember.

Identify passages that are:
1. **Stylistically excellent** - Uses rhetorical devices, memorable phrasing, 
   elegant structure
2. **Semantically rich** - Reveals insights, explains causality, synthesizes 
   complex ideas
3. **Emotionally resonant** - Evokes feeling, creates empathy, captures 
   human experience
4. **Historically significant** - Marks turning points, explains why events 
   mattered, captures era-defining moments
5. **Universally applicable** - Truths that transcend context, insights that 
   apply broadly

For each passage you identify, provide:
- The exact text (with character offsets)
- Quality score (1-10)
- Brief reasoning: What makes this "great writing"?
- Detected features: rhetorical devices, insight type, emotional impact

Source text:
{text}

Context: {author}, {work}, {period}

Return JSON with structure:
{{
  "great_passages": [
    {{
      "text": "exact quote",
      "start_char": 1234,
      "end_char": 1456,
      "quality_score": 9.2,
      "reasoning": "Brief explanation of why this is great writing",
      "features": {{
        "rhetorical_devices": ["metaphor", "parallelism"],
        "insight_type": "character_revelation",
        "emotional_valence": 0.75,
        "historical_significance": "turning_point"
      }}
    }}
  ]
}}
"""
```

### Simplified Python Implementation

```python
import re
from typing import List, Dict
import json

def extract_great_writing(text: str, author: str, work: str, 
                         period: str, llm_client) -> List[Dict]:
    """
    Extract "great writing" passages using LLM
    """
    
    prompt = GREAT_WRITING_DETECTION_PROMPT.format(
        text=text,
        author=author,
        work=work,
        period=period
    )
    
    response = llm_client.complete(prompt)
    result = json.loads(response)
    
    return result.get('great_passages', [])

def create_citations_with_quality(passages: List[Dict], 
                                 author_id: str, 
                                 work_id: str) -> List[Dict]:
    """
    Create Citation entities with quality metadata
    """
    citations = []
    
    for passage in passages:
        citation = {
            'prose': passage['text'],
            'citation': f"{author_id}, {work_id}, lines {passage['start_char']}-{passage['end_char']}",
            'quality_score': passage['quality_score'],
            'quality_reasoning': passage['reasoning'],
            'rhetorical_devices': passage['features'].get('rhetorical_devices', []),
            'insight_type': passage['features'].get('insight_type'),
            'emotional_valence': passage['features'].get('emotional_valence'),
            'historical_significance': passage['features'].get('historical_significance'),
            'is_great_writing': passage['quality_score'] >= 7.5,
            'attributed_to': author_id,
            'extracted_from': work_id
        }
        citations.append(citation)
    
    return citations
```

---

## Updated Citation Schema

### Add Quality Properties to Citation Entity

```cypher
(citation:Citation {
  // ... existing properties ...
  
  // Quality scoring (0-10)
  quality_score: 9.2,
  stylistic_score: 8.5,
  semantic_score: 9.5,
  emotional_score: 8.8,
  historical_score: 9.0,
  
  // Quality classification
  is_great_writing: true,  // quality_score >= 7.5
  is_quotable: true,
  is_insightful: true,
  is_historically_significant: true,
  
  // Quality reasoning
  quality_reasoning: 'Parallel structure creates rhythm; metaphor illuminates concept; reveals character motivation; captures turning point moment',
  
  // Detected features
  rhetorical_devices: ['metaphor', 'parallelism', 'alliteration'],
  insight_type: 'character_revelation',
  emotional_valence: 0.75,
  contains_causal_language: true,
  quotability_score: 9.5,
  
  // Detection metadata
  detected_by: 'llm_great_writing_detector_v1.0',
  detection_confidence: 0.92
})
```

---

## Bottom Line

**Can AI perfectly identify great writing?** No - it's inherently subjective.

**Can AI identify passages that are MORE LIKELY to be great writing?** Yes - using multi-dimensional signals:
- Rhetorical sophistication
- Semantic depth
- Emotional resonance
- Historical significance
- Memorability/quotability

**Best Approach:**
1. **AI pre-filters** using quality scores
2. **Human curators review** top-scoring passages
3. **Hybrid system** learns from human feedback
4. **Store quality metadata** for ranking/sorting

**This gives you** citations prioritized by quality, making it easier for humans to find the gems, while still capturing comprehensive coverage.

