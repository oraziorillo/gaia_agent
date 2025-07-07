#!/usr/bin/env python3
import argparse
import contextlib
import sys
import threading
import itertools
import time
from agent import GAIAAgent

def print_custom_help():
    help_text = '''\nGaia Agent CLI Utility\n\nUsage:\n  python run.py -q "<question>" -f <file_path>\n\nOptions:\n  -q, --question   The question for the agent (required)\n  -f, --file       Path to an input file (required)\n  -h, --help       Show this help message and exit\n\nExample:\n  python run.py -q 'Summarize this' -f report.pdf\n'''
    print(help_text)

@contextlib.contextmanager
def spinner_context(verbose=False):
    """Context manager that shows a spinner if verbose mode is not enabled."""
    if verbose:
        yield
        return
    
    # Start spinner
    done = False
    
    def spin():
        frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
        for f in itertools.cycle(frames):
            if done:
                break
            sys.stdout.write(f"\r{f} Thinking…")
            sys.stdout.flush()
            time.sleep(0.1)
        sys.stdout.write("\r")  # clear line
    
    t = threading.Thread(target=spin, daemon=True)
    t.start()
    
    try:
        yield
    finally:
        # Stop spinner
        done = True
        t.join()

def main():
    parser = argparse.ArgumentParser(
        prog="Gaia Agent CLI",
        description="Send a question (+ file [optional]) to a Gaia agent",
        epilog="Example: python run.py -q 'Summarize this' -f report.pdf"
    )
    parser.add_argument("-q", "--question", required=True,
                        help="The question for the agent")
    parser.add_argument("-f", "--file", dest="file_path",
                        help="Path to an input file (read in binary)")
    parser.add_argument("-m", "--openai-model", dest="openai_model", default="gpt-4.1-mini",
                        help="OpenAI model to use (e.g., gpt-4, gpt-3.5-turbo)")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Show extra debugging info")
    args = parser.parse_args()

    if args.verbose:
        from settings import Settings, get_settings
        _settings: Settings = get_settings()
        _settings.verbose = True

    with spinner_context(verbose=args.verbose):
        agent = GAIAAgent(args.openai_model)
        response = agent(args.question, args.file_path)

    print(f"Final answer: {response}")

if __name__ == "__main__":
    main()