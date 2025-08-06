from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional, Dict
import random
import uuid
from contextlib import asynccontextmanager

# pydantic-ai imports for the AI agents
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
    
    def check_for_blackjacks(self):
        """Check for immediate blackjacks."""
        if self.player_hand.is_blackjack():
            self.player_result = "Blackjack!"
        if self.opponent_hand.is_blackjack():
            self.opponent_result = "Blackjack!"
        
        # If the dealer has blackjack, handle that
        if self.dealer_hand.is_blackjack():
            # Compare with player
            if self.player_hand.is_blackjack():
                self.player_result = "Push with Dealer (both BJ)"
            else:
                self.player_result = "Dealer Blackjack - you lose"
            # Compare with opponent
            if self.opponent_hand.is_blackjack():
                self.opponent_result = "Push with Dealer (both BJ)"
            else:
                self.opponent_result = "Dealer Blackjack - opponent loses"
        
        # End game if anyone has blackjack
        if (self.player_hand.is_blackjack() or 
            self.opponent_hand.is_blackjack() or 
            self.dealer_hand.is_blackjack()):
            self.end_game()
            return True
        return False

    def play_dealer_turn(self):
        """Play the dealer's turn - hit until 17+."""
        while True:
            dealer_value = self.dealer_hand.best_value()
            if dealer_value < 17:
                self.deal_card(self.dealer_hand)
                if self.dealer_hand.is_bust():
                    break
            else:
                break
        
        # Compare final totals for each player not already bust
        self.finalize_results()
        self.end_game()

# ---------------------------------------------------------------------
# 3. API Response Models
# ---------------------------------------------------------------------

class CardResponse(BaseModel):
    rank: str
    suit: str
    
    @classmethod
    def from_card(cls, card: Card):
        return cls(rank=card.rank.value, suit=card.suit.value)

class HandResponse(BaseModel):
    cards: List[CardResponse]
    value: int
    is_bust: bool
    is_blackjack: bool
    
    @classmethod
    def from_hand(cls, hand: Hand):
        return cls(
            cards=[CardResponse.from_card(card) for card in hand.cards],
            value=hand.best_value(),
            is_bust=hand.is_bust(),
            is_blackjack=hand.is_blackjack()
        )

class GameStateResponse(BaseModel):
    game_id: str
    dealer_hand: HandResponse
    player_hand: HandResponse
    opponent_hand: HandResponse
    game_over: bool
    player_result: Optional[str] = None
    opponent_result: Optional[str] = None
    hide_dealer: bool

    @classmethod
    def from_state(cls, game_id: str, state: BlackjackState, hide_dealer: bool = True):
        dealer_hand = state.dealer_hand
        
        # If we should hide the dealer's second card and game isn't over,
        # create a new hand with just the first card
        if hide_dealer and not state.game_over:
            visible_dealer_hand = Hand(cards=[dealer_hand.cards[0]])
        else:
            visible_dealer_hand = dealer_hand
            
        return cls(
            game_id=game_id,
            dealer_hand=HandResponse.from_hand(visible_dealer_hand),
            player_hand=HandResponse.from_hand(state.player_hand),
            opponent_hand=HandResponse.from_hand(state.opponent_hand),
            game_over=state.game_over,
            player_result=state.player_result,
            opponent_result=state.opponent_result,
            hide_dealer=hide_dealer and not state.game_over
        )

class ActionRequest(BaseModel):
    action: Action

class AdviceResponse(BaseModel):
    advice: Action

# ---------------------------------------------------------------------
# 4. Game State Management
# ---------------------------------------------------------------------

# In-memory storage for game states
games: Dict[str, BlackjackState] = {}

# ---------------------------------------------------------------------
# 5. AI Agent Setup
# ---------------------------------------------------------------------
#################### API KEY HERE ###########
model = GeminiModel(
    'gemini-2.0-flash', 
    provider=GoogleGLAProvider(api_key='')
)

dealer_advisor_agent = Agent(
    model,
    deps_type=BlackjackState,
    result_type=Action,
    system_prompt=(
        "You are a blackjack dealer giving advice to the player. "
        "Provide the best move (hit/stand/double) following basic strategy. "
        "Use the player's hand and the dealer's visible card to decide."
    )
)

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

@dealer_advisor_agent.tool
async def get_advice_state(ctx: RunContext[BlackjackState]) -> str:
    """Return the game state for context (the player's hand + dealer up-card)."""
    # Create a state representation string for the AI
    dealer_show = f"{ctx.deps.dealer_hand.cards[0]}"
    player_cards = " ".join(str(card) for card in ctx.deps.player_hand.cards)
    player_value = ctx.deps.player_hand.best_value()
    
    return f"Dealer shows: {dealer_show}\nYour hand: {player_cards} ({player_value})"

@opponent_agent.tool
async def get_opponent_state(ctx: RunContext[BlackjackState]) -> str:
    """Return the game state from the perspective of the opponent."""
    dealer_show = f"{ctx.deps.dealer_hand.cards[0]}"
    opponent_cards = " ".join(str(card) for card in ctx.deps.opponent_hand.cards)
    opponent_value = ctx.deps.opponent_hand.best_value()
    
    return f"Dealer shows: {dealer_show}\nYour hand: {opponent_cards} ({opponent_value})"

# ---------------------------------------------------------------------
# 6. FastAPI Setup
# ---------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialization code here
    yield
    # Cleanup code here

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# ---------------------------------------------------------------------
# 7. API Endpoints
# ---------------------------------------------------------------------

@app.post("/games/", response_model=GameStateResponse)
async def create_game():
    """Create a new blackjack game."""
    game_id = str(uuid.uuid4())
    game = BlackjackState()
    game.initialize_deck(num_decks=1)
    game.deal_initial_cards()
    
    # Check for blackjacks
    game.check_for_blackjacks()
    
    games[game_id] = game
    return GameStateResponse.from_state(game_id, game)

@app.get("/games/{game_id}", response_model=GameStateResponse)
async def get_game(game_id: str):
    """Get the current state of a game."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    return GameStateResponse.from_state(game_id, games[game_id])

@app.post("/games/{game_id}/player/action", response_model=GameStateResponse)
async def player_action(game_id: str, action_request: ActionRequest):
    """Player takes an action (hit, stand, double)."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    
    if game.game_over:
        raise HTTPException(status_code=400, detail="Game is already over")
    
    if game.player_result:
        raise HTTPException(status_code=400, detail="Player's turn is already over")
    
    action = action_request.action
    
    if action == Action.HIT:
        game.deal_card(game.player_hand)
        if game.player_hand.is_bust():
            game.player_result = "Bust! Dealer wins."
    
    elif action == Action.STAND:
        # Player stands, no action needed
        pass
    
    elif action == Action.DOUBLE:
        game.deal_card(game.player_hand)
        if game.player_hand.is_bust():
            game.player_result = "Bust after double! Dealer wins."
    
    # Check if player's turn is over
    player_done = (action == Action.STAND or 
                   action == Action.DOUBLE or 
                   game.player_hand.is_bust())
    
    # If player's turn is over, play opponent's turn (AI)
    if player_done:
        # Use the AI opponent to decide moves
        while not game.opponent_hand.is_bust() and not game.opponent_result:
            # Ask the AI agent for a move
            opponent_response = opponent_agent.run_sync("What's your move?", deps=game)
            opponent_move = opponent_response.data
            
            if opponent_move == Action.HIT:
                game.deal_card(game.opponent_hand)
                if game.opponent_hand.is_bust():
                    game.opponent_result = "Bust! Dealer wins."
                    break
            
            elif opponent_move == Action.STAND:
                # Opponent stands, turn is over
                break
            
            elif opponent_move == Action.DOUBLE:
                game.deal_card(game.opponent_hand)
                if game.opponent_hand.is_bust():
                    game.opponent_result = "Bust after double! Dealer wins."
                break  # Doubling ends the turn
        
        # After both players are done, play dealer's turn
        game.play_dealer_turn()
    
    return GameStateResponse.from_state(game_id, game)

@app.post("/games/{game_id}/dealer-advice", response_model=AdviceResponse)
async def get_dealer_advice(game_id: str):
    """Get dealer's advice for the player's next move using the AI agent."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found")
    
    game = games[game_id]
    
    if game.game_over:
        raise HTTPException(status_code=400, detail="Game is already over")
    
    # Use the AI agent to get advice
    advice = dealer_advisor_agent.run_sync("What should the player do?", deps=game)
    return AdviceResponse(advice=advice.data)

# ---------------------------------------------------------------------
# 8. Run the application
# ---------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("blackjack_api:app", host="0.0.0.0", port=8000, reload=True)