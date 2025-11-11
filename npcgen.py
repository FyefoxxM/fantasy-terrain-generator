#!/usr/bin/env python3
"""
NPC Generator - Generate D&D NPCs with personality, occupation, and secrets
Part of the 30 for 30 challenge - Day 8
"""

import json
import random
import argparse
import sys
from pathlib import Path
from typing import Optional, List, Dict

# Try to import Day 7's name generator
try:
    from namegen import NameGenerator
except ImportError:
    print("Warning: namegen.py not found. Install Day 7's name generator for full functionality.")
    NameGenerator = None


class NPC:
    """Represents a generated NPC with all attributes."""
    
    def __init__(
        self,
        name: str,
        race: str,
        age: str,
        occupation: str,
        personality: List[str],
        secret: Optional[str] = None,
        hook: Optional[str] = None
    ):
        self.name = name
        self.race = race
        self.age = age
        self.occupation = occupation
        self.personality = personality
        self.secret = secret
        self.hook = hook
    
    def to_dict(self) -> Dict:
        """Convert NPC to dictionary for JSON export."""
        return {
            "name": self.name,
            "race": self.race,
            "age": self.age,
            "occupation": self.occupation,
            "personality": self.personality,
            "secret": self.secret,
            "hook": self.hook
        }
    
    def to_markdown(self) -> str:
        """Format NPC as markdown."""
        lines = [
            f"## {self.name}",
            f"**Race:** {self.race.capitalize()}",
            f"**Age:** {self.age}",
            f"**Occupation:** {self.occupation}",
            f"**Personality:** {', '.join(self.personality)}",
        ]
        
        if self.secret:
            lines.append(f"**Secret:** {self.secret}")
        
        if self.hook:
            lines.append(f"**Quest Hook:** {self.hook}")
        
        return "\n".join(lines)
    
    def __str__(self) -> str:
        """Pretty print for terminal display."""
        output = [
            f"╔═══════════════════════════════════════════════════════════════",
            f"║ {self.name} ({self.race.capitalize()}, {self.age})",
            f"╠═══════════════════════════════════════════════════════════════",
            f"║ Occupation: {self.occupation}",
            f"║ Personality: {', '.join(self.personality)}",
        ]
        
        if self.secret:
            output.append(f"║ ")
            output.append(f"║ SECRET: {self.secret}")
        
        if self.hook:
            output.append(f"║ ")
            output.append(f"║ QUEST HOOK: {self.hook}")
        
        output.append(f"╚═══════════════════════════════════════════════════════════════")
        
        return "\n".join(output)


class NPCGenerator:
    """Generate random NPCs with personality, occupation, and optional secrets/hooks."""
    
    # Trait conflicts - traits that shouldn't appear together
    TRAIT_CONFLICTS = {
        'cowardly': ['recklessly brave', 'fearless'],
        'recklessly brave': ['cowardly'],
        'fearless': ['cowardly'],
        'generous': ['greedy', 'frugal'],
        'greedy': ['generous'],
        'frugal': ['generous', 'extravagant'],
        'extravagant': ['frugal'],
        'honest to a fault': ['pathological liar', 'two-faced'],
        'pathological liar': ['honest to a fault'],
        'two-faced': ['honest to a fault'],
        'naive': ['suspicious', 'paranoid', 'calculating'],
        'suspicious': ['naive'],
        'paranoid': ['naive'],
        'calculating': ['naive', 'impulsive'],
        'impulsive': ['calculating', 'meticulous'],
        'meticulous': ['impulsive', 'chaotically messy'],
        'humble': ['arrogant', 'pompous', 'vain', 'boastful'],
        'arrogant': ['humble'],
        'pompous': ['humble'],
        'vain': ['humble'],
        'boastful': ['humble'],
        'lazy': ['industrious'],
        'industrious': ['lazy'],
        'forgiving': ['vengeful'],
        'vengeful': ['forgiving'],
        'open-minded': ['xenophobic', 'judgmental'],
        'xenophobic': ['open-minded', 'welcoming of strangers'],
        'welcoming of strangers': ['xenophobic'],
        'judgmental': ['open-minded'],
    }
    
    AGE_RANGES = [
        "young adult (18-25)",
        "adult (26-35)",
        "middle-aged (36-50)",
        "mature (51-65)",
        "elderly (66+)"
    ]
    
    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize generator and load data files."""
        if data_dir is None:
            data_dir = Path(__file__).parent
        
        self.data_dir = Path(data_dir)
        
        # Load all data files
        self.traits = self._load_json('npc_traits.json')
        self.occupations = self._load_json('npc_occupations.json')
        self.secrets = self._load_json('npc_secrets.json')
        self.hooks = self._load_json('npc_hooks.json')
        
        # Initialize name generator if available
        if NameGenerator:
            try:
                self.name_gen = NameGenerator()
            except FileNotFoundError:
                print("Warning: name_data.json not found. Using fallback name generation.")
                self.name_gen = None
        else:
            self.name_gen = None
    
    def _load_json(self, filename: str) -> any:
        """Load a JSON data file."""
        filepath = self.data_dir / filename
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: {filename} not found in {self.data_dir}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error parsing {filename}: {e}")
            sys.exit(1)
    
    def generate(
        self,
        race: Optional[str] = None,
        occupation_tier: Optional[str] = None,
        include_secret: bool = True,
        include_hook: bool = False,
        seed: Optional[int] = None
    ) -> NPC:
        """Generate a random NPC."""
        if seed is not None:
            random.seed(seed)
        
        # Generate name
        if race is None:
            race = random.choice(['human', 'elf', 'dwarf', 'orc'])
        
        if self.name_gen:
            name = self.name_gen.generate_name(race=race, seed=seed)
        else:
            # Fallback if namegen not available
            name = f"{race.capitalize()}-{random.randint(1000, 9999)}"
        
        # Pick age
        age = random.choice(self.AGE_RANGES)
        
        # Pick occupation based on tier
        occupation = self._pick_occupation(occupation_tier)
        
        # Pick 2-3 personality traits (no conflicts)
        personality = self._pick_traits()
        
        # Maybe add secret (50% chance)
        secret = None
        if include_secret and random.random() < 0.5:
            secret = random.choice(self.secrets)
        
        # Maybe add quest hook
        hook = None
        if include_hook:
            hook = random.choice(self.hooks)
        
        return NPC(
            name=name,
            race=race,
            age=age,
            occupation=occupation,
            personality=personality,
            secret=secret,
            hook=hook
        )
    
    def _pick_occupation(self, tier: Optional[str] = None) -> str:
        """Pick an occupation, optionally from a specific tier."""
        if tier:
            if tier not in self.occupations:
                print(f"Warning: Unknown tier '{tier}', using random")
                tier = None
        
        if tier:
            return random.choice(self.occupations[tier])
        else:
            # Weight by tier probability: 50% common, 30% uncommon, 20% rare
            roll = random.random()
            if roll < 0.5:
                tier = 'common'
            elif roll < 0.8:
                tier = 'uncommon'
            else:
                tier = 'rare'
            return random.choice(self.occupations[tier])
    
    def _pick_traits(self, count: int = None) -> List[str]:
        """Pick 2-3 personality traits that don't conflict."""
        if count is None:
            count = random.randint(2, 3)
        
        selected = []
        attempts = 0
        max_attempts = 50
        
        while len(selected) < count and attempts < max_attempts:
            trait = random.choice(self.traits)
            
            # Check if it conflicts with already selected traits
            if self._has_conflict(trait, selected):
                attempts += 1
                continue
            
            selected.append(trait)
            attempts = 0  # Reset on success
        
        return selected
    
    def _has_conflict(self, trait: str, existing: List[str]) -> bool:
        """Check if a trait conflicts with any existing traits."""
        if trait in existing:
            return True
        
        conflicts = self.TRAIT_CONFLICTS.get(trait, [])
        return any(existing_trait in conflicts for existing_trait in existing)
    
    def generate_batch(
        self,
        count: int,
        race: Optional[str] = None,
        occupation_tier: Optional[str] = None,
        include_secret: bool = True,
        include_hook: bool = False
    ) -> List[NPC]:
        """Generate multiple NPCs."""
        return [
            self.generate(
                race=race,
                occupation_tier=occupation_tier,
                include_secret=include_secret,
                include_hook=include_hook
            )
            for _ in range(count)
        ]


def main():
    """CLI interface for NPC generator."""
    parser = argparse.ArgumentParser(
        description='Generate D&D NPCs with personality, occupation, and secrets',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                        # Generate 1 random NPC
  %(prog)s human                  # Generate 1 human NPC
  %(prog)s -n 5                   # Generate 5 random NPCs
  %(prog)s elf --tier rare        # Generate 1 elf with rare occupation
  %(prog)s --with-hooks           # Include quest hooks
  %(prog)s -n 3 --export json     # Export 3 NPCs as JSON
  %(prog)s --seed 42              # Use seed for reproducibility
        """
    )
    
    parser.add_argument(
        'race',
        nargs='?',
        choices=['human', 'elf', 'dwarf', 'orc'],
        help='NPC race (random if not specified)'
    )
    
    parser.add_argument(
        '-n', '--count',
        type=int,
        default=1,
        help='Number of NPCs to generate (default: 1)'
    )
    
    parser.add_argument(
        '--tier',
        choices=['common', 'uncommon', 'rare'],
        help='Occupation tier (random if not specified)'
    )
    
    parser.add_argument(
        '--with-hooks',
        action='store_true',
        help='Include quest hooks'
    )
    
    parser.add_argument(
        '--no-secrets',
        action='store_true',
        help='Disable secrets (enabled by default)'
    )
    
    parser.add_argument(
        '--export',
        choices=['json', 'markdown'],
        help='Export format (default: pretty print to terminal)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file (default: stdout)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        help='Random seed for reproducibility'
    )
    
    parser.add_argument(
        '--data-dir',
        type=Path,
        help='Directory containing JSON data files (default: script directory)'
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = NPCGenerator(data_dir=args.data_dir)
    
    # Generate NPCs
    if args.count == 1:
        npcs = [generator.generate(
            race=args.race,
            occupation_tier=args.tier,
            include_secret=not args.no_secrets,
            include_hook=args.with_hooks,
            seed=args.seed
        )]
    else:
        npcs = generator.generate_batch(
            count=args.count,
            race=args.race,
            occupation_tier=args.tier,
            include_secret=not args.no_secrets,
            include_hook=args.with_hooks
        )
    
    # Format output
    if args.export == 'json':
        output = json.dumps([npc.to_dict() for npc in npcs], indent=2)
    elif args.export == 'markdown':
        output = "\n\n".join(npc.to_markdown() for npc in npcs)
    else:
        output = "\n\n".join(str(npc) for npc in npcs)
    
    # Write output
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Generated {len(npcs)} NPC(s) -> {args.output}")
    else:
        print(output)


if __name__ == '__main__':
    main()
