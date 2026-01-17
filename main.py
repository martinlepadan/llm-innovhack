#!/usr/bin/env python3
"""
Instagram Coach Agent - Main CLI Interface

Usage:
    python main.py                    # Start interactive chat
    python main.py --question "..."   # Ask a single question
    python main.py --demo             # Run demo questions
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent import InstagramCoachAgent


def run_demo(agent: InstagramCoachAgent):
    """Run a demo with predefined questions."""
    print("\n" + "=" * 60)
    print("🎬 RUNNING DEMO")
    print("=" * 60 + "\n")

    demo_questions = [
        "Quels sont mes 3 posts les plus performants ?",
        "Quel type de contenu (reel, photo, carousel) fonctionne le mieux ?",
        "Comment puis-je améliorer mon taux d'engagement ?",
    ]

    for i, question in enumerate(demo_questions, 1):
        print(f"\n{'=' * 60}")
        print(f"DEMO QUESTION {i}/{len(demo_questions)}")
        print(f"{'=' * 60}\n")

        agent.ask(question, verbose=True)

        if i < len(demo_questions):
            input("\nPress Enter to continue to next question...")

    print("\n✅ Demo completed!\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Instagram Coach Agent - AI-powered Instagram coaching"
    )
    parser.add_argument(
        "--question", "-q", type=str, help="Ask a single question and exit"
    )
    parser.add_argument(
        "--demo", "-d", action="store_true", help="Run demo with predefined questions"
    )
    parser.add_argument(
        "--reload", "-r", action="store_true", help="Force reload data from JSON files"
    )
    parser.add_argument(
        "--no-load",
        action="store_true",
        help="Don't auto-load data (for manual loading)",
    )
    parser.add_argument(
        "--stats", "-s", action="store_true", help="Show statistics and exit"
    )

    args = parser.parse_args()

    # Initialize agent
    try:
        agent = InstagramCoachAgent(auto_load_data=not args.no_load)

        if args.reload:
            print("\n🔄 Reloading data...")
            agent.load_data(force_reload=True)

    except Exception as e:
        print(f"\n❌ Error initializing agent: {e}")
        print("\nMake sure to:")
        print("  1. Set FEATHERLESS_API_KEY in .env file")
        print("  2. Install dependencies: pip install -r requirements.txt")
        print("  3. Check that data files exist in data/ directory\n")
        sys.exit(1)

    # Handle commands
    if args.stats:
        agent._print_stats()
        return

    if args.demo:
        run_demo(agent)
        return

    if args.question:
        agent.ask(args.question, verbose=True)
        return

    # Default: start chat
    agent.chat()


if __name__ == "__main__":
    main()
