
1. Currently the system has year nodes from -2000 to 2025 with followed by/ preceded by edges
2. This is the original temporal backbone - any claim with a temporal aspect must tether to a yearly backbone
3. the decision to use year was one of granularity. i did not want to get down to daily over thousands of years - but this can be debated
	1. Clearly a better model at a minimum is year ->decade ->century ->millennia
	2. Outside of year, all these temporal concepts are curated and not really global but cultural. 
	3. Perhaps there is a way to leverage edges to enrich the year backbone
	4. dates are fuzzy - the best practice is start, end, earliest start, latest end conceptERA
	5. ERAs
		1. another contrived concept which is really cultural
		2. helpful is the abiliity to see a stacked timeline 
			1. pollitical era
			2. economic era
			3. technical era
			4. various facets
			5. by culture
			6. We have periodo - which we can leverage along with other federations
			7. another issue is date ranges. 
				1. the recommendation was to only tie an event to start and end dates, so in a timeline or graph navigation view the middle years would not reveal the relationship. the alternative is to edge every year of the event from start to end
		### 3. Perplexity response:
		You’ve got everything you need here to build a very clean, historian-grade Period layer:

- A human classification plan (tiers 1–4).[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/56d011ad-0a9f-419d-a537-20e8142603dc/PERIOD_CLASSIFICATION_PLAN.md)]​
    
- A machine-readable period table with dates, locations, and facet tags.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cb359094-cf85-41fb-9ef5-e94df223b520/time_periods.csv)]​
    
- Supplemental candidate lists and mappings to LCSH/Wikidata/PeriodO.[more-periods.md+2](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/482c92db-d701-4c42-952b-0f0a8f2453b9/more-periods.md)
    

At a high level, these pieces fit together like this:

1. `time_periods.csv` is your **primary seed list** of candidate periods, with:
    
    - QID + label.
        
    - Start/end year.
        
    - One or more locations (region/country nodes).
        
    - One or more facet tags (`CulturalFacet`, `PoliticalFacet`, `ArchaeologicalFacet`, etc.) and the corresponding relationship names (`HAS_CULTURAL_FACET`, `HAS_POLITICAL_FACET`, …).[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cb359094-cf85-41fb-9ef5-e94df223b520/time_periods.csv)]​
        
2. `PERIOD_CLASSIFICATION_PLAN.md` tells you, for ~130+ of those (or related) entries, **what kind of thing each really is**:
    
    - Tier 1: true historiographic periods → keep as `:Period`.
        
    - Tier 2: short crisis/phase → convert to `:Event`.
        
    - Tier 3: institutional spans → convert to something like `:InstitutionalSpan`.
        
    - Tier 4: problematic/discipline/mis-specified → delete or reclassify.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/56d011ad-0a9f-419d-a537-20e8142603dc/PERIOD_CLASSIFICATION_PLAN.md)]​
        
3. `more-periods.md` is essentially a **larger candidate list** of Wikidata “period-like” entities you could eventually run through the same tiering framework.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/482c92db-d701-4c42-952b-0f0a8f2453b9/more-periods.md)]​
    
4. `periodo-dataset.csv` plus `period_lcsh_mapping_phase1_*.json` give you the **authority alignment layer**:
    
    - PeriodO concepts and their temporal bounds.
        
    - Mappings between your periods (via QIDs) and LCSH/other authority headings, which will become `SubjectConcept` + `ALIGNED_WITH` edges in your Subject layer.[period_lcsh_mapping_phase1_20260108_134151.json+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/02d7a1f9-2fd7-426f-b625-9559ebacef78/period_lcsh_mapping_phase1_20260108_134151.json)
        

If you want, next we can make this concrete by defining a **Period ingestion + classification pipeline**:

- Step 1: Load `time_periods.csv` and create `:Period` nodes with `start`/`end`, `STARTS_IN_YEAR`/`ENDS_IN_YEAR`, and facet edges.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/cb359094-cf85-41fb-9ef5-e94df223b520/time_periods.csv)]​
    
- Step 2: Apply the Tier 1–4 rules from `PERIOD_CLASSIFICATION_PLAN.md` to relabel some of those as `:Event` or `:InstitutionalSpan` or drop them.[[ppl-ai-file-upload.s3.amazonaws](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/56d011ad-0a9f-419d-a537-20e8142603dc/PERIOD_CLASSIFICATION_PLAN.md)]​
    
- Step 3: Use `periodo-dataset.csv` + the JSON mappings to add authority metadata and `ALIGNED_WITH` links to PeriodO/LCSH concepts.[periodo-dataset.csv+1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/100192890/7bce58bb-f521-40e3-a9e8-690964d81d3c/periodo-dataset.csv)
    

Tell me which of those steps you’d like to design first (e.g., “ingestion from `time_periods.csv`” vs “apply Tier 1–4 transformations”), and I’ll sketch the exact schema-aligned rules and example Cypher for it.


1. 
	