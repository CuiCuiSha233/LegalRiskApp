import asyncio
from openai import AsyncOpenAI
from backend.config import PROMPT_CONFIGS, SUMMARY_PROMPT, DEFAULT_MODEL
from backend.pdf_generator import truncate_text, MAX_CONTENT_LENGTH


async def call_llm(client, model, system_prompt, user_content, max_tokens=160000):
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.7,
            max_tokens=max_tokens,
        )
        report = response.choices[0].message.content

        lines = report.split("\n")
        cleaned_lines = []
        for line in lines:
            if "日期" in line or "出具人" in line or "注：" in line:
                continue
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()

    except Exception as e:
        return f"模型调用失败 ({model}): {str(e)}"


async def call_llm_stream(
    client, model, system_prompt, user_content, max_tokens=160000
):
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.7,
            max_tokens=max_tokens,
            stream=True,
        )

        full_content = ""
        async for chunk in response:
            delta = chunk.choices[0].delta.content
            if delta:
                full_content += delta
                yield delta

        lines = full_content.split("\n")
        cleaned_lines = []
        for line in lines:
            if "日期" in line or "出具人" in line or "注：" in line:
                continue
            cleaned_lines.append(line)
        yield "\n[FINAL]" + "\n".join(cleaned_lines).strip()

    except Exception as e:
        yield f"[ERROR]模型调用失败 ({model}): {str(e)}"


async def run_expert_analysis(client, content_to_analyze, all_configs):
    content_to_analyze = truncate_text(content_to_analyze, MAX_CONTENT_LENGTH)
    tasks = []
    for key, cfg in all_configs.items():
        tasks.append(call_llm(client, cfg["model"], cfg["prompt"], content_to_analyze))
    results = await asyncio.gather(*tasks)
    return results


async def run_expert_analysis_stream(client, content_to_analyze, all_configs):
    content_to_analyze = truncate_text(content_to_analyze, MAX_CONTENT_LENGTH)
    streams = []
    for key, cfg in all_configs.items():
        streams.append(
            call_llm_stream(client, cfg["model"], cfg["prompt"], content_to_analyze)
        )
    return streams


async def run_summary_analysis(client, reports, all_configs):
    summary_cfg = all_configs.get("summary", {})
    model = summary_cfg.get("model", DEFAULT_MODEL)
    prompt = summary_cfg.get("prompt", SUMMARY_PROMPT)

    combined_reports = (
        f"专家1意见 ({all_configs['expert1']['name']}): {reports[0]}\n\n"
        f"专家2意见 ({all_configs['expert2']['name']}): {reports[1]}\n\n"
        f"专家3意见 ({all_configs['expert3']['name']}): {reports[2]}"
    )
    combined_reports = truncate_text(combined_reports, MAX_CONTENT_LENGTH)
    return await call_llm(client, model, prompt, combined_reports)


async def run_summary_analysis_stream(client, reports, all_configs):
    summary_cfg = all_configs.get("summary", {})
    model = summary_cfg.get("model", DEFAULT_MODEL)
    prompt = summary_cfg.get("prompt", SUMMARY_PROMPT)

    combined_reports = (
        f"专家1意见 ({all_configs['expert1']['name']}): {reports[0]}\n\n"
        f"专家2意见 ({all_configs['expert2']['name']}): {reports[1]}\n\n"
        f"专家3意见 ({all_configs['expert3']['name']}): {reports[2]}"
    )
    combined_reports = truncate_text(combined_reports, MAX_CONTENT_LENGTH)

    async for chunk in call_llm_stream(client, model, prompt, combined_reports):
        yield chunk
