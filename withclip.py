import keyboard
import pyautogui
import pytesseract
import pyperclip
from PIL import ImageGrab
import datetime
import os
import openai
import re

# Set your OpenAI API key
openai.api_key = "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"  # Replace with your OpenAI API key

# Set the path to Tesseract OCR (Windows users)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Update this path if needed

# Define paths for outputs
output_folder = "copy"        # General output folder
screenshot_folder = os.path.join(output_folder, "screenshots")

# Ensure directories exist
os.makedirs(screenshot_folder, exist_ok=True)

# Paths for text files
text_file_path = os.path.join(output_folder, "textphoto.txt")  # Extracted text
answer_file_path = os.path.join(output_folder, "answer.txt")   # GPT response

# Variables to store mouse coordinates
top_left = None
bottom_right = None

def clean_answer_text(extracted_text):
    """
    Clean the extracted text to remove unwanted characters like bullet points, 'O' used as bullets, and specific symbols like ©.
    """
    # Remove bullet points (•) or similar symbols
    cleaned_text = re.sub(r'^[\u2022\u2023\u2219\u2022\u25CB\u2219]*\s*', '', extracted_text)
    
    # Remove 'O' used as a bullet in front of choices (O 10, O 12, etc.)
    cleaned_text = re.sub(r'\bO\s+', '', cleaned_text)  # Remove 'O' followed by a space
    
    # Remove the © symbol and other unwanted characters
    cleaned_text = cleaned_text.replace('•', '').replace('©', '').strip()  # Remove bullet points and © symbol
    
    return cleaned_text

def get_gpt_response(prompt):
    """
    Send the extracted text to GPT and get a response tailored for multiple-choice questions.
    """
    instruction = (
    "Answer the following multiple-choice question by providing ONLY the letter(s) or number(s) "
    "corresponding to the correct answer. If there are multiple answers, separate them with commas. "
    "Do not explain. Do not respond with anything but the correct answer. If the correct answer is associated "
    "with a letter or number, ONLY provide that letter/number, or letters/numbers if there are multiple correct answers. "
    "If there is no letter/number, simply provide the correct answer. Some possible answers will be associated with a bullet "
    "if they don't have a number or letter. When you provide the answer, only provide the correct choice, without the bullet."
    )


    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": instruction},
                {"role": "user", "content": prompt},
            ],
            max_tokens=50,
            temperature=0,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {str(e)}"

def take_screenshot_and_process_text(top_left, bottom_right):
    """
    Take a screenshot based on two mouse positions (top-left and bottom-right),
    extract text, send it to GPT for processing, and save both the text and response.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    screenshot_path = os.path.join(screenshot_folder, f"screenshot_{timestamp}.png")

    # Take a screenshot of the defined bounding box
    screenshot = ImageGrab.grab(bbox=(top_left[0], top_left[1], bottom_right[0], bottom_right[1]))
    screenshot.save(screenshot_path)
    print(f"Screenshot saved to {screenshot_path}")

    # Extract text using Tesseract OCR
    extracted_text = pytesseract.image_to_string(screenshot)
    print("Extracted Text:")
    print(extracted_text)

    # Clean the extracted text to remove unwanted characters
    cleaned_text = clean_answer_text(extracted_text)

    # Save the extracted text to textphoto.txt
    with open(text_file_path, "w") as text_file:
        text_file.write(f"Extracted Text:\n{cleaned_text}\n")
    print(f"Extracted text written to {text_file_path}")

    # Send the cleaned text to GPT
    if cleaned_text.strip():
        gpt_response = get_gpt_response(cleaned_text)
        print("GPT Response:")
        print(gpt_response)

        # Overwrite answer.txt with only the latest GPT response
        with open(answer_file_path, "w") as answer_file:
            answer_file.write(f"{gpt_response}\n")  # Write only the latest answer
        print(f"GPT response written to {answer_file_path}")
    else:
        print("No text was extracted from the screenshot.")

def copy_answer_to_clipboard():
    """
    Copy the content of answer.txt to the clipboard.
    """
    try:
        with open(answer_file_path, "r") as answer_file:
            answer_content = answer_file.read().strip()
            pyperclip.copy(answer_content)
            print("Answer copied to clipboard!")
    except FileNotFoundError:
        print("Answer file not found. Ensure that a response is generated first.")

def main():
    global top_left, bottom_right

    print("Move your mouse to the top-left corner and press '0'. Then move your mouse to the bottom-right corner and press '9' to take a screenshot.")
    print("Press 'F5' to copy the GPT response to the clipboard.")
    print("Press 'Esc' to exit.")

    while True:
        # Wait for a key event
        event = keyboard.read_event()

        if event.event_type == "down":
            if event.name == "0":  # Mark top-left corner with '0'
                top_left = pyautogui.position()
                print(f"Top-left corner set to: {top_left}")

            elif event.name == "9":  # Mark bottom-right corner with '9'
                bottom_right = pyautogui.position()
                print(f"Bottom-right corner set to: {bottom_right}")

                # Ensure both points are selected before taking a screenshot
                if top_left and bottom_right:
                    print("Taking screenshot based on selected coordinates...")
                    take_screenshot_and_process_text(top_left, bottom_right)
                else:
                    print("Both top-left and bottom-right points must be selected first.")

            elif event.name == "num lock":  # Copy GPT response to clipboard
                copy_answer_to_clipboard()

            elif event.name == "esc":  # Exit program on 'Esc'
                print("Exiting the program.")
                break

if __name__ == "__main__":
    main()
