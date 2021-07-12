import math


NUM_CARDS = 6

TOYS = ['공', '버스', '꽃', '강아지', '고양이', '신발', 
        '숟가락', '물고기', '자전거', '곰돌이', '아기', '가방']

NUM_TOYS = len(TOYS)

# number of times parent should say the target word before a new card appears
TARGET_WORD_GOAL = 4

# maximum number of seconds a card is displayed before it is replaced by a
# new card
MAX_CARD_SHOWN_TIME = 60


class Toy:
    def __init__(self, name):
        self.name = name
        self.weight = 1 / NUM_TOYS
        self.phrases = [
            Phrase('{}_{}'.format(name, i), self) for i in range(1, 7)
        ]

    def __lt__(self, other):
        return self.weight < other.weight


class Phrase:
    def __init__(self, phrase, toy, target_word=None, highlight=None):
        self.phrase = phrase
        self.toy = toy
        self.target_word = target_word
        self.highlight = highlight

        self.spoken_count = 0
        self.time_displayed = 0  # seconds

    def weight(self):
        '''Ordering function'''
        return (
                math.floor(self.spoken_count / TARGET_WORD_GOAL) + 
                math.floor(self.time_displayed / MAX_CARD_SHOWN_TIME)
        )


    def __lt__(self, other):
        return self.weight() < other.weight() 


class Context:
    def __init__(self, on_context_update_callback):
        self.toys = [Toy(name) for name in TOYS]
        self.on_context_update = on_context_update_callback


    def on_visual_attention_1(self, toy_name, alpha=0.005):
        ALPHA = alpha

        for toy in self.toys:
            if toy.name == toy_name:
                toy.weight = toy.weight + ALPHA
            toy.weight /= (1 + ALPHA)  # normalize

        self.toys = sorted(self.toys, reverse=True)
        self.on_context_update()


    def on_visual_attention_2(self, toy_name, alpha=0.005):
        ''' Version used in pilots. Approximately equal to the above.
        '''
        ALPHA = alpha

        for toy in self.toys:
            if toy.name == toy_name:
                toy.weight = (1 - ALPHA) * toy.weight + ALPHA
            else:
                toy.weight = (1 - ALPHA) * toy.weight

        self.toys = sorted(self.toys, reverse=True)
        self.on_context_update()

    
    def on_visual_attention_3(self, toy_name, alpha=0.02):
        ''' Linear increase and decrease.
        '''
        ALPHA = alpha
        EPSILON = 0.005  # prevent division by 0
        delta_w = 0
        w_attended = 0

        for toy in self.toys:
            if toy.name == toy_name:
                delta_w = min(1 - toy.weight - EPSILON, ALPHA)
                w_attended = toy.weight
                toy.weight += delta_w
                break

        for toy in self.toys:
            if toy.name != toy_name:
                toy.weight -= delta_w * toy.weight / (1 - w_attended)

        self.toys = sorted(self.toys, reverse=True)
        self.on_context_update()


    def on_spoken_attention(self, attended_toy, beta):
        ''' Use same function as visual attention but with different weight.
        '''
        BETA = beta
        ### ... ### 
        self.on_context_update()


class State:
    ''' The state holds
            (1) the joint attention distribution (context)
            (2) the currently displayed cards
    '''
    def __init__(self):
        self.context = Context(lambda: self.on_context_update())
        self.shown_cards = []  # list of phrases
        self.calculate_cards()

    
    def on_context_update(self):
        '''Callback'''
        self.calculate_cards()


    def calculate_cards(self):
        '''Calculates which cards to display.'''
        new_cards = []
        for toy in self.context.toys:
            toy.phrases = sorted(toy.phrases)
            how_many = math.ceil(toy.weight * NUM_CARDS)
            new_cards.extend(toy.phrases[:how_many])
            if len(new_cards) >= NUM_CARDS:
                break

        new_cards = new_cards[:NUM_CARDS]  # truncate
        self.shown_cards = new_cards

    
    def on_time_step_increment(self):
        '''Same update policy as target_word_spoken for all the words
        that are currently displayed?
        '''
        self.time += 1
        for phrase in self.shown_cards:
            phrase.time_displayed += 1
        self.calculate_cards()


    def on_target_word_spoken(self, target_word):
        for phrase in self.shown_cards:
            # if phrase.target_word == 'target_word':
            if phrase.phrase == target_word:  # for simulation
                phrase.spoken_count += 1
        self.calculate_cards()


    def print_cards(self):
        print('----------------')
        for phrase in self.shown_cards:
            print(phrase.phrase)
        print('----------------')
        for toy in self.context.toys:
            print(f'{toy.name:5}: weight = {toy.weight:.3f}  | ', end='')
            print(', '.join([x.phrase for x in toy.phrases]))
        print('weight sum: {}'.format(
                sum([x.weight for x in self.context.toys])))
