#!/usr/bin/env python3

import random
import time
import os

# ANSI color codes for terminal output
COLORS = {
    'RED': '\033[91m',
    'BLUE': '\033[94m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RESET': '\033[0m'
}

class Card:
    def _init_(self, color, value):
        self.color = color
        self.value = value

    def _str_(self):
        if self.color == "WILD":
            return f"{self.value}"
        return f"{COLORS[self.color]}{self.color} {self.value}{COLORS['RESET']}"

    def matches(self, other):
        # Wild cards match anything
        if self.color == "WILD" or other.color == "WILD":
            return True
        # Match by color or value
        return self.color == other.color or self.value == other.value


class Deck:
    def _init_(self):
        self.cards = []
        self.discard_pile = []
        self.create_deck()
        self.shuffle()

    def create_deck(self):
        colors = ["RED", "BLUE", "GREEN", "YELLOW"]
        values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "SKIP", "REVERSE", "DRAW 2"]

        # Add number cards and action cards
        for color in colors:
            # One 0 card per color
            self.cards.append(Card(color, "0"))
            # Two of each 1-9 and action cards per color
            for _ in range(2):
                for value in values[1:]:
                    self.cards.append(Card(color, value))

        # Add wild cards
        for _ in range(4):
            self.cards.append(Card("WILD", "WILD"))
            self.cards.append(Card("WILD", "WILD DRAW 4"))

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if not self.cards:
            # If deck is empty, shuffle discard pile and use as new deck
            if not self.discard_pile:
                return None  # Game is over if both are empty
            print("Reshuffling discard pile into deck...")
            self.cards = self.discard_pile[:-1]  # Keep the top card in discard pile
            self.discard_pile = [self.discard_pile[-1]]
            self.shuffle()

        return self.cards.pop()

    def add_to_discard(self, card):
        self.discard_pile.append(card)

    def top_card(self):
        if not self.discard_pile:
            return None
        return self.discard_pile[-1]


class Player:
    def _init_(self, name):
        self.name = name
        self.hand = []
        self.said_uno = False

    def draw(self, deck, count=1):
        for _ in range(count):
            card = deck.draw()
            if card:
                self.hand.append(card)
                if len(self.hand) > 1:
                    self.said_uno = False

    def play_card(self, card_index):
        return self.hand.pop(card_index)

    def has_valid_move(self, top_card):
        return any(card.matches(top_card) for card in self.hand)

    def say_uno(self):
        self.said_uno = True
        print(f"{self.name} says UNO!")


class HumanPlayer(Player):
    def take_turn(self, game):
        print(f"\n{self.name}'s turn")
        print(f"Top card: {game.deck.top_card()}")
        print("Your hand:")

        for i, card in enumerate(self.hand):
            print(f"{i+1}. {card}")

        top_card = game.deck.top_card()

        if not self.has_valid_move(top_card):
            print("No valid moves. Drawing a card...")
            self.draw(game.deck)
            print(f"Drew: {self.hand[-1]}")

            # Check if the drawn card can be played
            if self.hand[-1].matches(top_card):
                print(f"Playing the drawn card: {self.hand[-1]}")
                card = self.play_card(len(self.hand) - 1)
                game.deck.add_to_discard(card)

                # Handle special cards
                if len(self.hand) == 1 and not self.said_uno:
                    self.say_uno()

                return self.process_card_action(card, game)
            return True

        while True:
            try:
                choice = input("Choose a card to play (number) or 'd' to draw: ")

                if choice.lower() == 'd':
                    self.draw(game.deck)
                    print(f"Drew: {self.hand[-1]}")

                    # Check if the drawn card can be played
                    if self.hand[-1].matches(top_card):
                        play_drawn = input("Play the drawn card? (y/n): ")
                        if play_drawn.lower() == 'y':
                            card = self.play_card(len(self.hand) - 1)
                            game.deck.add_to_discard(card)

                            # Handle special cards
                            if len(self.hand) == 1 and not self.said_uno:
                                say_uno = input("Say UNO? (y/n): ")
                                if say_uno.lower() == 'y':
                                    self.say_uno()

                            return self.process_card_action(card, game)
                    return True

                index = int(choice) - 1
                if 0 <= index < len(self.hand):
                    card = self.hand[index]
                    if card.matches(top_card):
                        card = self.play_card(index)

                        # Handle wild cards
                        if card.color == "WILD":
                            while True:
                                color_choice = input("Choose a color (RED, BLUE, GREEN, YELLOW): ").upper()
                                if color_choice in ["RED", "BLUE", "GREEN", "YELLOW"]:
                                    card.color = color_choice
                                    break
                                print("Invalid color choice.")

                        game.deck.add_to_discard(card)

                        # Handle UNO declaration
                        if len(self.hand) == 1 and not self.said_uno:
                            say_uno = input("Say UNO? (y/n): ")
                            if say_uno.lower() == 'y':
                                self.say_uno()

                        return self.process_card_action(card, game)
                    else:
                        print("Invalid move. Card must match color or value.")
                else:
                    print("Invalid card index.")
            except ValueError:
                print("Please enter a valid number or 'd'.")

    def process_card_action(self, card, game):
        if card.value == "SKIP":
            print(f"{game.current_player.name}'s turn is skipped!")
            return False
        elif card.value == "REVERSE":
            print("Direction reversed! (No effect in 2-player game)")
            return False
        elif card.value == "DRAW 2":
            next_player = game.get_next_player()
            print(f"{next_player.name} draws 2 cards!")
            next_player.draw(game.deck, 2)
            return False
        elif card.value == "WILD DRAW 4":
            next_player = game.get_next_player()
            print(f"{next_player.name} draws 4 cards!")
            next_player.draw(game.deck, 4)
            return False
        return True


class AIPlayer(Player):
    def take_turn(self, game):
        print(f"\n{self.name}'s turn")
        print(f"Top card: {game.deck.top_card()}")
        print(f"{self.name} has {len(self.hand)} cards")

        time.sleep(1)  # Add a small delay to make the game feel more natural

        top_card = game.deck.top_card()
        playable_cards = [i for i, card in enumerate(self.hand) if card.matches(top_card)]

        if not playable_cards:
            print(f"{self.name} has no valid moves. Drawing a card...")
            self.draw(game.deck)

            # Check if the drawn card can be played
            if self.hand[-1].matches(top_card):
                card = self.play_card(len(self.hand) - 1)
                print(f"{self.name} plays: {card}")
                game.deck.add_to_discard(card)

                # Handle special cards
                if len(self.hand) == 1:
                    self.say_uno()

                return self.process_card_action(card, game)
            else:
                print(f"{self.name} drew a card and cannot play it")
            return True

        # AI strategy: prioritize action cards and cards that match the current color
        # First, try to play action cards
        action_cards = [i for i in playable_cards if self.hand[i].value in ["SKIP", "REVERSE", "DRAW 2"]]

        # Then, try to play cards matching the current color
        color_match = [i for i in playable_cards if self.hand[i].color == top_card.color]

        # Then, try to play number cards
        number_cards = [i for i in playable_cards if self.hand[i].value not in ["SKIP", "REVERSE", "DRAW 2", "WILD", "WILD DRAW 4"]]

        # Finally, use wild cards only when necessary
        wild_cards = [i for i in playable_cards if self.hand[i].color == "WILD"]

        # Choose the best card to play
        if action_cards:
            card_index = random.choice(action_cards)
        elif color_match:
            card_index = random.choice(color_match)
        elif number_cards:
            card_index = random.choice(number_cards)
        elif wild_cards:
            card_index = random.choice(wild_cards)
        else:
            card_index = random.choice(playable_cards)

        card = self.play_card(card_index)

        # Handle wild cards
        if card.color == "WILD":
            # Choose the most common color in hand
            colors = [c.color for c in self.hand if c.color != "WILD"]
            if colors:
                most_common = max(set(colors), key=colors.count)
                card.color = most_common
            else:
                card.color = random.choice(["RED", "BLUE", "GREEN", "YELLOW"])
            print(f"{self.name} plays: {card} and changes color to {card.color}")
        else:
            print(f"{self.name} plays: {card}")

        game.deck.add_to_discard(card)

        # Handle UNO declaration
        if len(self.hand) == 1:
            self.say_uno()

        return self.process_card_action(card, game)

    def process_card_action(self, card, game):
        if card.value == "SKIP":
            print(f"{game.current_player.name}'s turn is skipped!")
            return False
        elif card.value == "REVERSE":
            print("Direction reversed! (No effect in 2-player game)")
            return False
        elif card.value == "DRAW 2":
            next_player = game.get_next_player()
            print(f"{next_player.name} draws 2 cards!")
            next_player.draw(game.deck, 2)
            return False
        elif card.value == "WILD DRAW 4":
            next_player = game.get_next_player()
            print(f"{next_player.name} draws 4 cards!")
            next_player.draw(game.deck, 4)
            return False
        return True


class UnoGame:
    def _init_(self):
        self.deck = Deck()
        self.players = [HumanPlayer("Player"), AIPlayer("AI")]
        self.current_player_index = 0
        self.direction = 1  # 1 for clockwise, -1 for counter-clockwise

    def setup(self):
        # Deal 7 cards to each player
        for player in self.players:
            player.draw(self.deck, 7)

        # Place first card on discard pile
        initial_card = self.deck.draw()

        # If the first card is a wild card, assign it a random color
        if initial_card.color == "WILD":
            initial_card.color = random.choice(["RED", "BLUE", "GREEN", "YELLOW"])

        self.deck.add_to_discard(initial_card)

    @property
    def current_player(self):
        return self.players[self.current_player_index]

    def get_next_player(self):
        next_index = (self.current_player_index + self.direction) % len(self.players)
        return self.players[next_index]

    def next_turn(self):
        self.current_player_index = (self.current_player_index + self.direction) % len(self.players)

    def play(self):
        self.setup()

        print("\nWelcome to UNO!")
        print("Match cards by color or number.")
        print("Special cards: SKIP, REVERSE, DRAW 2, WILD, WILD DRAW 4")
        print("First player to get rid of all cards wins!\n")

        while True:
            # Clear screen for better readability
            os.system('clear' if os.name == 'posix' else 'cls')

            print(f"\nTop card: {self.deck.top_card()}")

            # Check if game is over
            for player in self.players:
                if not player.hand:
                    print(f"\n{player.name} wins!")
                    return

            # Current player takes turn
            next_turn = self.current_player.take_turn(self)

            # Check if the player has won after their turn
            if not self.current_player.hand:
                print(f"\n{self.current_player.name} wins!")
                return

            # Check if the player forgot to say UNO
            if len(self.current_player.hand) == 1 and not self.current_player.said_uno:
                # In a real game, other players would call them out
                if isinstance(self.current_player, HumanPlayer):
                    print("You forgot to say UNO! Drawing 2 penalty cards.")
                    self.current_player.draw(self.deck, 2)

            # Move to next player if the turn wasn't skipped
            if next_turn:
                self.next_turn()

            input("\nPress Enter to continue...")


if _name_ == "_main_":
    game = UnoGame()
    game.play()
