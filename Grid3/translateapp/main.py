import streamlit as st
import xml.etree.ElementTree as ET
from deep_translator import GoogleTranslator, MicrosoftTranslator, DeeplTranslator
import zipfile
import os
from io import BytesIO
import tempfile

def process_and_translate_xml(file, tool, source_lang, target_lang, api_key=None, debug_mode=False):
    try:
        tree = ET.parse(file)
        root = tree.getroot()

        # Log the filename for debugging
        if debug_mode:
            st.write(f"Processing file: {file}")

        # Find and translate relevant elements
        translated_count = 0
        for element in root.iter():
            if element.tag == "Parameter":
                # Skip translation for Parameter with Key="grid"
                if element.get("Key") == "grid":
                    continue
            if element.tag in ["r", "Caption", "Parameter"]:
                if element.text and element.text.strip():
                    # Debug before translation
                    original_text = element.text
                    translated_text = translate_text(original_text, tool, source_lang, target_lang, api_key)
                    element.text = translated_text
                    translated_count += 1
                    # Debug after translation
                    if debug_mode:
                        st.write(f"Translated '{original_text}' to '{translated_text}'")

        # Debug the number of elements translated
        st.write(f"Total elements translated in file: {translated_count}")

        # Save the modified XML
        translated_xml = BytesIO()
        tree.write(translated_xml, encoding="utf-8", xml_declaration=True)
        translated_xml.seek(0)
        return translated_xml
    except Exception as e:
        st.error(f"Error processing XML: {e}")
        return None

# Function to get supported languages
def get_supported_languages(tool, api_key=None):
    try:
        if tool == "Google":
            return GoogleTranslator().get_supported_languages()
        elif tool == "Microsoft":
            if not api_key:
                return []
            return MicrosoftTranslator(api_key=api_key).get_supported_languages()
        elif tool == "DeepL":
            if not api_key:
                return []
            return DeeplTranslator(api_key=api_key).get_supported_languages()
    except Exception as e:
        st.error(f"Error fetching supported languages: {e}")
        return []

# Function to translate text
def translate_text(text, tool, source_lang, target_lang, api_key=None):
    try:
        if tool == "Google":
            return GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        elif tool == "Microsoft":
            if api_key:
                translator = MicrosoftTranslator(api_key=api_key, source=source_lang, target=target_lang)
                return translator.translate(text)
        elif tool == "DeepL":
            if api_key:
                translator = DeeplTranslator(api_key=api_key, source=source_lang, target=target_lang)
                return translator.translate(text)
    except Exception as e:
        st.error(f"Translation error: {e}")
        return text

# Streamlit app
st.title("Gridset Translator")
st.markdown(
    """
    Upload a `.gridset` file, translate its text elements to another language, 
    and download the translated `.gridset` file.
    """
)

# Select translation tool
translation_tool = st.selectbox("Select Translation Tool", ["Google", "Microsoft", "DeepL"])

# API Key input for paid tools
if translation_tool in ["Microsoft", "DeepL"]:
    st.markdown("**Note:** The API key will not be cached or stored.")
    api_key = st.text_input(f"Enter your {translation_tool} API Key", type="password")
else:
    api_key = None

# Fetch supported languages dynamically
languages = get_supported_languages(translation_tool, api_key)

if languages:
    source_lang = st.selectbox("Source Language", options=languages, index=languages.index("english"))
    target_lang = st.selectbox("Target Language", options=languages, index=languages.index("spanish"))
else:
    st.error("Failed to fetch supported languages. Please check your API key or connection.")

# File upload
uploaded_file = st.file_uploader("Upload a Gridset file (.gridset)", type=["gridset"])
debug_mode = st.checkbox("Enable Debug Output", value=False)

if uploaded_file:
    # Debug the uploaded file
    st.write(f"Uploaded file: {uploaded_file.name}")

    # Use tempfile for a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Unzip the uploaded .gridset file
        try:
            with zipfile.ZipFile(uploaded_file, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
                st.write("Files successfully extracted.")
        except Exception as e:
            st.error(f"Error extracting .gridset file: {e}")
            st.stop()

        # Debug the extracted files
        extracted_files = list(os.walk(temp_dir))
        if debug_mode:
            st.write(f"Extracted files: {extracted_files}")

        # Process and translate XML files
        output_zip = BytesIO()
        with zipfile.ZipFile(output_zip, "w") as output_zip_ref:
            for root_dir, _, files in os.walk(temp_dir):
                for file_name in files:
                    file_path = os.path.join(root_dir, file_name)

                    # Debug file paths being processed
                    relative_path = os.path.relpath(file_path, temp_dir)
                    if debug_mode:
                        st.write(f"Processing file: {relative_path}")

                    if relative_path.startswith("Grids/") and file_name.endswith(".xml"):
                        try:
                            if debug_mode:
                                st.write(f"Translating: {file_name}")
                            translated_xml = process_and_translate_xml(
                                file_path, translation_tool, source_lang, target_lang, api_key,  debug_mode=debug_mode
                            )
                            if translated_xml:
                                if debug_mode:
                                    st.write(f"Successfully translated: {file_name}")
                                output_zip_ref.writestr(relative_path, translated_xml.read())
                            else:
                                st.error(f"Failed to translate: {file_name}")
                        except Exception as e:
                            st.error(f"Error translating file {file_name}: {e}")
                    else:
                        # Debug skipped files
                        if debug_mode:
                            st.write(f"Skipping file: {file_name}")
                        with open(file_path, "rb") as f:
                            output_zip_ref.writestr(relative_path, f.read())

        # Check if any files were written to the ZIP
        if output_zip.tell() == 0:
            st.error("No files were written to the output ZIP. Check your input.")
        else:
            # Provide download link for the translated .gridset
            st.success("Translation complete!")
            output_zip.seek(0)
            translated_filename = f"{os.path.splitext(uploaded_file.name)[0]}-{target_lang}.gridset"
            st.download_button(
                label="Download Translated Gridset",
                data=output_zip,
                file_name=translated_filename,
                mime="application/zip",
            )