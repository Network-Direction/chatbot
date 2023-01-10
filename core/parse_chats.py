
"""
Parses messages sent to the chat bot, so it can respond

Usage:
    import this module into the application

Authentication:
    None

Restrictions:
    None

To Do:
    None

Author:
    Luke Robertson - January 2023
"""


from config import GLOBAL
from core import teamschat
import random

jokes = [
    "I went to buy some camo pants but couldn't find any.",
    "I want to die peacefully in my sleep, like my grandfather… Not screaming \
        and yelling like the passengers in his car.",
    "It takes a lot of balls to golf the way I do.",
    "My father has schizophrenia, but he's good people.",
    "The easiest time to add insult to injury is when you're signing \
        someone's cast.",
    "Two fish are in a tank. One says, 'How do you drive this thing?'",
    "The problem isn't that obesity runs in your family. It's that no one \
        runs in your family.",
    "I got a new pair of gloves today, but they're both 'lefts,' which on the \
        one hand is great, but on the other, it's just not right.",
    "Two wifi engineers got married. The reception was fantastic.",
    "A dung beetle walks into a bar and asks, 'Is this stool taken?'",
    "I buy all my guns from a guy called T-Rex. He's a small arms dealer.",
    "A Freudian slip is when you say one thing and mean your mother.",
    "How do you get a country girl's attention? A tractor.",
    "What do you call a pudgy psychic? A four-chin teller.",
    "My wife asked me to stop singing “Wonderwall” to her. I said maybe...",
    "Dogs can't operate MRI machines. But catscan.",
    "What kind of music do chiropractors like? Hip pop.",
    "I signed up for a marathon, but how will I know if it's the real deal \
        or just a run through?",
    "When life gives you melons, you might be dyslexic.",
    "I spent a lot of time, money, and effort childproofing my house… \
        But the kids still get in.",
    "The man who survived both mustard gas and pepper spray is a \
        seasoned veteran now.",
    "Dark jokes are like food. Not everyone gets it"
]


# Take a given chat message, and decide what to do with it
def parse(message, sender):
    message = message.replace("<p>", "").replace("</p>", "").lower()

    # Confirm it's not the chatbot itself generating the message
    if sender != GLOBAL['chatbot_name']:
        if 'hi' in message:
            teamschat.send_chat("hi")
        elif 'tell me a joke' in message:
            teamschat.send_chat(random.choice(jokes))
        elif 'siri' or 'alexa' in message:
            teamschat.send_chat("She's way out of my league")
        else:
            print(f"{sender} says {message}")
