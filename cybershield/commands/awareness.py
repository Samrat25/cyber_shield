"""Cyber awareness training CLI commands."""

import click
from rich.console import Console
from cybershield.awareness.quiz import run_quiz

console = Console()


@click.group()
def awareness():
    """Cybersecurity awareness training and quiz commands."""
    pass


@awareness.command()
@click.option('--questions', '-n', type=int, help='Number of questions (default: all)')
@click.option('--difficulty', '-d', type=click.Choice(['easy', 'medium', 'hard']), 
              help='Filter by difficulty level')
def quiz(questions: int, difficulty: str):
    """
    Start an interactive cybersecurity awareness quiz.
    
    Test your knowledge about phishing, passwords, malware, social engineering,
    and other cybersecurity topics. Get instant feedback and explanations.
    """
    run_quiz(num_questions=questions, difficulty=difficulty)


@awareness.command()
def topics():
    """List all quiz topics and categories."""
    console.print("\n[bold cyan]📚 Quiz Topics & Categories[/bold cyan]\n")
    
    topics_info = {
        "Phishing": "Learn to identify fake emails, suspicious URLs, and social engineering attacks",
        "Password Security": "Best practices for creating and managing strong passwords",
        "Malware & Ransomware": "Understand different types of malicious software and how to avoid them",
        "Social Engineering": "Recognize manipulation tactics used by attackers",
        "Network Security": "Safe practices for using public Wi-Fi, VPNs, and network connections",
        "Data Protection": "Two-factor authentication, encryption, and protecting sensitive information",
        "Incident Response": "What to do when you suspect a security breach",
        "Advanced Threats": "Zero-day vulnerabilities, APTs, and sophisticated attack vectors",
        "Security Principles": "Fundamental concepts like least privilege and defense in depth"
    }
    
    for topic, description in topics_info.items():
        console.print(f"[bold yellow]• {topic}[/bold yellow]")
        console.print(f"  [dim]{description}[/dim]\n")
    
    console.print("[dim]Start the quiz: cybershield awareness quiz[/dim]")


@awareness.command()
def tips():
    """Display quick cybersecurity tips."""
    console.print("\n[bold cyan]🛡️  Quick Cybersecurity Tips[/bold cyan]\n")
    
    tips_list = [
        ("🔒 Use Strong Passwords", "12+ characters with mixed case, numbers, and symbols. Use a password manager."),
        ("🔐 Enable 2FA", "Add two-factor authentication to all important accounts."),
        ("🎣 Watch for Phishing", "Verify sender addresses, hover over links, and never share passwords."),
        ("🔄 Keep Software Updated", "Install security updates promptly to patch vulnerabilities."),
        ("📱 Secure Your Devices", "Use screen locks, encryption, and remote wipe capabilities."),
        ("🌐 Use HTTPS", "Look for the padlock icon and 'https://' in URLs."),
        ("📧 Think Before You Click", "Don't open suspicious attachments or click unknown links."),
        ("💾 Backup Regularly", "Keep backups of important data in multiple locations."),
        ("🚫 Limit Personal Info", "Be cautious about what you share on social media."),
        ("🔍 Monitor Your Accounts", "Regularly check for unauthorized access or suspicious activity."),
    ]
    
    for title, description in tips_list:
        console.print(f"[bold green]{title}[/bold green]")
        console.print(f"  {description}\n")


@awareness.command()
def scenarios():
    """Show real-world security scenarios and how to handle them."""
    console.print("\n[bold cyan]🎭 Real-World Security Scenarios[/bold cyan]\n")
    
    scenarios_list = [
        {
            "title": "Suspicious Email",
            "scenario": "You receive an email from 'IT Support' asking you to verify your account by clicking a link.",
            "red_flags": ["Unexpected request", "Urgency tactics", "Suspicious sender address", "Generic greeting"],
            "action": "Don't click! Verify with IT through official channels. Report the email as phishing."
        },
        {
            "title": "Public Wi-Fi",
            "scenario": "You're at a coffee shop and need to check your bank account.",
            "red_flags": ["Unencrypted network", "Unknown network owner", "Sensitive transaction"],
            "action": "Use mobile data or a VPN. Avoid sensitive transactions on public Wi-Fi."
        },
        {
            "title": "USB Drive Found",
            "scenario": "You find a USB drive labeled 'Confidential - Q4 Salaries' in the parking lot.",
            "red_flags": ["Unknown device", "Tempting label", "Could contain malware"],
            "action": "Don't plug it in! Turn it in to security. It could be a social engineering attack."
        },
        {
            "title": "Urgent Phone Call",
            "scenario": "Someone calls claiming to be from Microsoft, saying your computer has a virus.",
            "red_flags": ["Unsolicited call", "Urgency", "Requests remote access", "Asks for payment"],
            "action": "Hang up immediately. Microsoft doesn't make unsolicited calls. It's a scam."
        }
    ]
    
    for i, scenario in enumerate(scenarios_list, 1):
        console.print(f"[bold yellow]Scenario {i}: {scenario['title']}[/bold yellow]")
        console.print(f"\n[white]{scenario['scenario']}[/white]\n")
        console.print("[bold red]🚩 Red Flags:[/bold red]")
        for flag in scenario['red_flags']:
            console.print(f"  • {flag}")
        console.print(f"\n[bold green]✅ Correct Action:[/bold green]")
        console.print(f"  {scenario['action']}\n")
        console.print("─" * 70 + "\n")
