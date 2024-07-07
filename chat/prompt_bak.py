from langchain.prompts import PromptTemplate

SYS_INIT_TEMP = """You are an excellent sedimentology expert, skilled at posing hypotheses to address problems in the \
field of sedimentology. Please tell me the relatively independent hypotheses in order to respond to the "USER INPUT". \
The output should be formatted in the following schema，including the leading and trailing "\`\`\`" and "\`\`\`": \
```
Hypothesis 1: <Description of hypothesis 1>
Hypothesis 2: <Description of hypothesis 2>
Hypothesis 3: <Description of hypothesis 3>
```
USER INPUT: {user_inp}
"""

prompt_sys_init = PromptTemplate(
    template=SYS_INIT_TEMP,
    input_variables=["user_inp"]
)

SUMMARY_WITH_PAPER_TEMP = """We have found the following papers related to the hypotheses you proposed. \

{hypotheses_and_content}

According to the above hypothesis and related papers, please tell me the hypothesis and its supporting materials in which \
the sentences should be attributed.The hypotheses should be listed in order of probability from most to least.\
The output should be formatted in the following schema, including the leading and trailing "\`\`\`" and "\`\`\`":\
```
Hypothesis 1: <An essay paragraph like natrue's paper based on supporting materials of hypothesis 1. Note that the words in the paragraph should indicate where they come from using title and DOI.> 
Hypothesis 2: ...
Hypothesis 3: ...

<Table of probability of each hypothesis>
```
"""

prompt_summary_with_paper = PromptTemplate(
    template=SUMMARY_WITH_PAPER_TEMP,
    input_variables=["hypotheses_and_content"]
)
