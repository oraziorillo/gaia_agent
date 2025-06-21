entity_analysis_prompt = """
Analyze the following complex query and identify specific entities, people, places, 
concepts, organizations, events, or topics that likely have Wikipedia pages.
    
Query: "{query}"
    
Instructions:
- Focus on proper nouns, specific names, and well-defined concepts
- Avoid overly generic terms unless they're central to the query
- Consider both direct mentions and implied entities
- Return only the most relevant entities that would have dedicated Wikipedia pages
- Format your response as a simple semicolon-separated list, e.g. "Michael Jackson;Madonna;Chanel"
- You can only use words from the query in the list
- Keep the list as short as possible
- If no clear Wikipedia-worthy entities are found, return "NONE"
    
Potential Wikipedia entities:
"""

synthesis_prompt = """
You are informing another AI agent about information found on Wikipedia pages that may be relevant to answering a complex query. You are NOT answering the query yourself - you are simply reporting what information you found.

Original Query: "{query}"

Wikipedia Information Found:
{context}

Instructions:
- Report only the information from Wikipedia that appears relevant to the query
- Do NOT attempt to answer the original query directly
- Do NOT make inferences or draw conclusions beyond what's stated in the Wikipedia content
- If no relevant information was found, respond with exactly: "NONE"
- Structure your response as: "Based on the Wikipedia pages I searched, here is the relevant information I found: [information]"
- Be concise but thorough in reporting the relevant facts

Your response:
"""