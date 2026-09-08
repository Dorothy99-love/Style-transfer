normal_prompt= """Evaluate the quality of a summary written in a popular science style for a scientific article, targeting the high-school students audience. You must evaluate the summary along three dimensions:

1.Style transfer intensity: the degree to which the scientific content has been effectively transformed into a more accessible, popular-science style referring to well-known popular science magazines such as "WIRED" or "National Geographic".
2.Content preservation: how accurately the summary reflects the original article, including all major claims, methodologies, findings and contributions.
3.Language Naturalness: the degree to which the summary reads like human-written text.

Each dimension should be rated on a scale from 1 (worst) to 5 (best).

            
You should rate on a scale from 1 (worst) to 5 (best).
Format your answer output exactly as follows:
Explanation:
<Evaluation for each dimension, including lists of strengths and weaknesses etc.>

Separate scores:
Style transfer intensity: <1-5>
Content preservation: <1-5>
Language naturalness: <1-5>

Total rating:
You should rate the total score on a scale from 1 (worst) to 5 (best) according to separate scores."""