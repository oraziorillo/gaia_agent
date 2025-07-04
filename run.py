#!/usr/bin/env python3
import argparse, sys, threading, itertools, time
from agent import GAIAAgent

def print_custom_help():
    help_text = '''\nGaia Agent CLI Utility\n\nUsage:\n  python run.py -q "<question>" -f <file_path>\n\nOptions:\n  -q, --question   The question for the agent (required)\n  -f, --file       Path to an input file (required)\n  -h, --help       Show this help message and exit\n\nExample:\n  python run.py -q 'Summarize this' -f report.pdf\n'''
    print(help_text)

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

    if not args.verbose:
        # Start the spinner in a separate thread if the verbose flag is not set
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
        t = threading.Thread(target=spin)
        t.start()

    agent = GAIAAgent(args.openai_model)
    response = agent(args.question, args.file_path)

    if not args.verbose:
        # Wait for the spinner thread to finish if the verbose flag is not set
        done = True
        t.join()

    print(f"Agent response: {response}")

if __name__ == "__main__":
    main()