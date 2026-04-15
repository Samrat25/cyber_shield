"""
Cyber Awareness Quiz Module
Interactive quiz to educate users about cybersecurity threats and best practices.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box
import random
import json
from datetime import datetime

console = Console()


@dataclass
class QuizQuestion:
    """Represents a single quiz question."""
    question: str
    options: List[str]
    correct_answer: int  # Index of correct option (0-based)
    explanation: str
    category: str
    difficulty: str  # "easy", "medium", "hard"


class AwarenessQuiz:
    """Interactive cybersecurity awareness quiz."""
    
    def __init__(self):
        self.questions = self._load_questions()
        self.score = 0
        self.total_questions = 0
        self.results = []
    
    def _load_questions(self) -> List[QuizQuestion]:
        """Load quiz questions database."""
        return [
            # Phishing Questions
            QuizQuestion(
                question="You receive an email from 'paypa1-security@verify-account.com' asking you to verify your account. What should you do?",
                options=[
                    "Click the link and verify immediately",
                    "Reply with your account details",
                    "Delete the email - it's a phishing attempt",
                    "Forward it to friends to warn them"
                ],
                correct_answer=2,
                explanation="This is a classic phishing attempt. Notice the '1' instead of 'l' in 'paypa1' and the suspicious domain. Always verify sender addresses and never click suspicious links.",
                category="Phishing",
                difficulty="easy"
            ),
            QuizQuestion(
                question="Which of these URLs is most likely a phishing site?",
                options=[
                    "https://www.amazon.com/account",
                    "http://amaz0n-secure-login.xyz/verify",
                    "https://signin.amazon.com",
                    "https://www.amazon.co.uk/login"
                ],
                correct_answer=1,
                explanation="The second URL uses HTTP (not HTTPS), has a '0' instead of 'o', uses a suspicious TLD (.xyz), and includes 'verify' - all red flags for phishing.",
                category="Phishing",
                difficulty="medium"
            ),
            
            # Password Security
            QuizQuestion(
                question="What makes a password strong?",
                options=[
                    "Using your birthday and name",
                    "At least 12 characters with mixed case, numbers, and symbols",
                    "A common word with a number at the end",
                    "The same password for all accounts"
                ],
                correct_answer=1,
                explanation="Strong passwords should be long (12+ characters), use a mix of uppercase, lowercase, numbers, and symbols, and be unique for each account.",
                category="Password Security",
                difficulty="easy"
            ),
            QuizQuestion(
                question="How often should you change your passwords?",
                options=[
                    "Never, if they're strong enough",
                    "Every 30 days for all accounts",
                    "When there's a security breach or suspicious activity",
                    "Once a year on your birthday"
                ],
                correct_answer=2,
                explanation="Modern security advice suggests changing passwords only when necessary (breach, suspicious activity) rather than on a schedule, which can lead to weaker passwords.",
                category="Password Security",
                difficulty="medium"
            ),
            
            # Malware & Ransomware
            QuizQuestion(
                question="Your computer suddenly displays a message saying all files are encrypted and demands Bitcoin payment. What is this?",
                options=[
                    "A system update notification",
                    "Ransomware attack",
                    "Antivirus warning",
                    "Normal Windows behavior"
                ],
                correct_answer=1,
                explanation="This is a ransomware attack. Never pay the ransom. Disconnect from network immediately, report to IT/authorities, and restore from backups if available.",
                category="Malware",
                difficulty="easy"
            ),
            QuizQuestion(
                question="What should you do before opening an email attachment from an unknown sender?",
                options=[
                    "Open it to see what it is",
                    "Scan it with antivirus software first",
                    "Don't open it at all - delete the email",
                    "Forward it to IT to check"
                ],
                correct_answer=2,
                explanation="Never open attachments from unknown senders. Even antivirus can miss new threats. Delete suspicious emails or report them to your IT department.",
                category="Malware",
                difficulty="medium"
            ),
            
            # Social Engineering
            QuizQuestion(
                question="Someone calls claiming to be from IT support and asks for your password to 'fix an issue'. What do you do?",
                options=[
                    "Give them the password to get help",
                    "Refuse and hang up - legitimate IT never asks for passwords",
                    "Give them a fake password to test them",
                    "Ask them to email you instead"
                ],
                correct_answer=1,
                explanation="This is social engineering. Legitimate IT staff will NEVER ask for your password. Hang up and contact IT through official channels to verify.",
                category="Social Engineering",
                difficulty="easy"
            ),
            QuizQuestion(
                question="You find a USB drive in the parking lot. What should you do?",
                options=[
                    "Plug it into your work computer to find the owner",
                    "Take it home and check it on your personal computer",
                    "Turn it in to security without plugging it in",
                    "Throw it away"
                ],
                correct_answer=2,
                explanation="Unknown USB drives can contain malware that auto-executes when plugged in. Never plug unknown devices into your computer. Report to security.",
                category="Social Engineering",
                difficulty="medium"
            ),
            
            # Network Security
            QuizQuestion(
                question="Is it safe to use public Wi-Fi at a coffee shop for online banking?",
                options=[
                    "Yes, if the website uses HTTPS",
                    "Yes, if you trust the coffee shop",
                    "No, public Wi-Fi is not secure for sensitive transactions",
                    "Yes, if you use incognito mode"
                ],
                correct_answer=2,
                explanation="Public Wi-Fi is not secure. Attackers can intercept data even on HTTPS sites. Use a VPN or mobile data for sensitive transactions.",
                category="Network Security",
                difficulty="medium"
            ),
            QuizQuestion(
                question="What is a VPN used for?",
                options=[
                    "Making your internet faster",
                    "Encrypting your internet connection for privacy",
                    "Blocking all websites",
                    "Downloading files faster"
                ],
                correct_answer=1,
                explanation="A VPN (Virtual Private Network) encrypts your internet connection, protecting your data from interception and masking your IP address.",
                category="Network Security",
                difficulty="easy"
            ),
            
            # Data Protection
            QuizQuestion(
                question="What is two-factor authentication (2FA)?",
                options=[
                    "Using two different passwords",
                    "Logging in from two devices",
                    "Requiring password + second verification (code, biometric, etc.)",
                    "Having two user accounts"
                ],
                correct_answer=2,
                explanation="2FA adds a second layer of security beyond passwords, typically a code sent to your phone or generated by an app, making accounts much harder to hack.",
                category="Data Protection",
                difficulty="easy"
            ),
            QuizQuestion(
                question="After a data breach is announced, what should you do first?",
                options=[
                    "Wait to see if you're affected",
                    "Change passwords for that service and enable 2FA",
                    "Delete your account",
                    "Do nothing if you have a strong password"
                ],
                correct_answer=1,
                explanation="Immediately change your password and enable 2FA. Also change passwords on any other accounts where you used the same password.",
                category="Data Protection",
                difficulty="medium"
            ),
            
            # Advanced Scenarios
            QuizQuestion(
                question="You notice unusual activity on your account (logins from unknown locations). What's the FIRST thing you should do?",
                options=[
                    "Post about it on social media",
                    "Change your password immediately",
                    "Wait to see if it happens again",
                    "Email customer support"
                ],
                correct_answer=1,
                explanation="Change your password immediately to lock out the attacker. Then enable 2FA, check for unauthorized changes, and contact support.",
                category="Incident Response",
                difficulty="medium"
            ),
            QuizQuestion(
                question="What is 'zero-day' vulnerability?",
                options=[
                    "A bug that takes zero days to fix",
                    "A security flaw unknown to the software vendor",
                    "A vulnerability that expires in zero days",
                    "A bug that causes zero damage"
                ],
                correct_answer=1,
                explanation="A zero-day vulnerability is a security flaw that's unknown to the vendor, meaning there's zero days of protection. These are highly valuable to attackers.",
                category="Advanced Threats",
                difficulty="hard"
            ),
            QuizQuestion(
                question="What is the principle of 'least privilege' in cybersecurity?",
                options=[
                    "Everyone should have minimal computer access",
                    "Users should only have the minimum access needed for their job",
                    "Passwords should be as short as possible",
                    "Only privileged users need security training"
                ],
                correct_answer=1,
                explanation="Least privilege means giving users only the access they need to do their job, reducing the potential damage from compromised accounts.",
                category="Security Principles",
                difficulty="hard"
            ),
        ]
    
    def start_quiz(self, num_questions: Optional[int] = None, difficulty: Optional[str] = None):
        """
        Start the interactive quiz.
        
        Args:
            num_questions: Number of questions to ask (None = all)
            difficulty: Filter by difficulty ("easy", "medium", "hard", None = all)
        """
        console.clear()
        
        # Display welcome banner
        console.print(Panel.fit(
            "[bold cyan]🛡️  CyberShield Awareness Quiz  🛡️[/bold cyan]\n\n"
            "[white]Test your cybersecurity knowledge and learn how to protect yourself online![/white]",
            border_style="cyan",
            box=box.DOUBLE
        ))
        console.print()
        
        # Filter questions
        questions = self.questions
        if difficulty:
            questions = [q for q in questions if q.difficulty == difficulty]
        
        # Select random subset if specified
        if num_questions and num_questions < len(questions):
            questions = random.sample(questions, num_questions)
        else:
            random.shuffle(questions)
        
        self.total_questions = len(questions)
        
        # Ask each question
        for i, question in enumerate(questions, 1):
            self._ask_question(i, question)
            console.print()
        
        # Show final results
        self._show_results()
    
    def _ask_question(self, number: int, question: QuizQuestion):
        """Ask a single question and record the answer."""
        # Display question
        console.print(f"[bold yellow]Question {number}/{self.total_questions}[/bold yellow] "
                     f"[dim]({question.category} - {question.difficulty})[/dim]")
        console.print()
        console.print(f"[bold white]{question.question}[/bold white]")
        console.print()
        
        # Display options
        for i, option in enumerate(question.options, 1):
            console.print(f"  [cyan]{i}.[/cyan] {option}")
        console.print()
        
        # Get user answer
        while True:
            try:
                answer = Prompt.ask(
                    "[bold]Your answer[/bold]",
                    choices=[str(i) for i in range(1, len(question.options) + 1)]
                )
                answer_idx = int(answer) - 1
                break
            except (ValueError, KeyboardInterrupt):
                console.print("[red]Invalid input. Please enter a number.[/red]")
        
        # Check answer
        is_correct = answer_idx == question.correct_answer
        
        if is_correct:
            self.score += 1
            console.print("[bold green]✓ Correct![/bold green]")
        else:
            console.print(f"[bold red]✗ Incorrect.[/bold red] The correct answer was: "
                         f"[yellow]{question.options[question.correct_answer]}[/yellow]")
        
        # Show explanation
        console.print()
        console.print(Panel(
            f"[italic]{question.explanation}[/italic]",
            title="[bold]Explanation[/bold]",
            border_style="blue"
        ))
        
        # Record result
        self.results.append({
            "question": question.question,
            "category": question.category,
            "difficulty": question.difficulty,
            "correct": is_correct,
            "user_answer": question.options[answer_idx],
            "correct_answer": question.options[question.correct_answer]
        })
        
        # Pause before next question
        if number < self.total_questions:
            Confirm.ask("\n[dim]Press Enter for next question[/dim]", default=True)
            console.clear()
    
    def _show_results(self):
        """Display final quiz results and certificate."""
        console.clear()
        
        percentage = (self.score / self.total_questions * 100) if self.total_questions > 0 else 0
        
        # Determine performance level
        if percentage >= 90:
            level = "EXPERT"
            emoji = "🏆"
            color = "bold green"
        elif percentage >= 75:
            level = "ADVANCED"
            emoji = "⭐"
            color = "bold cyan"
        elif percentage >= 60:
            level = "INTERMEDIATE"
            emoji = "👍"
            color = "bold yellow"
        else:
            level = "BEGINNER"
            emoji = "📚"
            color = "bold white"
        
        # Display results banner
        console.print(Panel.fit(
            f"[{color}]{emoji}  Quiz Complete!  {emoji}[/{color}]\n\n"
            f"[white]Score: [bold]{self.score}/{self.total_questions}[/bold] ({percentage:.1f}%)[/white]\n"
            f"[white]Level: [{color}]{level}[/{color}][/white]",
            border_style="green",
            box=box.DOUBLE
        ))
        console.print()
        
        # Category breakdown
        categories = {}
        for result in self.results:
            cat = result["category"]
            if cat not in categories:
                categories[cat] = {"correct": 0, "total": 0}
            categories[cat]["total"] += 1
            if result["correct"]:
                categories[cat]["correct"] += 1
        
        # Display category performance
        table = Table(title="Performance by Category", box=box.ROUNDED)
        table.add_column("Category", style="cyan")
        table.add_column("Score", justify="center")
        table.add_column("Percentage", justify="center")
        
        for cat, stats in categories.items():
            cat_pct = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
            color = "green" if cat_pct >= 75 else "yellow" if cat_pct >= 50 else "red"
            table.add_row(
                cat,
                f"{stats['correct']}/{stats['total']}",
                f"[{color}]{cat_pct:.0f}%[/{color}]"
            )
        
        console.print(table)
        console.print()
        
        # Recommendations
        console.print("[bold]Recommendations:[/bold]")
        if percentage >= 90:
            console.print("🎉 Excellent work! You have strong cybersecurity awareness.")
        elif percentage >= 75:
            console.print("👏 Great job! Review the questions you missed to reach expert level.")
        elif percentage >= 60:
            console.print("📖 Good start! Study the explanations and retake the quiz to improve.")
        else:
            console.print("📚 Keep learning! Cybersecurity awareness is crucial. Review the material and try again.")
        
        console.print()
        
        # Save results
        if Confirm.ask("[bold]Save results to file?[/bold]", default=True):
            self._save_results(percentage, level)
    
    def _save_results(self, percentage: float, level: str):
        """Save quiz results to a JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"quiz_results_{timestamp}.json"
        
        data = {
            "timestamp": datetime.now().isoformat(),
            "score": self.score,
            "total_questions": self.total_questions,
            "percentage": percentage,
            "level": level,
            "results": self.results
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            console.print(f"[green]✓ Results saved to {filename}[/green]")
        except Exception as e:
            console.print(f"[red]✗ Error saving results: {e}[/red]")


def run_quiz(num_questions: Optional[int] = None, difficulty: Optional[str] = None):
    """
    Convenience function to run the quiz.
    
    Args:
        num_questions: Number of questions (None = all)
        difficulty: Filter by difficulty ("easy", "medium", "hard", None = all)
    """
    quiz = AwarenessQuiz()
    quiz.start_quiz(num_questions, difficulty)
