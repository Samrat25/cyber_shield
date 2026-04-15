#!/usr/bin/env python3
"""
Test script for awareness quiz module.
Demonstrates quiz functionality without interactive prompts.
"""

from cybershield.awareness.quiz import AwarenessQuiz
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def test_quiz_questions():
    """Display quiz questions and categories."""
    
    console.print("\n[bold cyan]🎓 CyberShield Awareness Quiz Overview[/bold cyan]\n")
    
    quiz = AwarenessQuiz()
    
    # Category statistics
    categories = {}
    difficulties = {"easy": 0, "medium": 0, "hard": 0}
    
    for question in quiz.questions:
        cat = question.category
        if cat not in categories:
            categories[cat] = 0
        categories[cat] += 1
        difficulties[question.difficulty] += 1
    
    # Display statistics
    console.print(f"[bold]Total Questions:[/bold] {len(quiz.questions)}")
    console.print()
    
    # Category breakdown
    table = Table(title="Questions by Category", box=box.ROUNDED)
    table.add_column("Category", style="cyan")
    table.add_column("Count", justify="center", style="yellow")
    
    for cat, count in sorted(categories.items()):
        table.add_row(cat, str(count))
    
    console.print(table)
    console.print()
    
    # Difficulty breakdown
    table2 = Table(title="Questions by Difficulty", box=box.ROUNDED)
    table2.add_column("Difficulty", style="cyan")
    table2.add_column("Count", justify="center", style="yellow")
    
    for diff, count in difficulties.items():
        table2.add_row(diff.title(), str(count))
    
    console.print(table2)
    console.print()
    
    # Sample questions
    console.print("[bold cyan]Sample Questions:[/bold cyan]\n")
    
    for i, question in enumerate(quiz.questions[:3], 1):
        console.print(f"[bold yellow]Question {i}:[/bold yellow] [dim]({question.category} - {question.difficulty})[/dim]")
        console.print(f"{question.question}\n")
        
        for j, option in enumerate(question.options, 1):
            prefix = "✓" if j - 1 == question.correct_answer else " "
            style = "green" if j - 1 == question.correct_answer else "white"
            console.print(f"  [{style}]{prefix} {j}. {option}[/{style}]")
        
        console.print(f"\n[italic]Explanation: {question.explanation}[/italic]")
        console.print("\n" + "─" * 70 + "\n")
    
    # Topics covered
    console.print("[bold cyan]Topics Covered:[/bold cyan]\n")
    
    topics_info = {
        "Phishing": "Identify fake emails, suspicious URLs, and social engineering attacks",
        "Password Security": "Best practices for creating and managing strong passwords",
        "Malware & Ransomware": "Understand different types of malicious software",
        "Social Engineering": "Recognize manipulation tactics used by attackers",
        "Network Security": "Safe practices for using public Wi-Fi and VPNs",
        "Data Protection": "Two-factor authentication and protecting sensitive information",
        "Incident Response": "What to do when you suspect a security breach",
        "Advanced Threats": "Zero-day vulnerabilities and sophisticated attacks",
        "Security Principles": "Fundamental concepts like least privilege"
    }
    
    for topic, description in topics_info.items():
        if topic in categories:
            console.print(f"[bold green]✓ {topic}[/bold green] ({categories[topic]} questions)")
            console.print(f"  [dim]{description}[/dim]\n")
    
    console.print("\n[bold]To take the interactive quiz, run:[/bold]")
    console.print("  [cyan]cybershield awareness quiz[/cyan]")
    console.print("\n[bold]Or with options:[/bold]")
    console.print("  [cyan]cybershield awareness quiz --questions 10 --difficulty easy[/cyan]\n")


if __name__ == "__main__":
    test_quiz_questions()
