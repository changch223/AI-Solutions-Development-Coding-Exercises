from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
import random

# pydantic-ai
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.providers.google_gla import GoogleGLAProvider

# ---------------------------------------------------------------------
# 1. Card, Hand, and Action Models
# ---------------------------------------------------------------------

class Suit(str, Enum):
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    SPADES = "♠"

class Rank(str, Enum):
    ACE = "A"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"

class Card(BaseModel):
    rank: Rank
    suit: Suit
    
    def value(self) -> List[int]:
        if self.rank == Rank.ACE:
            return [1, 11]
        elif self.rank in [Rank.TEN, Rank.JACK, Rank.QUEEN, Rank.KING]:
            return [10]
        else:
            return [int(self.rank.value)]
    
    def __str__(self) -> str:
        return f"{self.rank.value}{self.suit.value}"

class Hand(BaseModel):
    cards: List[Card] = Field(default_factory=list)
    
    def best_value(self) -> int:
        total = 0
        aces = 0
        
        for card in self.cards:
            if card.rank == Rank.ACE:
                aces += 1
            else:
                total += card.value()[0]
        
        # Add aces optimally
        for _ in range(aces):
            if total + 11 <= 21:
                total += 11
            else:
                total += 1
        
        return total
    
    def is_bust(self) -> bool:
        return self.best_value() > 21
    
    def is_blackjack(self) -> bool:
        return (len(self.cards) == 2) and (self.best_value() == 21)
    
    def __str__(self) -> str:
        return " ".join(str(card) for card in self.cards) + f" ({self.best_value()})"

class Action(str, Enum):
    HIT = "hit"
    STAND = "stand"
    DOUBLE = "double"

# ---------------------------------------------------------------------
# 2. Blackjack State (3 Hands: Player, Opponent, Dealer)
# ---------------------------------------------------------------------

class BlackjackState(BaseModel):
    player_hand: Hand = Field(default_factory=Hand)
    opponent_hand: Hand = Field(default_factory=Hand)
    dealer_hand: Hand = Field(default_factory=Hand)
    deck: List[Card] = Field(default_factory=list)
    game_over: bool = False
    
    # We'll store separate "results" for the player and the opponent
    player_result: Optional[str] = None
    opponent_result: Optional[str] = None
    
    def initialize_deck(self, num_decks: int = 1):
        """Initialize and shuffle deck(s)."""
        self.deck = []
        for _ in range(num_decks):
            for suit in Suit:
                for rank in Rank:
                    self.deck.append(Card(rank=rank, suit=suit))
        random.shuffle(self.deck)
    
    def deal_card(self, hand: Hand):
        """Deal one card to a given hand."""
        if not self.deck:
            self.initialize_deck()
        card = self.deck.pop()
        hand.cards.append(card)
        return card
    
    def deal_initial_cards(self):
        """Deal initial 2 cards to everyone."""
        self.player_hand = Hand()
        self.opponent_hand = Hand()
        self.dealer_hand = Hand()
        
        # Player
        self.deal_card(self.player_hand)
        self.deal_card(self.player_hand)
        
        # Opponent
        self.deal_card(self.opponent_hand)
        self.deal_card(self.opponent_hand)
        
        # Dealer
        self.deal_card(self.dealer_hand)
        self.deal_card(self.dealer_hand)
        
        self.game_over = False
        self.player_result = None
        self.opponent_result = None
    
    def finalize_results(self):
        """Compare each player's best_value to dealer's best_value (if not already bust)."""
        dealer_total = self.dealer_hand.best_value()
        
        # Player result if not already bust
        if not self.player_result:
            player_total = self.player_hand.best_value()
            if self.player_hand.is_bust():
                self.player_result = "Bust - Dealer wins"
            elif self.dealer_hand.is_bust():
                self.player_result = "Dealer busts - You win!"
            elif player_total > dealer_total:
                self.player_result = "You win!"
            elif player_total < dealer_total:
                self.player_result = "Dealer wins!"
            else:
                self.player_result = "Push (tie)"
        
        # Opponent result if not already bust
        if not self.opponent_result:
            opponent_total = self.opponent_hand.best_value()
            if self.opponent_hand.is_bust():
                self.opponent_result = "Bust - Dealer wins"
            elif self.dealer_hand.is_bust():
                self.opponent_result = "Dealer busts - Opponent wins!"
            elif opponent_total > dealer_total:
                self.opponent_result = "Opponent wins!"
            elif opponent_total < dealer_total:
                self.opponent_result = "Dealer wins!"
            else:
                self.opponent_result = "Push (tie)"
    
    def end_game(self):
        self.game_over = True
    
    def get_visible_state(self, hide_dealer: bool = True) -> str:
        """Return a string representation of the game state.
        
        If hide_dealer=True, the dealer's second card is hidden.
        """
        lines = []
        
        # Show the dealer's hand
        if hide_dealer and not self.game_over:
            dealer_show = f"{self.dealer_hand.cards[0]} (??)"
            lines.append(f"Dealer shows: {dealer_show}")
        else:
            lines.append(f"Dealer's hand: {self.dealer_hand}")
        
        lines.append(f"Your hand: {self.player_hand}")
        lines.append(f"Opponent's hand: {self.opponent_hand}")
        
        # If the game is over, show results
        if self.game_over:
            if self.player_result:
                lines.append(f"Your result: {self.player_result}")
            if self.opponent_result:
                lines.append(f"Opponent's result: {self.opponent_result}")
        
        return "\n".join(lines)

# ---------------------------------------------------------------------
# 3. Create Agents:
#    - Dealer Advisor Agent (just offers advice to the human player).
#    - Opponent Agent (plays a second hand automatically).
# ---------------------------------------------------------------------

model = GeminiModel(
    'gemini-2.0-flash', 
        provider=GoogleGLAProvider(api_key='')
)
    
# Dealer Advisor: This agent doesn't *play*; it just recommends a move for the user if requested.
dealer_advisor_agent = Agent(
    model,
    deps_type=BlackjackState,
    result_type=Action,   # We'll assume it returns "hit", "stand", or "double"
    system_prompt=(
        "You are a blackjack dealer giving advice to the player. "
        "Provide the best move (hit/stand/double) following basic strategy. "
        "Use the player's hand and the dealer's visible card to decide."
    )
)

# Opponent Agent: This agent *plays* the second hand (the 'opponent').
opponent_agent = Agent(
    model,
    deps_type=BlackjackState,
    result_type=Action,
    system_prompt=(
        "You are a blackjack player (the opponent), playing basic strategy. "
        "Return one of: hit, stand, or double. Decide your best move based on your hand "
        "and the dealer's visible card. You only see your own hand and the dealer's up-card. "
    )
)

# Example tool for the dealer advisor (optional)
@dealer_advisor_agent.tool
async def get_advice_state(ctx: RunContext[BlackjackState]) -> str:
    """Return the game state for context (the player's hand + dealer up-card)."""
    # We'll just show the same "visible" state
    return ctx.deps.get_visible_state(hide_dealer=True)

# Example tool for the opponent
@opponent_agent.tool
async def get_opponent_state(ctx: RunContext[BlackjackState]) -> str:
    """Return the game state from the perspective of the opponent."""
    # In reality, the opponent sees their own hand + the dealer's up-card
    return ctx.deps.get_visible_state(hide_dealer=True)

# ---------------------------------------------------------------------
# 4. Game Flow with 3 Parties
# ---------------------------------------------------------------------

def play_three_party_blackjack():
    game = BlackjackState()
    game.initialize_deck(num_decks=1)
    game.deal_initial_cards()
    
    print("=== Welcome to 3-Party Blackjack ===")
    print("(You vs. Opponent vs. Dealer)\n")
    print(game.get_visible_state(hide_dealer=True))
    
    # ------------------------------------
    # 1. Check for immediate blackjacks
    # ------------------------------------
    if game.player_hand.is_blackjack():
        game.player_result = "Blackjack!"
    if game.opponent_hand.is_blackjack():
        game.opponent_result = "Blackjack!"
    
    # If the dealer has blackjack, let's handle that too
    if game.dealer_hand.is_blackjack():
        # Compare with player
        if game.player_hand.is_blackjack():
            game.player_result = "Push with Dealer (both BJ)"
        else:
            game.player_result = "Dealer Blackjack - you lose"
        # Compare with opponent
        if game.opponent_hand.is_blackjack():
            game.opponent_result = "Push with Dealer (both BJ)"
        else:
            game.opponent_result = "Dealer Blackjack - opponent loses"
    
    # If the dealer or either player had BJ, the game might effectively be over
    # but let's check if we want to proceed if only one or two had blackjack, etc.
    # For simplicity, let's say if the dealer or either player had a natural, we stop.
    # But you could handle partial continuing logic if you prefer.
    if game.player_hand.is_blackjack() or game.opponent_hand.is_blackjack() or game.dealer_hand.is_blackjack():
        game.end_game()
        print("\n=== FINAL STATE ===")
        print(game.get_visible_state(hide_dealer=False))
        return
    
    # ------------------------------------
    # 2. User's Turn
    # ------------------------------------
    while not game.game_over:
        # Optionally ask if user wants "Dealer's Advice"
        ask_advice = input("\nWould you like advice from the dealer? (Y/N): ").strip().lower()
        if ask_advice == "y":
            advisor_resp = dealer_advisor_agent.run_sync("What should the player do?", deps=game)
            print(f"Dealer's advice: {advisor_resp.data.value}")
        
        # Now ask the user for the actual move
        move = input("Your move? [H]it, [S]tand, [D]ouble: ").strip().lower()
        if move not in ['h','s','d']:
            print("Invalid choice, try again.")
            continue
        
        if move == 'h':
            print("You choose to HIT.")
            game.deal_card(game.player_hand)
            print(game.get_visible_state(hide_dealer=True))
            if game.player_hand.is_bust():
                game.player_result = "Bust! Dealer wins."
                game.end_game()
            break  # If you want multiple hits, remove this break; but typical code checks after each hit.
        
        elif move == 's':
            print("You STAND.")
            break
        
        elif move == 'd':
            print("You DOUBLE.")
            game.deal_card(game.player_hand)
            print(game.get_visible_state(hide_dealer=True))
            if game.player_hand.is_bust():
                game.player_result = "Bust after double! Dealer wins."
                game.end_game()
            else:
                print("You stand after doubling.")
            break  # Doubling ends your turn
    
    # If user would like to keep hitting multiple times, you can loop until they choose stand. 
    # For simplicity, let's just do one action for demonstration.
    
    # ------------------------------------
    # 3. Opponent's Turn (AI agent)
    # ------------------------------------
    if not game.game_over:
        print("\nOpponent's turn...")
        while True:
            if game.opponent_hand.is_bust():
                # Opponent bust is recognized automatically, but let's handle it here:
                game.opponent_result = "Bust!"
                break
            
            # Ask the agent for a move:
            opponent_response = opponent_agent.run_sync("What's your move?", deps=game)
            opponent_move = opponent_response.data
            print(f"Opponent agent chooses: {opponent_move}")
            
            if opponent_move == Action.HIT:
                game.deal_card(game.opponent_hand)
                print(game.get_visible_state(hide_dealer=True))
                
                if game.opponent_hand.is_bust():
                    game.opponent_result = "Bust! Dealer wins."
                    break
                
                # If you want the opponent to keep hitting, continue the loop
                # or break if you only want one hit. We'll let them continue hitting until they stand or bust.
            
            elif opponent_move == Action.STAND:
                print("Opponent stands.")
                break
            
            elif opponent_move == Action.DOUBLE:
                print("Opponent doubles.")
                game.deal_card(game.opponent_hand)
                print(game.get_visible_state(hide_dealer=True))
                if game.opponent_hand.is_bust():
                    game.opponent_result = "Bust after double!"
                else:
                    print("Opponent stands after doubling.")
                break  # Doubling ends their turn
    
    # ------------------------------------
    # 4. Dealer's Turn (standard rule: hit until 17+)
    # ------------------------------------
    if not game.game_over:
        # If either hand is bust, that player's result is done, 
        # but we still let the other side continue or see the dealer's final.
        
        # Dealer hits until 17 or bust
        print("\nDealer's turn...")
        while True:
            dealer_value = game.dealer_hand.best_value()
            if dealer_value < 17:
                print("Dealer hits.")
                game.deal_card(game.dealer_hand)
                print(game.get_visible_state(hide_dealer=False))
                if game.dealer_hand.is_bust():
                    print("Dealer busts!")
                    break
            else:
                print("Dealer stands.")
                break
        
        # Compare final totals for each player not already bust
        game.finalize_results()
        game.end_game()
    
    # ------------------------------------
    # 5. Final Results
    # ------------------------------------
    print("\n=== FINAL STATE ===")
    print(game.get_visible_state(hide_dealer=False))
    print("Game Over!")

# ---------------------------------------------------------------------
# 5. Run it
# ---------------------------------------------------------------------
if __name__ == "__main__":
    play_three_party_blackjack()
