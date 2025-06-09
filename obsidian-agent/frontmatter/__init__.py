from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Post:
    content: str
    metadata: Dict[str, any] = field(default_factory=dict)


def loads(text: str) -> Post:
    if text.startswith('---'):
        end = text.find('---', 3)
        if end != -1:
            body = text[end+3:].lstrip('\n')
            return Post(body, {})
    return Post(text, {})


def dumps(post: Post) -> str:
    return post.content
