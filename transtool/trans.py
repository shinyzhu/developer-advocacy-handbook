import os
import time
from dotenv import load_dotenv # pip3 install python-dotenv
load_dotenv()

import openai # pip3 install openai

OPENAI_MODEL = 'gpt-3.5-turbo'
DOC_PATH_SOURCE = '../'
DOC_PATH_TARGET = '../zh/'

def init_chatgpt():
    openai.organization = os.getenv("OPENAI_ORG")
    openai.api_key = os.getenv("OPENAI_API_KEY")
    print('init_chatgpt: ChatGPT inited.')

'''
Translate a paragraph by OpenAI
'''
def chatgpt_translate(content=''):
    if content == '':
        return ''
    
    time.sleep(1)

    messages = [
        {"role": "system", "content": "Translate the following content to Chinese. Keep the markdown format. Just return the translated content."},
        {"role": "user", "content": content}
        ]
    
    #print('chatgpt_translate: content submitted. ')

    response = openai.ChatCompletion.create(model=OPENAI_MODEL, messages=messages)

    translated = response.choices[0].message.content
    usage = response.usage

    print('chatgpt_translate: Content processed. usage: prompt_tokens={0}, completion_tokens={1}, total_tokens={2}'
          .format(usage.prompt_tokens, usage.completion_tokens, usage.total_tokens))

    return translated.strip()

'''
Append content to target file.
'''
def save_content_append(target, content=''):
    if content == '':
        return
    
    f = open(target, 'a')
    f.write(content)
    f.close()

'''
Let's do it!
'''
def main():
    doc_names = ['404.md', 'about.md', 'create-slide-decks.md', 'deliver-a-talk.md', 'final-words.md',
                'get-speaking-opportunities.md', 'index.md', 'prepare-for-outreach.md', 'prepare-slide-decks.md',
                'record.md', 'recording-talks.md', 'slide-checklist.md', 'talk-delivery-tips.md',
                'things-not-to-say-on-stage.md', 'toc.md', 'travel-and-conference-participation.md',
                'use-the-web.md', 'videos.md', 'what-is-developer-advocacy.md', 'working-from-your-own-computer.md',
                'working-with-your-company.md', 'working-with-your-competition.md', 'write-excellent-code-examples.md',
                'write-great-posts-and-articles.md']

    doc_index = 0 # 0 ~ 23
    doc_name = doc_names[doc_index]
    
    # It is the latest current_para_index in your log, example:
    # main: Translating paragraph - 10/60
    # It's 10 if you want to start from the 10th line
    start_para = 1

    print('main: Processing document [{}] - {}'.format(doc_index, doc_name))

    doc_target = os.path.join(DOC_PATH_TARGET, doc_name)

    paragraphs, frontmatters = load_paragraphs(doc_name)

    if start_para == 1:
        # It should be a new file when start from 1, so we import the frontmatter.
        # MANUAL CASE:
        # If error occured in the first paragraph, you need to manually remove the frontmatter from the target document.
        save_content_append(doc_target, '\n'.join(frontmatters))

    # translate and append to target file
    para_count = len(paragraphs)
    for idx, para in enumerate(paragraphs):
        # skip the translated paragraphs
        if (idx + 1) < start_para:
            print('main: Skip paragraph - {}/{}'.format(idx + 1, para_count))
        else:
            print('main: Translating paragraph - {}/{}'.format(idx + 1, para_count))
            # There will be some errors when calling the API
            # Be careful with the logs :) Good luck
            tran = chatgpt_translate(para)

            # append to target file
            save_content_append(doc_target, '\n\n{}'.format(tran))
    

'''
Load paramgraphs and frontmatters from a markdown document.
'''
def load_paragraphs(doc_name):
    doc = os.path.join(DOC_PATH_SOURCE, doc_name)
    print('load_paragraphs: Loading file {}'.format(doc))

    file = open(doc, 'r')
    content = file.read()
    file.close()

    lines = content.split('\n')

    paragraphs = []
    para_lines = []
    frontmatters = []
    in_frontmatter = False
    line_count = len(lines)

    for idx, l in enumerate(lines):
        print('load_paragraphs: Line {0}/{1}: {2}'.format(idx + 1, line_count, l))
        # ignore frontmatter
        if l.startswith('---'):
            in_frontmatter = not in_frontmatter # will occour 2 times
            frontmatters.append(l)
            print('load_paragraphs: Ignore frontmatter {0}/{1}: in_frontmatter: {2}'.format(idx + 1, line_count, in_frontmatter))
            continue

        if not in_frontmatter:
            # prepare paragraph in multiple lines
            if not l == '':
                # in a paragraph
                para_lines.append(l.strip())
                print('load_paragraphs: in_paragraph {0}/{1} -- {2}'.format(idx + 1, line_count, l))
            else:
                # paragraph break, the last line doesn't contain break
                if len(para_lines) > 0:
                    paragraphs.append(' '.join(para_lines))
                    para_lines = []
                print('load_paragraphs: paragraph_br {0}/{1} <> {2}'.format(idx + 1, line_count, l))
        else:
            frontmatters.append(l)

    # append the last paragraph
    paragraphs.append(' '.join(para_lines))

    return paragraphs, frontmatters


if __name__ == "__main__":
    init_chatgpt()
    main()