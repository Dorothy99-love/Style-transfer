G_Eval_prompt = """Evaluate the quality of a summary written in a popular science style for a scientific article, targeting the high-school students audience. You must evaluate the summary along three dimensions:

1.Style transfer intensity: the degree to which the scientific content has been effectively transformed into a more accessible, popular-science style referring to well-known popular science magazines such as "WIRED" or "National Geographic".
2.Content preservation: how accurately the summary reflects the original article, including all major claims and findings.
3.Language Naturalness: the degree to which the summary reads like human-written text.

Each dimension should be rated on a scale from 0.0 (worst) to 1.0 (best).
       
You should rate on a scale from 0.0 (worst) to 1.0 (best).

Format your answer output exactly as follows:
Explanation:
<Step-by-step evaluation for each dimension, including lists of strengths and weaknesses where applicable>

Separate scores:
Style transfer intensity: <0.0-1.0>
Content preservation: <0.0-1.0>
Language naturalness: <0.0-1.0>

Total rating:
You should rate the total score on a scale from 0.0 (worst) to 1.0 (best) according to separate scores"""