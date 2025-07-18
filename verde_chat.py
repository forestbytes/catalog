import sys
# from langchain_community.llms import OpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()
load_dotenv()

def setup_llm(model_name=None, temperature=None):
    """Initialize LangChain with environment variables and error handling."""
    api_key = os.getenv("D2S_LLM_API_KEY")
    api_base = os.getenv("LLM_URL")
    if not api_key or not api_base:
        raise EnvironmentError("Missing D2S_LLM_API_KEY or LLM_URL in environment variables.")

    # model_name=model_name or os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
    # model_name=model_name or os.getenv("LLM_MODEL", "anvilgpt/llama3:70b") # Slow but robust answers
    # model_name=model_name or os.getenv("LLM_MODEL", "anvilgpt/mistral:latest") # Fast, good for dev and testing

    llm = ChatOpenAI(
        model_name = model_name or os.getenv("LLM_MODEL", "anvilgpt/deepseek-r1:70b"),
        temperature=temperature if temperature is not None else float(os.getenv("LLM_TEMPERATURE", "0")),
        openai_api_key=api_key,
        openai_api_base=api_base
    )
    return llm

def query_llm(question: str, **kwargs):
    """Send a query to the LLM and get a response, with error handling."""
    try:
        llm = setup_llm(**kwargs)
        # response = llm.predict(question)
        response = llm.invoke(question)
        if hasattr(response, 'content'):
            response = response.content

        return response
    except Exception as e:
        return f"Error querying LLM: {e}"

def main():
    """Main function to run the LLM query."""
    question = "What is the latest information on USFS's data catalog work?"

    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])

    response = query_llm(question)
    md = Markdown(response)
    panel = Panel(
        md,
        title="LLM Response",
        subtitle="[italic green]Generated using LangChain[/italic green]",
        expand=False,
        border_style="blue"
    )
    console.print(panel)
    # print("LLM Response:", response, dir(response))


if __name__ == "__main__":
    main()
