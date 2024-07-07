import asyncio
import re
import sys
import time
import threading

from chat.llm import generate_context, chat_completion
from chat.prompt import prompt_sys_init, prompt_summary_with_paper, prompt_summary_with_paper_v2, \
    prompt_summary_with_paper_v3
from chat.functions import stream_output, get_sub_queries
from config import cfg
# from db.MilvusPool import search_vec
from db.PostgresqlPool import search_vec_pg
from db.PostgresqlPool import pg_pool

from chat.agent import GPTResearcher
from context.compression import DB_MODE, SEARCH_API_MODE

ANSWER_PATTERN = r"```(.*?)```"
AGENT_ROLE_PROMPT = "You are an AI research assistant specializing in sedimentology, equipped with a vast database of geological knowledge. Your mission is to assist geologists and researchers in uncovering the secrets hidden within Earth's sedimentary layers. As a knowledgeable guide in the realm of sedimentology, you provide insights on sedimentary structures, analyze depositional environments, and offer assistance in the interpretation of sedimentary sequences. Your virtual presence serves as a valuable resource for Earth scientists, helping them navigate the intricate world of sediments and contributing to the understanding of Earth's dynamic history through the study of its geological archives."


class CountDownTask:
    def __init__(self):
        self._running = True  # 定义线程状态变量

    def terminate(self):
        self._running = False

    def start(self):
        self._running = True

    def three_dots(self):
        while True:
            for i in range(3):
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(0.7)
            sys.stdout.write('\b\b\b   \b\b\b')
            sys.stdout.flush()
            if not self._running:
                break


def start_countdown_task(msg):
    c = CountDownTask()
    t = threading.Thread(target=c.three_dots)
    print(msg, end='')
    t.start()
    return c, t


# def chat(user_input, msg_history=[], model=cfg.fast_llm_model, temperature=cfg.temperature,
#          max_tokens=None) -> str:
#     # step 1 - init hypothesis
#     c, t = start_countdown_task("Think about the possibilities")
#     prompt_init = prompt_sys_init.format(user_inp=user_input)
#     messages = generate_context(prompt_init, [], "user")
#     chat_res = chat_completion(messages, model, temperature, max_tokens)
#     extracted_text = re.findall(ANSWER_PATTERN, chat_res, re.DOTALL)
#     c.terminate()
#     t.join()
#
#     # step 2 - search
#     c, t = start_countdown_task("\nSearch for supporting material for the hypothesis")
#     print()
#     hypotheses = [i for i in extracted_text[0].strip().split("\n") if i != '']
#     # Extract the part after "Hypothesis" for each string in the list
#     sentences = [hypothesis.split(': ', 1)[1] for hypothesis in hypotheses]
#     related_sentences = search_vec(sentences)
#     c.terminate()
#     t.join()
#
#     # step 3 - think deeply and summary
#     c, t = start_countdown_task(f"\nThink deeply and summary")
#     hypotheses_and_content = ""
#     for i, s in enumerate(hypotheses):
#         hypotheses_and_content += f"\'{s}\' related paper as follows:\n"
#         for j, r in enumerate(related_sentences[i]):
#             hypotheses_and_content += f"{j + 1}. {r.to_ref()}\n"
#
#     prompt_summary = prompt_summary_with_paper.format(hypotheses_and_content=hypotheses_and_content)
#     messages = generate_context(prompt_summary, [], "user")
#     chat_res = chat_completion(messages, model, temperature, max_tokens)
#     extracted_res = re.findall(ANSWER_PATTERN, chat_res, re.DOTALL)
#     c.terminate()
#     t.join()
#     print("")
#
#     return extracted_res[0].strip()


def chat_v2(user_input, conn, msg_history=[], model=cfg.fast_llm_model, temperature=cfg.temperature,
            max_tokens=None) -> str:
    # step 1 - search
    c, t = start_countdown_task("Search for supporting material for the hypothesis")
    # related_sentences = search_vec(sentences=[user_input], limit=20)
    related_sentences = search_vec_pg(sentences=user_input, table_name='sedimentology_paper_sentence', conn=conn,
                                      limit=100)
    c.terminate()
    t.join()

    # step 2 - think deeply and summary (with paper)
    c, t = start_countdown_task(f"\nThink deeply and summary")
    hypotheses_and_content = "related paper as follows:\n"
    # for j, r in enumerate(related_sentences[0]):
    for j, r in enumerate(related_sentences):
        hypotheses_and_content += f"{j + 1}. {r.to_ref()}\n"

    prompt_summary = prompt_summary_with_paper_v2.format(hypotheses_and_content=hypotheses_and_content,
                                                         user_inp=user_input)
    messages = generate_context(prompt_summary, [], "user")
    chat_res = chat_completion(messages, model, temperature, max_tokens)
    extracted_res = re.findall(ANSWER_PATTERN, chat_res, re.DOTALL)
    c.terminate()
    t.join()
    print("Answer:")

    if len(extracted_res) == 0:
        return chat_res
    return extracted_res[0].strip()


def chat_v3_start(user_input, conn, msg_history=[], model=cfg.fast_llm_model, temperature=cfg.temperature,
                  max_tokens=None) -> str:
    # step 1 - search
    c, t = start_countdown_task("Search for supporting material for the hypothesis")
    # related_sentences = search_vec(sentences=[user_input], limit=20)
    related_sentences = search_vec_pg(sentences=user_input, table_name='sedimentology_paper_paragraph', conn=conn,
                                      limit=25)
    c.terminate()
    t.join()

    # step 2 - think deeply and summary (with paper)
    c, t = start_countdown_task(f"\nThink deeply and summary")
    hypotheses_and_content = "related paper as follows:\n"
    # for j, r in enumerate(related_sentences[0]):
    for j, r in enumerate(related_sentences):
        hypotheses_and_content += f"{j + 1}. {r.to_ref()}\n"

    prompt_summary = prompt_summary_with_paper_v3.format(hypotheses_and_content=hypotheses_and_content,
                                                         user_inp=user_input)
    messages = generate_context(prompt_summary, msg_history, "user")
    chat_res = chat_completion(messages, model, temperature, max_tokens)
    extracted_res = re.findall(ANSWER_PATTERN, chat_res, re.DOTALL)
    c.terminate()
    t.join()
    print("Answer:")

    if len(extracted_res) == 0:
        res = chat_res
    else:
        res = extracted_res[0].strip()
    generate_context(res, msg_history, "system")
    return res


def chat_v3_cycle(user_input, msg_history=[], model=cfg.fast_llm_model, temperature=cfg.temperature,
                  max_tokens=None) -> str:
    # step 2 - think deeply and summary (with paper)
    c, t = start_countdown_task(f"\nThink deeply and summary")
    messages = generate_context(f"/add: {user_input}", msg_history, "user")
    chat_res = chat_completion(messages, model, temperature, max_tokens)
    extracted_res = re.findall(ANSWER_PATTERN, chat_res, re.DOTALL)
    c.terminate()
    t.join()
    print("Answer:")

    if len(extracted_res) == 0:
        res = chat_res
    else:
        res = extracted_res[0].strip()
    generate_context(res, msg_history, "system")
    return res


# =====================================================================================================================


async def RAG_with_Agent_Chat(user_input, conn, msg_history=[], model=cfg.fast_llm_model, temperature=cfg.temperature,
                              max_token=None, websocket=None) -> str:
    await stream_output("logs", f"🔎 Running research for '{user_input}'...", websocket)
    await stream_output("logs", "🌍 Paleogeography Agent", websocket)
    # step 1: 分解问题 get sub-queries
    sub_queries = await get_sub_queries(user_input, AGENT_ROLE_PROMPT, cfg) + [user_input]
    await stream_output("logs",
                        f"🧠 I will conduct my research based on the following queries: {sub_queries}...", websocket)
    gpt_researcher = GPTResearcher(query=user_input, report_type="research_report", websocket=websocket)
    gpt_researcher.role = AGENT_ROLE_PROMPT
    # step 2: do search for sub-queries
    await gpt_researcher.sub_query(sub_queries)
    # step 3: get more detailed info in personal db
    for query in sub_queries:
        await stream_output("logs", f"\n🔎 Running research for '{query}' in DB...", websocket)
        related_sentences = search_vec_pg(sentences=query, table_name='sedimentology_paper_paragraph', conn=conn,
                                          limit=15)
        context = await gpt_researcher.get_similar_content_by_query(query, related_sentences, mode=DB_MODE)
        await stream_output("logs", f"📃 {context}", websocket)
        gpt_researcher.append_context(context)
    # step 4: generate report
    report = await gpt_researcher.generate_report()
    return report


# if __name__ == '__main__':
    # full_msg_history = []
    # mode = 3
    # if mode < 3:
    #     while True:
    #         conn = pg_pool.get_connection()
    #         user_input = input("User input: ")
    #         if user_input.lower() == "quit":
    #             break
    #         if mode == 1:
    #             print(chat(user_input, full_msg_history))
    #         elif mode == 2:
    #             print(chat_v2(user_input, conn, full_msg_history))
    # else:
    #     # 改用pg-vector
    #     conn = pg_pool.get_connection()
    #     user_input = input("User input: ")
    #     print(chat_v3_start(user_input, conn, full_msg_history))
    #     while True:
    #         user_input = input("User input: ")
    #         if user_input.lower() == "quit":
    #             break
    #         print(chat_v3_cycle(user_input, full_msg_history))
    # full_msg_history = []
    # conn = pg_pool.get_connection()
    # user_input = input("User input: ")
    # report = asyncio.run(RAG_with_Agent_Chat(user_input, conn, full_msg_history))

from backend.server import app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
