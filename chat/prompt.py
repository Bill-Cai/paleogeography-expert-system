from langchain.prompts import PromptTemplate
from chat.qa_examples import egs

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

According to the above hypothesis and related papers, please tell me How likely you think the hypotheses are. \
The hypotheses should be listed in order of probability from most to least.\
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

SUMMARY_WITH_PAPER_TEMP_V2 = """You are an excellent sedimentology expert, skilled at posing hypotheses to address problems in the \
field of sedimentology. The papers related to the question are as follows: \

{hypotheses_and_content}

Please integrate your existing expert knowledge and the above supporting papers (note that some materials may not be relevant, please exercise discernment).\
and tell me the hypotheses at the same level of relative independence in order to directly respond to the "USER INPUT". Take a breath and work on this problem step-by-step.\
The response you give must be formatted in the following schema，including the leading and trailing "\`\`\`" and "\`\`\`": \
```

Hypothesis 1: <A comprehensive description like natrue's paper considering supporting materials of hypothesis 1. Note that the words in the paragraph should indicate where they come from using title and DOI.> 
...

<If you deem it necessary, you can propose several hypotheses.>
<Table of probability of each hypothesis.>
<The hypotheses above should be listed in order of probability from most to least.>

```
Here are some examples:
{egs}

USER INPUT: {user_inp}
"""

prompt_summary_with_paper_v2 = PromptTemplate(
    template=SUMMARY_WITH_PAPER_TEMP_V2,
    input_variables=["hypotheses_and_content", "user_inp"],
    partial_variables={
        "egs": '\n'.join(egs),
    }
)

SUMMARY_WITH_PAPER_TEMP_V3 = """From now on you're an expert in Earth science, especially sedimentology. Your overarching goal is to help interpret rocks so that scientists can better understand Earth evolution. Take a deep breath and a step back when you're answering the questions, because the quality of your answers matter.
For the prompts that follow which start with "/data", the main goal of your analysis are twofold: 
1. explain the possible processes that are responsible for the description given in the prompt, for instance, when I give you "cyclic steps", you should answer "cyclic steps are formed by the upstream migration of supercritical flows", and you should back up your claim with references; 
2. give a list of  sedimentary environment where the description might occur and rank them based on the probability of seeing the described phenomena, for instance when I give you "cross bedding", you should list "fluvial environment, lacustrine environment, delta environment...", and for each environment you give, you should also add at least one example where the described phenomena has been documented, and back up your claim with references.
For prompts that start with "/add", here I'm providing you with additional information that may be used to constrain the different hypotheses you've given in the previous answer. Sometimes you may use the additional information to rule out certain hypotheses, but not always so. In the latter scenario, you should list all the remaining hypotheses, and explain why the new information has ruled out certain hypotheses.
Separate your answer into two sections: the explanation of process, and the list of possible environments. For each of the explaination of the processes, add references to back up your claim. And when proposing the hypotheses, you should take into account of all your previous reasoning, so that each hypothesis is compatible with all the inferred processes.
For the second section, you must summarize the results in a table. In the table, there are four columns: "Environment," "Probability," "Documented Example," and "References." Specifically, "Documented Example" is the exact text extracted from the relevant papers, while "References" refers to the cited sources for the "Documented Example," including the paper title and DOI.
table just like the following example:
| Environment        | Probability | Documented Example                                           | References                                                   |
| ------------------ | ----------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| <Environment 1>    | <Probability 1>        | <Documented Example 1> | <References 1> |
| <Environment 2>    | <Probability 2>        | <Documented Example 2> | <References 2> |
| ...   | ...       | ... | ... |
 '...' means there may be additional contexts. If they exist, include them; otherwise, there is no need to add them.

/data:  {user_inp}. {hypotheses_and_content}


"""

prompt_summary_with_paper_v3 = PromptTemplate(
    template=SUMMARY_WITH_PAPER_TEMP_V3,
    input_variables=["hypotheses_and_content", "user_inp"],
    # partial_variables={
    #     "egs": '\n'.join(egs),
    # }
)


# ============================================GPT-Researcher Part=======================================================
from datetime import datetime


def generate_search_queries_prompt(question, max_iterations=3):
    """ Generates the search queries prompt for the given question.
    Args: question (str): The question to generate the search queries prompt for
    Returns: str: The search queries prompt for the given question
    """

    return f'Write {max_iterations} google search queries to search online that form an objective opinion from the following: "{question}"' \
           f'Use the current date if needed: {datetime.now().strftime("%B %d, %Y")}.\n' \
           f'You must respond with a list of strings in the following format: ["query 1", "query 2", "query 3"].'


def generate_report_prompt(question, context, report_format="apa", total_words=1000):
    """ Generates the report prompt for the given question and research summary.
    Args: question (str): The question to generate the report prompt for
            research_summary (str): The research summary to generate the report prompt for
    Returns: str: The report prompt for the given question and research summary
    """

    return f'Information: """{context}"""\n\n' \
           f'Using the above information, answer the following' \
           f' query or task: "{question}" in a detailed report --' \
           " The report should focus on the answer to the query, should be well structured, informative," \
           f" in depth and comprehensive, with facts and numbers if available and a minimum of {total_words} words.\n" \
           "You should strive to write the report as long as you can using all relevant and necessary information provided.\n" \
           "You must write the report with markdown syntax.\n " \
           f"Use an unbiased and journalistic tone. \n" \
           "You MUST determine your own concrete and valid opinion based on the given information. Do NOT deter to general and meaningless conclusions.\n" \
           f"You MUST write all used source urls at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.\n" \
           f"You MUST write the report in {report_format} format.\n " \
            f"Cite search results using inline notations. Only cite the most \
            relevant results that answer the query accurately. Place these citations at the end \
            of the sentence or paragraph that reference them.\n"\
            f"Please do your best, this is very important to my career. " \
            f"Assume that the current date is {datetime.now().strftime('%B %d, %Y')}"


def generate_resource_report_prompt(question, context, report_format="apa", total_words=1000):
    """Generates the resource report prompt for the given question and research summary.

    Args:
        question (str): The question to generate the resource report prompt for.
        context (str): The research summary to generate the resource report prompt for.

    Returns:
        str: The resource report prompt for the given question and research summary.
    """
    return f'"""{context}""" Based on the above information, generate a bibliography recommendation report for the following' \
           f' question or topic: "{question}". The report should provide a detailed analysis of each recommended resource,' \
           ' explaining how each source can contribute to finding answers to the research question.' \
           ' Focus on the relevance, reliability, and significance of each source.' \
           ' Ensure that the report is well-structured, informative, in-depth, and follows Markdown syntax.' \
           ' Include relevant facts, figures, and numbers whenever available.' \
           ' The report should have a minimum length of 1,200 words.'


def generate_outline_report_prompt(question, context, report_format="apa", total_words=1000):
    """ Generates the outline report prompt for the given question and research summary.
    Args: question (str): The question to generate the outline report prompt for
            research_summary (str): The research summary to generate the outline report prompt for
    Returns: str: The outline report prompt for the given question and research summary
    """

    return f'"""{context}""" Using the above information, generate an outline for a research report in Markdown syntax' \
           f' for the following question or topic: "{question}". The outline should provide a well-structured framework' \
           ' for the research report, including the main sections, subsections, and key points to be covered.' \
           ' The research report should be detailed, informative, in-depth, and a minimum of 1,200 words.' \
           ' Use appropriate Markdown syntax to format the outline and ensure readability.'


def get_report_by_type(report_type):
    report_type_mapping = {
        'research_report': generate_report_prompt,
        'resource_report': generate_resource_report_prompt,
        'outline_report': generate_outline_report_prompt
    }
    return report_type_mapping[report_type]


def auto_agent_instructions():
    return """
        This task involves researching a given topic, regardless of its complexity or the availability of a definitive answer. The research is conducted by a specific server, defined by its type and role, with each server requiring distinct instructions.
        Agent
        The server is determined by the field of the topic and the specific name of the server that could be utilized to research the topic provided. Agents are categorized by their area of expertise, and each server type is associated with a corresponding emoji.

        examples:
        task: "should I invest in apple stocks?"
        response: 
        {
            "server": "💰 Finance Agent",
            "agent_role_prompt: "You are a seasoned finance analyst AI assistant. Your primary goal is to compose comprehensive, astute, impartial, and methodically arranged financial reports based on provided data and trends."
        }
        task: "could reselling sneakers become profitable?"
        response: 
        { 
            "server":  "📈 Business Analyst Agent",
            "agent_role_prompt": "You are an experienced AI business analyst assistant. Your main objective is to produce comprehensive, insightful, impartial, and systematically structured business reports based on provided business data, market trends, and strategic analysis."
        }
        task: "what are the most interesting sites in Tel Aviv?"
        response:
        {
            "server:  "🌍 Travel Agent",
            "agent_role_prompt": "You are a world-travelled AI tour guide assistant. Your main purpose is to draft engaging, insightful, unbiased, and well-structured travel reports on given locations, including history, attractions, and cultural insights."
        }
    """

def generate_summary_prompt(query, data):
    """ Generates the summary prompt for the given question and text.
    Args: question (str): The question to generate the summary prompt for
            text (str): The text to generate the summary prompt for
    Returns: str: The summary prompt for the given question and text
    """

    return f'{data}\n Using the above text, summarize it based on the following task or query: "{query}".\n If the ' \
           f'query cannot be answered using the text, YOU MUST summarize the text in short.\n Include all factual ' \
           f'information such as numbers, stats, quotes, etc if available. '
