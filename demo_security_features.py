#!/usr/bin/env python3
"""
CyberShield Security Features Demo
Demonstrates phishing detection and awareness training integration.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from cybershield.phishing.detector import PhishingDetector
from cybershield.awareness.quiz import AwarenessQuiz

console = Console()


def show_banner():
    """Display demo banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   ██████╗██╗   ██╗██████╗ ███████╗██████╗ ███████╗██╗  ██╗  ║
║  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗██╔════╝██║  ██║  ║
║  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝███████╗███████║  ║
║  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗╚════██║██╔══██║  ║
║  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║███████║██║  ██║  ║
║   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝  ║
║                                                               ║
║           Security Features Demo - GAP 2 & 3                 ║
╚═══════════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="cyan")
    console.print()


def demo_phishing_detection():
    """Demonstrate phishing detection capabilities."""
    console.print(Panel.fit(
        "[bold cyan]🎣 Phishing Detection Demo[/bold cyan]\n\n"
        "[white]Real-time URL analysis to protect against phishing attacks[/white]",
        border_style="cyan",
        box=box.DOUBLE
    ))
    console.print()
    
    detector = PhishingDetector()
    
    # Test cases with explanations
    test_cases = [
        {
            "url": "http://paypa1-secure-login.xyz/verify-account",
            "description": "Classic phishing - typosquatting with '1' instead of 'l'"
        },
        {
            "url": "https://www.paypal.com/signin",
            "description": "Legitimate PayPal login page"
        },
        {
            "url": "http://192.168.1.1/banking-login",
            "description": "IP address with banking keywords - highly suspicious"
        },
        {
            "url": "https://accounts.google.com/signin",
            "description": "Legitimate Google sign-in"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        console.print(f"[bold yellow]Test Case {i}:[/bold yellow]")
        console.print(f"[dim]{test['description']}[/dim]")
        console.print(f"[cyan]URL:[/cyan] {test['url']}\n")
        
        result = detector.detect(test['url'])
        
        # Color based on risk
        risk_colors = {
            "HIGH": "red",
            "MEDIUM": "yellow",
            "LOW": "blue",
            "SAFE": "green"
        }
        color = risk_colors.get(result["risk_level"], "white")
        
        # Display result
        console.print(f"  [{color}]● Risk Level: {result['risk_level']}[/{color}]")
        console.print(f"  Score: {result['risk_score']}/10")
        console.print(f"  Phishing: {'⚠️ YES' if result['is_phishing'] else '✅ NO'}")
        
        if result['score_breakdown']:
            console.print(f"  Indicators: {', '.join(result['score_breakdown'].keys())}")
        
        console.print()
    
    console.print("[green]✓ Phishing detection demo completed![/green]\n")


def demo_awareness_quiz():
    """Demonstrate awareness quiz capabilities."""
    console.print(Panel.fit(
        "[bold cyan]🎓 Awareness Training Demo[/bold cyan]\n\n"
        "[white]Interactive quiz to educate users about cybersecurity[/white]",
        border_style="cyan",
        box=box.DOUBLE
    ))
    console.print()
    
    quiz = AwarenessQuiz()
    
    # Show statistics
    categories = {}
    difficulties = {"easy": 0, "medium": 0, "hard": 0}
    
    for question in quiz.questions:
        cat = question.category
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
        difficulties[question.difficulty] += 1
    
    console.print(f"[bold]Quiz Statistics:[/bold]")
    console.print(f"  Total Questions: {len(quiz.questions)}")
    console.print(f"  Categories: {len(categories)}")
    console.print(f"  Difficulties: Easy ({difficulties['easy']}), Medium ({difficulties['medium']}), Hard ({difficulties['hard']})")
    console.print()
    
    # Show sample question
    sample = quiz.questions[0]
    console.print("[bold yellow]Sample Question:[/bold yellow]")
    console.print(f"[dim]Category: {sample.category} | Difficulty: {sample.difficulty}[/dim]\n")
    console.print(f"[white]{sample.question}[/white]\n")
    
    for i, option in enumerate(sample.options, 1):
        prefix = "✓" if i - 1 == sample.correct_answer else " "
        style = "green" if i - 1 == sample.correct_answer else "white"
        console.print(f"  [{style}]{prefix} {i}. {option}[/{style}]")
    
    console.print(f"\n[italic]Explanation: {sample.explanation}[/italic]\n")
    
    # Show topics
    console.print("[bold]Topics Covered:[/bold]")
    for cat in sorted(categories.keys()):
        console.print(f"  • {cat} ({categories[cat]} questions)")
    
    console.print()
    console.print("[green]✓ Awareness quiz demo completed![/green]\n")


def show_integration_examples():
    """Show how features integrate with main system."""
    console.print(Panel.fit(
        "[bold cyan]🔗 System Integration[/bold cyan]\n\n"
        "[white]How phishing detection and awareness training integrate with CyberShield[/white]",
        border_style="cyan",
        box=box.DOUBLE
    ))
    console.print()
    
    examples = [
        {
            "title": "Blockchain Logging",
            "description": "Detected phishing URLs are logged to Aptos blockchain",
            "command": "cybershield phishing check --url <URL> --log-blockchain"
        },
        {
            "title": "P2P Network Alerts",
            "description": "Share phishing threats with other nodes in real-time",
            "command": "cybershield network broadcast-threat --type phishing --url <URL>"
        },
        {
            "title": "Dashboard Integration",
            "description": "View phishing detection stats in the web dashboard",
            "command": "cybershield dashboard"
        },
        {
            "title": "Automated Training",
            "description": "Schedule regular awareness quizzes for team members",
            "command": "cybershield awareness quiz --schedule weekly"
        },
        {
            "title": "Email Gateway",
            "description": "Integrate phishing detection into email filtering",
            "command": "cybershield phishing scan-emails --mailbox inbox"
        }
    ]
    
    for example in examples:
        console.print(f"[bold yellow]• {example['title']}[/bold yellow]")
        console.print(f"  {example['description']}")
        console.print(f"  [dim]$ {example['command']}[/dim]\n")
    
    console.print("[green]✓ Integration examples shown![/green]\n")


def show_cli_commands():
    """Display available CLI commands."""
    console.print(Panel.fit(
        "[bold cyan]📋 Available Commands[/bold cyan]\n\n"
        "[white]Quick reference for phishing detection and awareness training[/white]",
        border_style="cyan",
        box=box.DOUBLE
    ))
    console.print()
    
    # Phishing commands
    console.print("[bold yellow]Phishing Detection:[/bold yellow]")
    phishing_cmds = [
        ("check", "Check single URL for phishing", "cybershield phishing check --url <URL>"),
        ("batch", "Check multiple URLs from file", "cybershield phishing batch --file urls.txt"),
        ("examples", "Show example URLs for testing", "cybershield phishing examples"),
    ]
    
    for cmd, desc, example in phishing_cmds:
        console.print(f"  [cyan]{cmd}[/cyan] - {desc}")
        console.print(f"    [dim]{example}[/dim]")
    
    console.print()
    
    # Awareness commands
    console.print("[bold yellow]Awareness Training:[/bold yellow]")
    awareness_cmds = [
        ("quiz", "Start interactive quiz", "cybershield awareness quiz"),
        ("topics", "List all quiz topics", "cybershield awareness topics"),
        ("tips", "Show security tips", "cybershield awareness tips"),
        ("scenarios", "View real-world scenarios", "cybershield awareness scenarios"),
    ]
    
    for cmd, desc, example in awareness_cmds:
        console.print(f"  [cyan]{cmd}[/cyan] - {desc}")
        console.print(f"    [dim]{example}[/dim]")
    
    console.print()


def main():
    """Run the complete demo."""
    show_banner()
    
    console.print("[bold]This demo showcases CyberShield's security education features:[/bold]")
    console.print("  1. Phishing Detection (GAP 2)")
    console.print("  2. Awareness Training (GAP 3)")
    console.print()
    
    input("Press Enter to start the demo...")
    console.clear()
    
    # Demo 1: Phishing Detection
    demo_phishing_detection()
    input("Press Enter to continue...")
    console.clear()
    
    # Demo 2: Awareness Quiz
    demo_awareness_quiz()
    input("Press Enter to continue...")
    console.clear()
    
    # Demo 3: Integration
    show_integration_examples()
    input("Press Enter to continue...")
    console.clear()
    
    # Demo 4: CLI Commands
    show_cli_commands()
    
    console.print(Panel.fit(
        "[bold green]✓ Demo Complete![/bold green]\n\n"
        "[white]To try the features yourself:[/white]\n\n"
        "[cyan]Phishing Detection:[/cyan]\n"
        "  $ cybershield phishing check --url 'http://paypa1-login.xyz'\n\n"
        "[cyan]Awareness Quiz:[/cyan]\n"
        "  $ cybershield awareness quiz --questions 10\n\n"
        "[dim]For more information, see PHISHING_AND_AWARENESS.md[/dim]",
        border_style="green",
        box=box.DOUBLE
    ))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Demo interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n\n[red]Error: {e}[/red]")
