import os

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys

# Ensure we can import from src
sys.path.insert(0, os.path.abspath("src"))

from worksheets.factory import WorksheetFactory
from worksheet_renderer import (
    render_reading_worksheet_to_image,
    render_reading_worksheet_to_pdf,
    render_feature_matrix_to_image,
    render_feature_matrix_to_pdf,
    render_venn_diagram_to_image,
    render_venn_diagram_to_pdf,
    render_odd_one_out_to_image,
    render_odd_one_out_to_pdf,
    render_tree_map_to_image,
    render_tree_map_to_pdf,
)


def generate_motion_week_series():
    output_dir = "motion_week_series"
    os.makedirs(output_dir, exist_ok=True)

    # =========================================================================
    # MONDAY — Types of Motion (Baseball Theme)
    # Experiment: Motion station with toy cars, ramp, spinning tops.
    # SOL: Science 1.2
    # =========================================================================

    # Monday Reading: Baseball & Types of Motion
    mon_reading_data = {
        "title": "Monday: Types of Motion",
        "passage_title": "Play Ball! Motion on the Baseball Field",
        "passage": (
            "Have you ever watched a baseball game? Baseball is full of different kinds of motion! "
            "When a pitcher throws the ball, it moves in a straight line through the air toward the batter. "
            "That is called straight-line motion. A push from the pitcher's arm sends the ball flying forward. "
            "When the batter swings and hits the ball, the bat gives the ball a big push that changes its direction!\n\n"
            "Not all motion in baseball goes in a straight line. When a fielder spins around to throw the ball "
            "to first base, that is circular, or spinning, motion. A baseball can even curve through the air "
            "when a pitcher throws a special 'curveball.' Gravity is always pulling the ball down toward the ground, "
            "which is why outfielders have to judge where a high fly ball will land. "
            "Every push, pull, and force on the field makes the ball move in a different way!"
        ),
        "instructions": "Read about motion in baseball. Then answer the questions below.",
        "questions": [
            {
                "prompt": "What kind of motion does a baseball make when the pitcher throws it in a straight line?",
                "response_lines": 2,
            },
            {
                "prompt": "What force is always pulling the baseball down toward the ground?",
                "response_lines": 2,
            },
            {
                "prompt": "Name two different types of motion you can see during a baseball game.",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {
                "term": "Straight-Line Motion",
                "definition": "Movement that goes in one direction without turning.",
            },
            {
                "term": "Circular Motion",
                "definition": "Movement that goes around in a circle or curve.",
            },
            {
                "term": "Gravity",
                "definition": "A pull that brings objects down toward the ground.",
            },
        ],
    }
    ws_mon_read = WorksheetFactory.create("reading_comprehension", mon_reading_data)
    render_reading_worksheet_to_image(ws_mon_read, f"{output_dir}/01_monday_reading.png")
    render_reading_worksheet_to_pdf(ws_mon_read, f"{output_dir}/01_monday_reading.pdf")

    # Monday Feature Matrix: Types of Motion Classification
    mon_matrix_data = {
        "title": "Monday: Types of Motion — Baseball Edition",
        "instructions": (
            "Check the box to show which type of motion each baseball action uses. "
            "Some actions may have more than one!"
        ),
        "items": [
            {
                "name": "Pitcher throws the ball",
                "checked_properties": ["Straight-Line", "Push"],
            },
            {
                "name": "Batter swings the bat",
                "checked_properties": ["Circular / Spinning", "Push"],
            },
            {
                "name": "Ball rolls along the ground",
                "checked_properties": ["Straight-Line"],
            },
            {
                "name": "Fielder spins to throw",
                "checked_properties": ["Circular / Spinning", "Push"],
            },
            {
                "name": "Gravity pulls the fly ball down",
                "checked_properties": ["Straight-Line", "Pull"],
            },
            {
                "name": "Ball curves in the air",
                "checked_properties": ["Circular / Spinning"],
            },
        ],
        "properties": ["Straight-Line", "Circular / Spinning", "Push", "Pull"],
        "show_answers": False,
    }
    ws_mon_matrix = WorksheetFactory.create("feature_matrix", mon_matrix_data)
    render_feature_matrix_to_image(ws_mon_matrix, f"{output_dir}/02_monday_feature_matrix.png")
    render_feature_matrix_to_pdf(ws_mon_matrix, f"{output_dir}/02_monday_feature_matrix.pdf")

    # =========================================================================
    # TUESDAY — Back-and-Forth Motion (Pendulum)
    # Experiment: Simple pendulum with a washer/clay on string.
    # SOL: Science 1.2
    # =========================================================================

    # Tuesday Reading: Back-and-Forth Motion
    tue_reading_data = {
        "title": "Tuesday: Back-and-Forth Motion",
        "passage_title": "Swing, Swing, Swing! The Pendulum",
        "passage": (
            "Have you ever sat on a playground swing? When you swing back and forth, "
            "you are showing a special kind of motion called back-and-forth motion, or oscillation. "
            "A pendulum is an object on a string that swings back and forth in a very steady pattern. "
            "When you pull a pendulum to one side and let it go, gravity pulls the weight downward, "
            "and it swings to the other side. Then gravity pulls it back again!\n\n"
            "Scientists love pendulums because they are very predictable. That means you can guess "
            "exactly where the pendulum will go next. Long pendulums swing slowly, while short pendulums "
            "swing faster. Clocks have used pendulums for hundreds of years to keep accurate time. "
            "The swinging motion happens over and over in a pattern — back, forth, back, forth — "
            "until the pendulum slowly runs out of energy and stops."
        ),
        "instructions": "Read about the pendulum. Then answer the questions below.",
        "questions": [
            {
                "prompt": "What force pulls the pendulum back down when it swings to one side?",
                "response_lines": 2,
            },
            {
                "prompt": "What does 'predictable' mean? Give an example from the passage.",
                "response_lines": 2,
            },
            {
                "prompt": "How is a long pendulum different from a short pendulum?",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {
                "term": "Back-and-Forth Motion",
                "definition": "Movement that swings from one side to the other over and over.",
            },
            {
                "term": "Pendulum",
                "definition": "A weight on a string that swings back and forth in a pattern.",
            },
            {
                "term": "Predictable",
                "definition": "Something you can know will happen before it does.",
            },
        ],
    }
    ws_tue_read = WorksheetFactory.create("reading_comprehension", tue_reading_data)
    render_reading_worksheet_to_image(ws_tue_read, f"{output_dir}/03_tuesday_reading.png")
    render_reading_worksheet_to_pdf(ws_tue_read, f"{output_dir}/03_tuesday_reading.pdf")

    # Tuesday Venn Diagram: Pendulum vs. Spinning Top
    tue_venn_data = {
        "title": "Tuesday: Back-and-Forth vs. Spinning Motion",
        "instructions": "Sort each word or phrase into the correct section of the diagram.",
        "left_label": "Pendulum",
        "right_label": "Spinning Top",
        "both_label": "Both",
        "word_bank": [
            "Swings back and forth",
            "Spins in circles",
            "Gravity acts on it",
            "Moves in a pattern",
            "Used in clocks",
            "Can slow down and stop",
            "Push starts the motion",
            "Stays in one spot",
        ],
        "left_items": ["Has a string"],
        "right_items": ["Rotates around its center"],
        "both_items": ["Needs a push to start"],
    }
    ws_tue_venn = WorksheetFactory.create("venn_diagram", tue_venn_data)
    render_venn_diagram_to_image(ws_tue_venn, f"{output_dir}/04_tuesday_venn.png")
    render_venn_diagram_to_pdf(ws_tue_venn, f"{output_dir}/04_tuesday_venn.pdf")

    # =========================================================================
    # WEDNESDAY — Vibrations and Sound (Rubber Band Guitar)
    # Experiment: Rubber band guitar over empty tissue box.
    # SOL: Science 1.2
    # =========================================================================

    # Wednesday Reading: Vibrations and Sound
    wed_reading_data = {
        "title": "Wednesday: Vibrations and Sound",
        "passage_title": "Twang! How Sound Travels",
        "passage": (
            "When you pluck a rubber band stretched across an empty box, the rubber band moves "
            "so fast that it looks blurry. That fast back-and-forth movement is called a vibration. "
            "Vibrations are the secret behind every sound you have ever heard! The vibrating rubber band "
            "pushes the air around it, and those air pushes travel to your ears as sound waves.\n\n"
            "Not all vibrations sound the same. When you pluck a thick rubber band, it vibrates slowly "
            "and makes a low sound called a low pitch. A thin rubber band vibrates very fast and makes "
            "a high-pitched sound. If you pluck harder, the rubber band vibrates with more energy and the "
            "sound is louder. If you pluck gently, the vibration is smaller and the sound is softer. "
            "Every musical instrument — from guitars to drums — uses vibration to make its music!"
        ),
        "instructions": "Read about vibrations and sound. Then answer the questions below.",
        "questions": [
            {
                "prompt": "What is a vibration? Describe it in your own words.",
                "response_lines": 2,
            },
            {
                "prompt": "How does plucking a rubber band harder change the sound?",
                "response_lines": 2,
            },
            {
                "prompt": "What is the difference between a thick rubber band's sound and a thin one?",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {
                "term": "Vibration",
                "definition": "A very fast back-and-forth movement that makes sound.",
            },
            {
                "term": "Pitch",
                "definition": "How high or low a sound is.",
            },
            {
                "term": "Sound Wave",
                "definition": "The movement of energy through air that our ears detect as sound.",
            },
        ],
    }
    ws_wed_read = WorksheetFactory.create("reading_comprehension", wed_reading_data)
    render_reading_worksheet_to_image(ws_wed_read, f"{output_dir}/05_wednesday_reading.png")
    render_reading_worksheet_to_pdf(ws_wed_read, f"{output_dir}/05_wednesday_reading.pdf")

    # Wednesday Odd One Out: Vibrations and Sound
    wed_odd_data = {
        "title": "Wednesday: Vibrations — Odd One Out",
        "instructions": (
            "In each row, circle the item that does NOT belong with the others. "
            "Write why it is the odd one out."
        ),
        "rows": [
            {
                "items": ["Rubber band", "Guitar string", "Drum skin", "A rock"],
                "odd_item": "A rock",
                "explanation": "Rubber bands, guitar strings, and drum skins all vibrate to make sound. A rock does not vibrate to produce sound.",
            },
            {
                "items": ["Loud pluck", "Hard tap", "Soft whisper", "Heavy hit"],
                "odd_item": "Soft whisper",
                "explanation": "Loud pluck, hard tap, and heavy hit all create bigger vibrations and louder sounds. A soft whisper is quiet.",
            },
            {
                "items": ["High pitch", "Fast vibration", "Thin rubber band", "Slow vibration"],
                "odd_item": "Slow vibration",
                "explanation": "High pitch and thin rubber bands go with fast vibration. Slow vibration makes a low pitch instead.",
            },
            {
                "items": ["Sound wave", "Vibration", "Air movement", "Gravity"],
                "odd_item": "Gravity",
                "explanation": "Sound waves, vibrations, and air movement are all connected to how sound travels. Gravity pulls objects down and is not part of making sound.",
            },
        ],
        "reasoning_lines": 2,
        "show_answers": False,
    }
    ws_wed_odd = WorksheetFactory.create("odd_one_out", wed_odd_data)
    render_odd_one_out_to_image(ws_wed_odd, f"{output_dir}/06_wednesday_odd_one_out.png")
    render_odd_one_out_to_pdf(ws_wed_odd, f"{output_dir}/06_wednesday_odd_one_out.pdf")

    # =========================================================================
    # THURSDAY — Pushes and Pulls (Forces)
    # Experiment: Push a toy car and compare pushes of different strengths;
    #             use a magnet to pull a paper clip.
    # SOL: Science 1.2
    # =========================================================================

    # Thursday Reading: Pushes and Pulls
    thu_reading_data = {
        "title": "Thursday: Pushes and Pulls",
        "passage_title": "Forces All Around Us",
        "passage": (
            "Every time something moves, a force is at work! A force is a push or a pull. "
            "When you push a toy car forward, you are giving it a push force. The car moves in the "
            "direction you pushed it. When you push harder, the car moves faster and travels farther. "
            "When you push gently, the car moves slowly and stops sooner. Changing the strength of a "
            "push changes how an object moves.\n\n"
            "Pulls are forces too! Gravity is a pull that the Earth uses to keep everything on the ground. "
            "Magnets can pull metal objects toward them without even touching them! "
            "Forces can also stop moving objects — if you reach out and grab a rolling toy car, "
            "your hand's push force stops it. "
            "Every day, pushes and pulls work together to make the world around us move, slow down, "
            "speed up, and change direction."
        ),
        "instructions": "Read about pushes and pulls. Then answer the questions below.",
        "questions": [
            {
                "prompt": "What is a force? Give one example of a push and one example of a pull.",
                "response_lines": 2,
            },
            {
                "prompt": "What happens to a toy car when you push it harder? What about when you push it gently?",
                "response_lines": 2,
            },
            {
                "prompt": "Name two pulling forces described in the passage.",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {
                "term": "Force",
                "definition": "A push or a pull that makes objects move, speed up, slow down, or change direction.",
            },
            {
                "term": "Push",
                "definition": "A force that moves an object away from you.",
            },
            {
                "term": "Pull",
                "definition": "A force that moves an object toward you.",
            },
        ],
    }
    ws_thu_read = WorksheetFactory.create("reading_comprehension", thu_reading_data)
    render_reading_worksheet_to_image(ws_thu_read, f"{output_dir}/07_thursday_reading.png")
    render_reading_worksheet_to_pdf(ws_thu_read, f"{output_dir}/07_thursday_reading.pdf")

    # Thursday Tree Map: Types of Forces
    thu_tree_data = {
        "title": "Thursday: Pushes and Pulls — Forces Tree Map",
        "instructions": "Sort the words from the word bank into the correct branch of forces.",
        "root_label": "Forces",
        "branches": [
            {
                "label": "Push",
                "slots": [
                    {"text": "Kicking a ball"},
                    {"text": "Opening a door"},
                ],
                "slot_count": 2,
            },
            {
                "label": "Pull",
                "slots": [
                    {"text": "Gravity"},
                    {"text": "Magnet attracts metal"},
                ],
                "slot_count": 2,
            },
            {
                "label": "Effect of Force",
                "slots": [
                    {"text": "Object speeds up"},
                    {"text": "Object changes direction"},
                ],
                "slot_count": 2,
            },
        ],
        "word_bank": [
            "Kicking a ball",
            "Gravity",
            "Opening a door",
            "Magnet attracts metal",
            "Object speeds up",
            "Object changes direction",
        ],
    }
    ws_thu_tree = WorksheetFactory.create("tree_map", thu_tree_data)
    render_tree_map_to_image(ws_thu_tree, f"{output_dir}/08_thursday_tree_map.png")
    render_tree_map_to_pdf(ws_thu_tree, f"{output_dir}/08_thursday_tree_map.pdf")

    # =========================================================================
    # FRIDAY — Forces in Baseball (Baseball Theme)
    # Experiment: Toss a ball and observe what makes it go fast, slow, high, low.
    #             Use different strengths of throw to compare distances.
    # SOL: Science 1.2
    # =========================================================================

    # Friday Reading: Forces in Baseball
    fri_reading_data = {
        "title": "Friday: Forces in Baseball",
        "passage_title": "Home Run Science: Forces at the Ballpark",
        "passage": (
            "Baseball is one of the best sports for learning about forces! Every single play uses "
            "pushes and pulls. When a pitcher winds up and throws the ball, the arm gives the ball "
            "a strong push force. The harder the pitcher pushes, the faster the ball travels to home plate. "
            "If the pitcher uses less force, the ball goes slower — that is called a changeup!\n\n"
            "When the batter hits the ball with the bat, another big push force sends the ball flying "
            "through the air. The direction the bat pushes the ball decides whether it goes to left field, "
            "right field, or straight up into a pop fly. But gravity — Earth's pull — is always working too. "
            "It pulls the ball back down toward the ground no matter how hard the batter hits it. "
            "When the ball finally lands in an outfielder's glove, the glove provides a stopping force. "
            "From the first pitch to the final out, forces are at work on every play!"
        ),
        "instructions": "Read about forces in baseball. Then answer the questions below.",
        "questions": [
            {
                "prompt": "What force does the pitcher use to throw the ball? How does force strength affect speed?",
                "response_lines": 2,
            },
            {
                "prompt": "What force always pulls the baseball back down to the ground?",
                "response_lines": 2,
            },
            {
                "prompt": "How does the direction of the bat's push affect where the ball goes?",
                "response_lines": 2,
            },
        ],
        "vocabulary": [
            {
                "term": "Push Force",
                "definition": "A force that sends an object moving away, like a pitch or a hit.",
            },
            {
                "term": "Gravity",
                "definition": "Earth's pull that brings the ball back down to the ground.",
            },
            {
                "term": "Stopping Force",
                "definition": "A force that slows down or stops a moving object.",
            },
        ],
    }
    ws_fri_read = WorksheetFactory.create("reading_comprehension", fri_reading_data)
    render_reading_worksheet_to_image(ws_fri_read, f"{output_dir}/09_friday_reading.png")
    render_reading_worksheet_to_pdf(ws_fri_read, f"{output_dir}/09_friday_reading.pdf")

    # Friday Feature Matrix: Baseball Forces Classification
    fri_matrix_data = {
        "title": "Friday: Forces in Baseball — Feature Matrix",
        "instructions": (
            "Check the correct box(es) for each baseball action. "
            "Think about whether it uses a push, a pull, or changes the ball's motion."
        ),
        "items": [
            {
                "name": "Pitcher throws the ball",
                "checked_properties": ["Push", "Changes Speed"],
            },
            {
                "name": "Gravity pulls ball to ground",
                "checked_properties": ["Pull", "Changes Direction"],
            },
            {
                "name": "Batter hits a home run",
                "checked_properties": ["Push", "Changes Direction", "Changes Speed"],
            },
            {
                "name": "Catcher stops the ball",
                "checked_properties": ["Push", "Changes Speed"],
            },
            {
                "name": "Ball rolls to a stop",
                "checked_properties": ["Changes Speed"],
            },
            {
                "name": "Fielder throws to first base",
                "checked_properties": ["Push", "Changes Direction"],
            },
        ],
        "properties": ["Push", "Pull", "Changes Speed", "Changes Direction"],
        "show_answers": False,
    }
    ws_fri_matrix = WorksheetFactory.create("feature_matrix", fri_matrix_data)
    render_feature_matrix_to_image(ws_fri_matrix, f"{output_dir}/10_friday_feature_matrix.png")
    render_feature_matrix_to_pdf(ws_fri_matrix, f"{output_dir}/10_friday_feature_matrix.pdf")

    print(f"Successfully generated Motion Week series in '{output_dir}/'")
    print("10 worksheets created (5 days x 2 worksheets each):")
    print("  Mon: 01_monday_reading.pdf, 02_monday_feature_matrix.pdf")
    print("  Tue: 03_tuesday_reading.pdf, 04_tuesday_venn.pdf")
    print("  Wed: 05_wednesday_reading.pdf, 06_wednesday_odd_one_out.pdf")
    print("  Thu: 07_thursday_reading.pdf, 08_thursday_tree_map.pdf")
    print("  Fri: 09_friday_reading.pdf, 10_friday_feature_matrix.pdf")


if __name__ == "__main__":
    generate_motion_week_series()
