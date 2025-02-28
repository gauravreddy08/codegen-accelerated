import cssutils
from collections import deque
import uuid
import re
import logging
import tiktoken

cssutils.log.setLevel(logging.CRITICAL)

def count_tokens(text):
    encoding = tiktoken.encoding_for_model("gpt-4o")
    tokens = encoding.encode(text)
    return len(tokens)

def parse_css(input_text, llm_output=False):
    sheet = cssutils.parseString(input_text)
    code = deque()
    hashmap = set()

    for rule in sheet:
        if rule.type in [rule.STYLE_RULE]:
            code.append((rule.selectorText, rule.cssText))
            if llm_output: hashmap.add(rule.selectorText)

        elif rule.type in [rule.MEDIA_RULE]:    
            code.append((rule.media.mediaText, rule.cssText))
            if llm_output: hashmap.add(rule.media.mediaText)

        elif rule.type in [rule.COMMENT]:
            if rule.cssText.startswith('/* unchanged code */'):
                code.append((f'uc/{uuid.uuid4()}', None))

            elif rule.cssText.startswith('/* deleted block'):
                selector = re.search(r'/* deleted block (\w+)', rule.cssText).group(1)
                code.append((selector, None))
                if llm_output: hashmap.add(selector)

            else:
                code.append((f'comment/{rule.cssText}', rule.cssText))
                if llm_output: hashmap.add(rule.cssText)
        else:
            raise ValueError(f'Unknown rule type: {rule.type}')
    
    return (code, hashmap) if llm_output else code

if __name__ == "__main__":
    with open('input.css', 'r') as f:
        blocks = parse_css(f.read())
    
