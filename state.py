import math


NUM_CARDS = 6

TOYS = ['공', '버스', '꽃', '강아지', '고양이', '신발', 
        '숟가락', '물고기', '자전거', '곰돌이', '아기', '가방']

NUM_TOYS = len(TOYS)


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


class Context:
    def __init__(self):
        self.toys = [Toy(name) for name in TOYS]


    def on_visual_attention(self, toy_name, alpha=0.005):
        ALPHA = alpha

        for toy in self.toys:
            if toy.name == toy_name:
                toy.weight = toy.weight + ALPHA
            toy.weight /= (1 + ALPHA)  # normalize

        self.toys = sorted(self.toys, reverse=True)


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

    
    def on_visual_attention_3(self, toy_name, alpha=0.02):
        ''' Linear increase and decrease.
        '''
        ALPHA = alpha
        delta_w = 0
        w_attended = 0
        EPSILON = 0.005  # prevent division by 0

        for toy in self.toys:
            if toy.name == toy_name:
                delta_w = min(1-toy.weight-EPSILON, ALPHA)
                w_attended = toy.weight
                toy.weight += delta_w
                break

        for toy in self.toys:
            if toy.name != toy_name:
                toy.weight -= delta_w * toy.weight / (1 - w_attended)

        self.toys = sorted(self.toys, reverse=True)


    def on_spoken_attention(self, attended_toy):
        BETA = 0.2
        for toy in self.toys:
            if toy.name == attended_toy:
                toy.weight += BETA
            else:
                toy.weight -= BETA
        self.toys = sorted(self.toys, reverse=True)


class State:
    ''' The state is a function of
            (1) the joint attention distribution (context)
            (2) the spoken target words
            (3) time
    '''
    def __init__(self):
        self.context = Context()
        self.time = 0

    
    def on_time_step_increment(self):
        self.time += 1


    def on_target_word_spoken(self, target_word):
        pass


    def context_to_guidance(self):
        cards = []
        for toy in self.context.toys:
            how_many = math.ceil(toy.weight * NUM_CARDS)
            cards.extend(toy.phrases[:how_many])
            if len(cards) >= NUM_CARDS:
                break

        cards = cards[:NUM_CARDS]  # truncate

        print('----------------')
        for phrase in cards:
            print(phrase.phrase)
        print('----------------')
        for toy in self.context.toys:
            print(f'{toy.name:5}: weight = {toy.weight:.3f}  | ', end='')
            print(', '.join([x.phrase for x in toy.phrases]))
        print('weight sum: {}'.format(
                sum([x.weight for x in self.context.toys])))


