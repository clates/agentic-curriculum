import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys

# Ensure we can import from src
sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import (
    render_alphabet_to_image,
    render_alphabet_to_pdf,
)


def generate_disney_alphabet():
    output_dir = "disney_alphabet_series"
    os.makedirs(output_dir, exist_ok=True)

    alphabet_data = [
        {
            "letter": "A",
            "title": "Disney Alphabet: Letter A",
            "instructions": "Practice writing the letter A with Alice!",
            "starting_words": ["ANT", "AXE", "ARM", "ASH"],
            "containing_words": ["CAT", "BAG", "HAT", "CAP"],
            "character_image_path": "assets/disney_api/alice.jpg",
        },
        {
            "letter": "B",
            "title": "Disney Alphabet: Letter B",
            "instructions": "Practice writing the letter B with Bolt!",
            "starting_words": ["BAT", "BED", "BIG", "BOX"],
            "containing_words": ["ROB", "SUB", "TUB", "CAB"],
            "character_image_path": "assets/disney_api/bolt.jpg",
        },
        {
            "letter": "C",
            "title": "Disney Alphabet: Letter C",
            "instructions": "Practice writing the letter C with Chip!",
            "starting_words": ["CAT", "CAP", "CUP", "CAN"],
            "containing_words": ["ACT", "FACT", "TACT", "DUCT"],
            "character_image_path": "assets/disney_api/chip.png",
        },
        {
            "letter": "D",
            "title": "Disney Alphabet: Letter D",
            "instructions": "Practice writing the letter D with Mushu the Dragon!",
            "starting_words": ["DOG", "DUG", "DOT", "DAD"],
            "containing_words": ["RED", "BED", "MAD", "SAD"],
            "character_image_path": "assets/disney_api/mushu.jpg",
        },
        {
            "letter": "E",
            "title": "Disney Alphabet: Letter E",
            "instructions": "Practice writing the letter E with EVE!",
            "starting_words": ["EGG", "ELK", "EEL", "END"],
            "containing_words": ["BED", "NET", "TEN", "PEN"],
            "character_image_path": "assets/disney_api/eve.png",
        },
        {
            "letter": "F",
            "title": "Disney Alphabet: Letter F",
            "instructions": "Practice writing the letter F with Prince Naveen!",
            "starting_words": ["FAN", "FIN", "FOG", "FOX"],
            "containing_words": ["OFF", "BUFF", "IFF", "PUFF"],
            "character_image_path": "assets/disney_api/naveen.jpg",
        },
        {
            "letter": "G",
            "title": "Disney Alphabet: Letter G",
            "instructions": "Practice writing the letter G with Gaston!",
            "starting_words": ["GUM", "GAS", "GOT", "GET"],
            "containing_words": ["DOG", "LOG", "BIG", "BAG"],
            "character_image_path": "assets/disney_api/gaston.jpg",
        },
        {
            "letter": "H",
            "title": "Disney Alphabet: Letter H",
            "instructions": "Practice writing the letter H with Heihei!",
            "starting_words": ["HEN", "HAM", "HAT", "HUG"],
            "containing_words": ["SHIP", "FISH", "BASH", "DASH"],
            "character_image_path": "assets/disney_api/heihei.jpg",
        },
        {
            "letter": "I",
            "title": "Disney Alphabet: Letter I",
            "instructions": "Practice writing the letter I with Iago!",
            "starting_words": ["INK", "ILL", "IN", "IF"],
            "containing_words": ["PIG", "BIG", "WIG", "TIN"],
            "character_image_path": "assets/disney_api/iago.jpg",
        },
        {
            "letter": "J",
            "title": "Disney Alphabet: Letter J",
            "instructions": "Practice writing the letter J with Jasmine!",
            "starting_words": ["JAM", "JET", "JIG", "JOG"],
            "containing_words": ["OBJECT", "ENJOY", "ADJUST", "INJURE"],
            "character_image_path": "assets/disney_api/jasmine.jpg",
        },
        {
            "letter": "K",
            "title": "Disney Alphabet: Letter K",
            "instructions": "Practice writing the letter K with Kuzco!",
            "starting_words": ["KID", "KIT", "KIN", "KEG"],
            "containing_words": ["BACK", "SKIN", "SINK", "BANK"],
            "character_image_path": "assets/disney_api/kuzco.jpg",
        },
        {
            "letter": "L",
            "title": "Disney Alphabet: Letter L",
            "instructions": "Practice writing the letter L with Simba the Lion!",
            "starting_words": ["LOG", "LIP", "LID", "LEG"],
            "containing_words": ["PAL", "NIL", "GAL", "SAL"],
            "character_image_path": "assets/disney_api/simba.jpg",
        },
        {
            "letter": "M",
            "title": "Disney Alphabet: Letter M",
            "instructions": "Practice writing the letter M with Moana!",
            "starting_words": ["MAP", "MUD", "MOM", "MAT"],
            "containing_words": ["SWIM", "PALM", "HAM", "CLAM"],
            "character_image_path": "assets/disney_api/moana.png",
        },
        {
            "letter": "N",
            "title": "Disney Alphabet: Letter N",
            "instructions": "Practice writing the letter N with Nemo!",
            "starting_words": ["NET", "NUT", "NAP", "NIP"],
            "containing_words": ["SUN", "RUN", "PAN", "CAN"],
            "character_image_path": "assets/disney_api/nemo.jpg",
        },
        {
            "letter": "O",
            "title": "Disney Alphabet: Letter O",
            "instructions": "Practice writing the letter O with Olaf!",
            "starting_words": ["ON", "OFF", "OX", "ODD"],
            "containing_words": ["DOG", "LOG", "BOX", "POT"],
            "character_image_path": "assets/disney_api/olaf.jpg",
        },
        {
            "letter": "P",
            "title": "Disney Alphabet: Letter P",
            "instructions": "Practice writing the letter P with Pua!",
            "starting_words": ["PIG", "POT", "PAN", "PEN"],
            "containing_words": ["MAP", "SHIP", "STOP", "TRAP"],
            "character_image_path": "assets/disney_api/pua.jpg",
        },
        {
            "letter": "Q",
            "title": "Disney Alphabet: Letter Q",
            "instructions": "Practice writing the letter Q with the Queen of Hearts!",
            "starting_words": ["QUIT", "QUIZ", "QUIP", "QUID"],
            "containing_words": ["LIQUID", "EQUIP", "SQUID", "AQUA"],
            "character_image_path": "assets/disney_api/queen_of_hearts.jpg",
        },
        {
            "letter": "R",
            "title": "Disney Alphabet: Letter R",
            "instructions": "Practice writing the letter R with Rex!",
            "starting_words": ["RAT", "RED", "RUN", "RIG"],
            "containing_words": ["CAR", "FAR", "BAR", "JAR"],
            "character_image_path": "assets/disney_api/rex.jpg",
        },
        {
            "letter": "S",
            "title": "Disney Alphabet: Letter S",
            "instructions": "Practice writing the letter S with Sven!",
            "starting_words": ["SUN", "SIT", "SAD", "SIP"],
            "containing_words": ["BUS", "GAS", "HAS", "YES"],
            "character_image_path": "assets/disney_api/sven.jpg",
        },
        {
            "letter": "T",
            "title": "Disney Alphabet: Letter T",
            "instructions": "Practice writing the letter T with Thumper!",
            "starting_words": ["TEN", "TOP", "TAP", "TIN"],
            "containing_words": ["CAT", "HAT", "BAT", "SAT"],
            "character_image_path": "assets/disney_api/thumper.png",
        },
        {
            "letter": "U",
            "title": "Disney Alphabet: Letter U",
            "instructions": "Practice writing the letter U with Ursula!",
            "starting_words": ["UP", "US", "UNDER", "UMPH"],
            "containing_words": ["SUN", "BUG", "CUP", "MUD"],
            "character_image_path": "assets/disney_api/ursula.jpg",
        },
        {
            "letter": "V",
            "title": "Disney Alphabet: Letter V",
            "instructions": "Practice writing the letter V with Vanellope!",
            "starting_words": ["VAN", "VET", "VAT", "VIM"],
            "containing_words": ["GIVE", "HAVE", "LOVE", "FIVE"],
            "character_image_path": "assets/disney_api/vanellope.jpg",
        },
        {
            "letter": "W",
            "title": "Disney Alphabet: Letter W",
            "instructions": "Practice writing the letter W with Wall-E!",
            "starting_words": ["WIG", "WET", "WIN", "WEB"],
            "containing_words": ["SWIM", "TWIG", "TWIN", "WOLF"],
            "character_image_path": "assets/disney_api/walle.png",
        },
        {
            "letter": "X",
            "title": "Disney Alphabet: Letter X",
            "instructions": "Practice writing the letter X with Agent X!",
            "starting_words": ["X-RAY", "XEBEC", "XENON", "XEROX"],
            "containing_words": ["BOX", "FOX", "AXE", "TAX"],
            "character_image_path": "assets/disney_api/agent_x.png",
        },
        {
            "letter": "Y",
            "title": "Disney Alphabet: Letter Y",
            "instructions": "Practice writing the letter Y with Yzma!",
            "starting_words": ["YES", "YET", "YAM", "YAK"],
            "containing_words": ["BOY", "TOY", "FLY", "SKY"],
            "character_image_path": "assets/disney_api/yzma.jpg",
        },
        {
            "letter": "Z",
            "title": "Disney Alphabet: Letter Z",
            "instructions": "Practice writing the letter Z with Zazu!",
            "starting_words": ["ZIG", "ZAG", "ZOO", "ZAP"],
            "containing_words": ["BUZZ", "JAZZ", "FUZZ", "FIZZ"],
            "character_image_path": "assets/disney_api/zazu.jpg",
        },
    ]

    for data in alphabet_data:
        ws = WorksheetFactory.create("alphabet", data)
        filename = f"{data['letter']}_worksheet"
        render_alphabet_to_image(ws, f"{output_dir}/{filename}.png")
        render_alphabet_to_pdf(ws, f"{output_dir}/{filename}.pdf")

    print(f"Successfully generated Disney alphabet series in {output_dir}/")


if __name__ == "__main__":
    generate_disney_alphabet()
